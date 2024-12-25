from faster_whisper import WhisperModel
from pathlib import Path
import numpy as np
from typing import Optional, List, Tuple
from utils.logger import get_logger
import torch
from config import settings
from openai import OpenAI

logger = get_logger(__name__)

class Transcriber:
    def __init__(self, model_size: str = None, api_key: str = None):
        """Initialisiert das Whisper-Modell und OpenAI Client."""
        self.model = None
        self.client = OpenAI(api_key=api_key or settings.LLM_API_KEY)
        self.load_model(model_size)
    
    def load_model(self, model_size: str = None):
        """Lädt das Whisper-Modell mit den angegebenen Parametern."""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            if model_size is None:
                model_size = settings.WHISPER_DEVICE_CUDA if device == "cuda" else settings.WHISPER_MODEL
            
            logger.info(f"Lade Whisper-Modell: {model_size} auf {device}")
            
            self.model = WhisperModel(
                model_size, 
                device=device, 
                compute_type=compute_type
            )
            logger.info(f"Whisper-Modell '{model_size}' erfolgreich geladen")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden des Whisper-Modells: {str(e)}")
            raise
    
    def reload_model(self):
        """Lädt das Modell mit aktuellen Konfigurationseinstellungen neu."""
        logger.info("Lade Whisper-Modell neu...")
        if self.model:
            # Cleanup des alten Modells
            del self.model
            torch.cuda.empty_cache()  # GPU-Speicher freigeben
        
        self.load_model()

    def post_process_transcription(self, raw_text: str) -> str:
        """
        Verarbeitet die Rohtranskription mit einem leichtgewichtigen LLM für bessere Lesbarkeit.
        """
        try:
            # Timeout hinzufügen
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL_LIGHT,
                messages=[
                    {"role": "system", "content": """
                        Formatiere den Text für bessere Lesbarkeit:
                        1. Teile den Text in logische Absätze
                        2. Füge Satzzeichen korrekt ein
                        3. Markiere Sprecherwechsel wenn erkennbar
                        4. Behalte den ursprünglichen Inhalt bei
                        
                        Wichtig:
                        - Keine inhaltlichen Änderungen
                        - Keine Interpretationen
                        - Nur einfache Formatierung mit <p> Tags
                    """},
                    {"role": "user", "content": f"Hier ist die Rohtranskription:\n\n{raw_text}"}
                ],
                temperature=0.3,
                timeout=30.0  # 30 Sekunden Timeout
            )
            
            if not response or not response.choices:
                logger.error("Keine Antwort vom LLM erhalten")
                return raw_text
            
            processed_text = response.choices[0].message.content
            logger.info(f"Transkription erfolgreich formatiert: {len(processed_text)} Zeichen")
            return processed_text
            
        except Exception as e:
            logger.error(f"Fehler bei der Textformatierung: {str(e)}")
            # Bei Timeout oder anderen Fehlern den Originaltext zurückgeben
            return raw_text

    def transcribe_audio(
        self, 
        audio_path: Path, 
        previous_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Transkribiert eine Audiodatei und formatiert den Text für den Quill-Editor.
        """
        try:
            # Transkription mit Whisper durchführen
            segments, info = self.model.transcribe(
                str(audio_path),
                language="de",
                initial_prompt=previous_text,
                word_timestamps=True
            )
            
            # Rohen Text sammeln
            raw_text = " ".join([segment.text.strip() for segment in segments])
            
            # Text nachbearbeiten
            processed_text = self.post_process_transcription(raw_text)
            
            # Konfidenz berechnen
            confidence = np.mean([segment.avg_logprob for segment in segments]) if segments else 0.0
            
            logger.info(f"Transkription erfolgreich: {len(processed_text)} Zeichen")
            return processed_text, confidence
            
        except Exception as e:
            logger.error(f"Fehler bei der Transkription: {str(e)}")
            raise

    def transcribe_chunk(
        self, 
        audio_chunk: bytes, 
        previous_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Für Chunks keine Nachbearbeitung, da der Text noch unvollständig ist.
        """
        try:
            temp_path = Path("temp") / f"chunk_{id(audio_chunk)}.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_chunk)
            
            segments, info = self.model.transcribe(
                str(temp_path),
                language="de",
                initial_prompt=previous_text,
                word_timestamps=True
            )
            
            # Für Chunks einfache Formatierung
            text = " ".join([segment.text.strip() for segment in segments])
            confidence = np.mean([segment.avg_logprob for segment in segments]) if segments else 0.0
            
            temp_path.unlink()
            return text, confidence
            
        except Exception as e:
            logger.error(f"Fehler bei der Chunk-Transkription: {str(e)}")
            raise

# Globale Transcriber-Instanz
transcriber_instance = Transcriber()