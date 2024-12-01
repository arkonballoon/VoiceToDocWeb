from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import logging
import json

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
    CONFIG_FILE: Path = DATA_DIR / "config.json"
    
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
    WHISPER_DEVICE_CUDA: str = "large-v3"
    MAX_WORKERS: int = 3
    
    def save_to_file(self):
        """Speichert die aktuelle Konfiguration in eine JSON-Datei"""
        config_dict = self.model_dump()
        # Konvertiere Path-Objekte zu Strings
        for key, value in config_dict.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
        
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    def load_from_file(self) -> bool:
        """Lädt die Konfiguration aus einer JSON-Datei"""
        if not self.CONFIG_FILE.exists():
            return False
            
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Konvertiere String-Pfade zurück zu Path-Objekten
            for key, value in config_dict.items():
                if key.endswith('_DIR') or key.endswith('_FILE'):
                    config_dict[key] = Path(value)
            
            # Aktualisiere die Einstellungen
            for key, value in config_dict.items():
                setattr(self, key, value)
            return True
            
        except Exception as e:
            logging.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
# Globale Konfigurationsinstanz
settings = Settings()

# Erstelle notwendige Verzeichnisse
for directory in [settings.DATA_DIR, settings.TEMP_DIR, settings.LOG_DIR, settings.TEMPLATE_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 