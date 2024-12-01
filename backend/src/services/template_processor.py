from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from utils.logger import get_logger
import backoff
from openai import OpenAI
import logging
import json
from config import settings

logger = logging.getLogger(__name__)

class TemplateProcessingResult(BaseModel):
    """Ergebnis der Template-Verarbeitung"""
    class Config:
        arbitrary_types_allowed = True
    
    extracted_info: Dict[str, str]
    filled_template: str
    validation_result: Optional[Dict[str, Any]] = None
    needs_revision: bool = False
    revision_comments: Optional[str] = None

class TemplateProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API-Key ist erforderlich")
        self.client = OpenAI(api_key=api_key)
        logger.info("TemplateProcessor initialisiert mit API-Key: %s...", api_key[:8])
        logger.info("Verwende LLM-Modell: %s", settings.LLM_MODEL)
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        jitter=None
    )
    def process_template(self, template_content: str, transcription: str) -> dict:
        """
        Verarbeitet ein Template mit der gegebenen Transkription.
        """
        try:
            if not self.client.api_key:
                raise ValueError("Kein API-Key konfiguriert")

            # Log der Eingabedaten
            logger.debug("Starte Template-Verarbeitung mit Modell %s:", settings.LLM_MODEL)
            logger.debug("Template-Content (gekürzt): %s...", template_content[:200])
            logger.debug("Transkription (gekürzt): %s...", transcription[:200])

            # Erstelle Request-Payload für besseres Logging
            messages = [
                {"role": "system", "content": template_content},
                {"role": "user", "content": transcription}
            ]
            logger.debug("OpenAI Request-Payload: %s", json.dumps(messages, indent=2, ensure_ascii=False))

            # API-Aufruf mit Logging
            logger.info("Sende Anfrage an OpenAI API (Modell: %s)", settings.LLM_MODEL)
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            
            # Log der Antwort
            logger.debug("OpenAI Antwort erhalten:")
            logger.debug("Response-ID: %s", response.id)
            logger.debug("Modell: %s", response.model)
            logger.debug("Verwendete Tokens: %d", response.usage.total_tokens)
            logger.debug("Antwort-Content: %s", response.choices[0].message.content)
            
            result = {
                "processed_text": response.choices[0].message.content,
                "status": "success",
                "metadata": {
                    "model": response.model,
                    "total_tokens": response.usage.total_tokens,
                    "response_id": response.id
                }
            }
            
            logger.info("Template-Verarbeitung erfolgreich abgeschlossen")
            logger.debug("Rückgabe-Ergebnis: %s", json.dumps(result, indent=2, ensure_ascii=False))
            
            return result
            
        except Exception as e:
            logger.error("Fehler bei der Template-Verarbeitung: %s", str(e), exc_info=True)
            logger.error("Template-Content (gekürzt): %s...", template_content[:100])
            logger.error("Transkription (gekürzt): %s...", transcription[:100])
            raise
    
    def _extract_information(self, template: str, transcription: str) -> Dict[str, str]:
        """Extrahiert benötigte Informationen aus der Transkription"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """
                    Extrahiere die im Template-Header als benötigt markierten Informationen 
                    aus der Transkription. Gib nur die gefundenen Informationen als JSON zurück.
                    Format: {"field_name": "extracted_value"}
                """},
                {"role": "user", "content": f"Template:\n{template}\n\nTranskription:\n{transcription}"}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    
    def _fill_template(
        self, 
        template: str, 
        extracted_info: Dict[str, str],
        additional_context: Optional[str] = None
    ) -> str:
        """Füllt das Template mit den extrahierten Informationen"""
        context = f"Additional Context:\n{additional_context}\n\n" if additional_context else ""
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """
                    Fülle das Template mit den extrahierten Informationen aus.
                    Verwende nur die gegebenen Informationen und erfinde keine zusätzlichen Details.
                    Behalte den Stil und die Struktur des Templates bei.
                """},
                {"role": "user", "content": f"""
                    Template:\n{template}\n\n
                    Extrahierte Informationen:\n{extracted_info}\n\n
                    {context}
                """}
            ]
        )
        return response.choices[0].message.content
    
    def _validate_result(
        self, 
        template: str, 
        transcription: str, 
        extracted_info: Dict[str, str],
        filled_template: str
    ) -> Dict[str, any]:
        """Validiert das ausgefüllte Template"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """
                    Überprüfe das ausgefüllte Template auf:
                    1. Vollständigkeit der benötigten Informationen
                    2. Korrekte Verwendung der extrahierten Informationen
                    3. Einhaltung der Template-Struktur
                    4. Konsistenz mit der Original-Transkription
                    
                    Gib das Ergebnis als JSON zurück mit:
                    {
                        "is_valid": bool,
                        "needs_revision": bool,
                        "revision_comments": string,
                        "validation_details": object
                    }
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