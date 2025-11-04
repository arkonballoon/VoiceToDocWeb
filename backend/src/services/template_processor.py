import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from utils.logger import get_logger, log_function_call
import backoff
from openai import AsyncOpenAI
import logging
import json
from config import settings
from fastapi import WebSocket
import asyncio
from datetime import datetime
from utils.singleton import Singleton

logger = get_logger(__name__)

class TemplateProcessingResult(BaseModel):
    """Ergebnis der Template-Verarbeitung"""
    class Config:
        arbitrary_types_allowed = True
    
    extracted_info: Dict[str, str]
    filled_template: str
    validation_result: Optional[Dict[str, Any]] = None
    needs_revision: bool = False
    revision_comments: Optional[str] = None

class TemplateProcessor(Singleton):
    def _init(self):
        """Initialisierung des TemplateProcessors"""
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.active_connections = {}
        logger.info(f"TemplateProcessor initialisiert mit API-Key: {self.api_key[:10]}...")
        logger.info(f"Verwende LLM-Modell: {self.model}")
    
    async def register_connection(self, process_id: str, websocket: WebSocket):
        """Registriert eine neue WebSocket-Verbindung für Updates"""
        self.active_connections[process_id] = websocket
        
    async def remove_connection(self, process_id: str):
        """Entfernt eine WebSocket-Verbindung"""
        if process_id in self.active_connections:
            del self.active_connections[process_id]
    
    async def send_update(self, process_id: str, status: str, progress: float, message: str):
        """Sendet ein Update über WebSocket"""
        if process_id in self.active_connections:
            try:
                websocket = self.active_connections[process_id]
                update = {
                    "type": "template_update",
                    "status": status,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_json(update)
                logger.debug(f"Update gesendet: {update}")
                
            except Exception as e:
                logger.error(f"Fehler beim Senden des Updates: {str(e)}")
                await self.remove_connection(process_id)
    
    async def process_template_with_updates(
        self, 
        template: str, 
        transcription: str,
        process_id: str
    ) -> Dict[str, Any]:
        """Verarbeitet ein Template mit der gegebenen Transkription und sendet Updates"""
        try:
            logger.info(f"Starte Template-Verarbeitung für {process_id}")
            await self.send_update(
                process_id, 
                "started", 
                0.0, 
                "Starte Verarbeitung der Vorlage..."
            )
            
            # Informationen extrahieren
            logger.info(f"Extrahiere Informationen für {process_id}")
            await self.send_update(
                process_id,
                "extracting",
                0.25,
                "Extrahiere Informationen aus der Transkription..."
            )
            extracted_info = await self._extract_information(template, transcription)
            
            # Template füllen
            logger.info(f"Fülle Template für {process_id}")
            await self.send_update(
                process_id,
                "filling",
                0.50,
                "Verarbeite Template mit extrahierten Informationen..."
            )
            filled_template = await self._fill_template(template, extracted_info, transcription)
            
            # Validierung
            logger.info(f"Validiere Ergebnis für {process_id}")
            await self.send_update(
                process_id,
                "validating",
                0.75,
                "Validiere das ausgefüllte Template..."
            )
            validation_result = await self._validate_result(
                template, transcription, extracted_info, filled_template
            )
            
            result = {
                "processed_text": filled_template,
                "extracted_info": extracted_info,
                "validation_result": json.loads(validation_result),
                "metadata": {
                    "model": settings.LLM_MODEL,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await self.send_update(
                process_id, 
                "completed", 
                1.0, 
                "Verarbeitung erfolgreich abgeschlossen"
            )
            logger.info(f"Template-Verarbeitung für {process_id} abgeschlossen")
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Template-Verarbeitung {process_id}: {str(e)}")
            await self.send_update(
                process_id, 
                "error", 
                1.0, 
                f"Fehler bei der Verarbeitung: {str(e)}"
            )
            raise
        finally:
            # Verbindung entfernen
            await self.remove_connection(process_id)
    
    async def process_template(self, template: str, transcription: str) -> Dict[str, Any]:
        """Verarbeitet ein Template mit der gegebenen Transkription"""
        try:
            # Parallele Verarbeitung mit Timeout
            tasks = [
                asyncio.create_task(self._extract_information(template, transcription)),
                asyncio.create_task(self._fill_template(template, {}, transcription)),
            ]
            
            # Warte maximal 60 Sekunden auf alle Tasks
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=60.0)
            extracted_info, filled_template = results

            # Validierung separat durchführen
            validation_result = await self._validate_result(
                template,
                transcription,
                extracted_info,
                filled_template
            )

            return {
                "processed_text": filled_template,
                "extracted_info": extracted_info,
                "validation_result": json.loads(validation_result),
                "metadata": {
                    "model": settings.LLM_MODEL,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except asyncio.TimeoutError:
            logger.error("Timeout bei der Template-Verarbeitung")
            raise TimeoutError("Die Verarbeitung hat zu lange gedauert")
            
        except Exception as e:
            logger.error(f"Fehler bei der Template-Verarbeitung: {str(e)}")
            raise
    
    async def _extract_information(self, template: str, transcription: str) -> Dict[str, Any]:
        """Extrahiert Informationen aus der Transkription"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": """
                            Extrahiere die im Template-Header unter "## Benötigte Informationen" 
                            markierten Informationen aus der Transkription. 
                            Gib nur die gefundenen Informationen als JSON zurück.
                            Format: {"field_name": "extracted_value"}
                            Wenn eine Information nicht gefunden werden kann, verwende einen leeren String "".
                            Bei Listen gebe die Werte als kommagetrennte Zeichenkette zurück.
                        """},
                        {"role": "user", "content": f"Template:\n{template}\n\nTranskription:\n{transcription}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.3
                ),
                timeout=30.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Fehler bei der Informationsextraktion: {str(e)}")
            return {}
    
    async def _fill_template(
        self, 
        template: str, 
        extracted_info: Dict[str, str],
        additional_context: Optional[str] = None
    ) -> str:
        """Füllt das Template mit den extrahierten Informationen"""
        context = f"Additional Context:\n{additional_context}\n\n" if additional_context else ""
        
        response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": """
                    Fülle das Template mit den extrahierten Informationen aus.
                    Verwende die gegebenen Informationen.
                    Verwende dabei die Struktur des Templates ab ##Struktur. 
                    Ersetze den Text "Beschreibung: ..." in den einzelnen Abschnitten durch einen vollständigen Text, 
                    der die Beschreibung des Abschnitts umsetzt und die extrahierten Informationen enthält.
                    Die Überschriften (###) und Struktur müssen beibehalten werden.
                    Formatiere den Text professionell und lesbar.
                """},
                {"role": "user", "content": f"""
                    Template:\n{template}\n\n
                    Extrahierte Informationen:\n{extracted_info}\n\n
                    {context}
                """}
            ]
        )
        content = response.choices[0].message.content
        # Entferne "Beschreibung: " am Zeilenanfang
        cleaned_content = re.sub(r'(?m)^Beschreibung:\s*', '', content)
        return cleaned_content
    
    async def _validate_result(
        self, 
        template: str, 
        transcription: str, 
        extracted_info: Dict[str, str],
        filled_template: str
    ) -> Dict[str, any]:
        """Validiert das ausgefüllte Template"""
        response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": """
                    Überprüfe das ausgefüllte Template auf:
                    1. Vollständigkeit der benötigten Informationen
                    2. Korrekte Verwendung der extrahierten Informationen
                    3. Einhaltung der Template-Struktur
                    4. Konsistenz mit der Original-Transkription
                    
                   Gib das Ergebnis als JSON zurück mit exakt dieser Struktur:
                    {
                        "is_valid": boolean,
                        "needs_revision": boolean,
                        "revision_comments": string,
                        "validation_details": {
                            "completeness_score": float,
                            "structure_score": float,
                            "consistency_score": float,
                            "missing_fields": string[],
                            "structure_issues": string[],
                            "consistency_issues": string[]
                        },
                        "improvement_suggestions": {
                            "general_feedback": string,
                            "specific_suggestions": string[]
                        }
                    }
                     Wichtig: 
                     - Alle numerischen Werte müssen zwischen 0.0 und 1.0 liegen
                     - Arrays können leer sein, aber müssen immer als Array existieren
                     - Gebe konkrete, actionable Verbesserungsvorschläge
                     - Das general_feedback sollte eine Zusammenfassung der wichtigsten Punkte sein
                     - specific_suggestions sollte spezifische, umsetzbare Vorschläge enthalten
                     - Antworte in Deutsch
                """},
                {"role": "user", "content": f"""
                    Original Template:\n{template}\n\n
                    Transkription:\n{transcription}\n\n
                    Extrahierte Informationen:\n{extracted_info}\n\n
                    Ausgefülltes Template:\n{filled_template}
                """}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content 
