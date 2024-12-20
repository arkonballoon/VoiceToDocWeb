from faster_whisper import WhisperModel
from pathlib import Path
import numpy as np
from typing import Optional, List, Tuple
from utils.logger import get_logger
import torch
from config import settings

logger = get_logger(__name__)

class Transcriber:
    def __init__(self, model_size: str = None):
        """Initialisiert das Whisper-Modell."""
        self.model = None
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

    def transcribe_audio(
        self, 
        audio_path: Path, 
        previous_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Transkribiert eine Audiodatei.
        
        Args:
            audio_path: Pfad zur WAV-Datei
            previous_text: Vorheriger Transkriptionstext für Kontext
            
        Returns:
            Tuple aus transkribiertem Text und Konfidenz
        """
        try:
            # Transkription mit Whisper durchführen
            segments, info = self.model.transcribe(
                str(audio_path),
                language="de",
                initial_prompt=previous_text,
                word_timestamps=True
            )
            
            # Segmente zu Text zusammenfügen
            text = " ".join([segment.text for segment in segments])
            
            # Durchschnittliche Konfidenz berechnen
            confidence = np.mean([segment.avg_logprob for segment in segments]) if segments else 0.0
            
            logger.info(f"Transkription erfolgreich: {len(text)} Zeichen")
            return text.strip(), confidence
            
        except Exception as e:
            logger.error(f"Fehler bei der Transkription: {str(e)}")
            raise

    def transcribe_chunk(
        self, 
        audio_chunk: bytes, 
        previous_text: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Transkribiert einen Audio-Chunk aus dem WebSocket-Stream.
        
        Args:
            audio_chunk: Audio-Bytes im WAV-Format
            previous_text: Vorheriger Transkriptionstext für Kontext
            
        Returns:
            Tuple aus transkribiertem Text und Konfidenz
        """
        try:
            # Temporäre Datei für den Chunk erstellen
            temp_path = Path("temp") / f"chunk_{id(audio_chunk)}.wav"
            
            # Chunk in temporäre Datei schreiben
            with open(temp_path, "wb") as f:
                f.write(audio_chunk)
            
            # Transkription durchführen
            text, confidence = self.transcribe_audio(temp_path, previous_text)
            
            # Temporäre Datei löschen
            temp_path.unlink()
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"Fehler bei der Chunk-Transkription: {str(e)}")
            raise 

# Globale Transcriber-Instanz
transcriber_instance = Transcriber()