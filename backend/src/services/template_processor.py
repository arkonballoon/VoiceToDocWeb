import re
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
    def process_template(self, template: str, transcription: str) -> Dict[str, Any]:
        """Verarbeitet ein Template mit der gegebenen Transkription"""
        try:
            # Informationen aus der Transkription extrahieren
            extracted_info = self._extract_information(template, transcription)
            
            # Template mit extrahierten Informationen füllen
            filled_template = self._fill_template(template, extracted_info, transcription)
            
            # Ergebnis validieren
            validation_result = self._validate_result(
                template,
                transcription,
                extracted_info,
                filled_template
            )
            
            # JSON-String in Dict umwandeln
            validation_dict = json.loads(validation_result)
            
            return {
                "processed_text": filled_template,
                "extracted_info": extracted_info,
                "validation_result": validation_dict,
                "metadata": {
                    "model": settings.LLM_MODEL,
                    "total_tokens": 0,  # TODO: Aus Response extrahieren
                    "response_id": "test-id"  # TODO: Eindeutige ID generieren
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler bei der Template-Verarbeitung: {str(e)}")
            raise
    
    def _extract_information(self, template: str, transcription: str) -> Dict[str, str]:
        """Extrahiert benötigte Informationen aus der Transkription"""
        response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
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
                model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": """
                    Fülle das Template mit den extrahierten Informationen aus.
                    Verwende die gegebenen Informationen.
                    Verwende dabei die Struktur des Templates ab ##Struktur. Ersetze den Text in den einzelnen Abschnitten durch einen Text der der Beschreibung des Abschnitts entspricht inkl. Beschreibung: und die extrahierten Informationen enthält.
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
    
    def _validate_result(
        self, 
        template: str, 
        transcription: str, 
        extracted_info: Dict[str, str],
        filled_template: str
    ) -> Dict[str, any]:
        """Validiert das ausgefüllte Template"""
        response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
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