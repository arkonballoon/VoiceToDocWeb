from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import logging

class Settings(BaseSettings):
    """Zentrale Konfigurationsklasse für die Anwendung"""
    
    # Basis-Konfiguration
    APP_NAME: str = "VoiceToDoc"
    DEBUG: bool = False
    
    # Pfade
    DATA_DIR: Path = Path("data")
    TEMP_DIR: Path = Path("temp")
    LOG_DIR: Path = Path("logs")
    TEMPLATE_DIR: Path = DATA_DIR / "templates"
    
    # Logging
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://192.168.178.67:3000",
        "http://192.168.178.67:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Audio-Verarbeitung
    AUDIO_MIN_SILENCE_LEN: int = 500
    AUDIO_SILENCE_THRESH: int = -32
    AUDIO_MIN_CHUNK_LENGTH: int = 2000
    AUDIO_MAX_CHUNK_LENGTH: int = 5000
    
    # Transcription
    WHISPER_MODEL: str = "base"
    MAX_WORKERS: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
# Globale Konfigurationsinstanz
settings = Settings()

# Erstelle notwendige Verzeichnisse
for directory in [settings.DATA_DIR, settings.TEMP_DIR, settings.LOG_DIR, settings.TEMPLATE_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 