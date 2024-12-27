from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Optional
import logging
import json
from dotenv import load_dotenv
import os

# Logger konfigurieren
logger = logging.getLogger(__name__)

# Lade .env Datei
load_dotenv()

# API Key Prüfung
if not os.getenv("LLM_API_KEY"):
    logger.error("LLM_API_KEY nicht in .env Datei gefunden")
    raise ValueError("LLM_API_KEY muss in der .env Datei gesetzt sein")

class Settings(BaseSettings):
    """Zentrale Konfigurationsklasse für die Anwendung"""
    
    # Basis-Konfiguration
    APP_NAME: str = "VoiceToDoc"
    DEBUG: bool = False
    
    # Basis-Pfad
    BASE_DIR: Path = Path("/app")
    
    # Abgeleitete Pfade
    DATA_DIR: Path = BASE_DIR / "data"
    TEMP_DIR: Path = DATA_DIR / "temp"
    LOG_DIR: Path = DATA_DIR / "logs"
    TEMPLATE_DIR: Path = DATA_DIR / "templates"
    CONFIG_FILE: Path = DATA_DIR / "config.json"
    
    # Logging
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://192.168.178.67:3000",
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
    
    # LLM API
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_MODEL: str = "gpt-4o"  # Für komplexe Aufgaben
    LLM_MODEL_LIGHT: str = "gpt-4o-mini"  # Für einfache Textformatierung
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000
    
    # Storage-Konfiguration
    STORAGE_TYPE: str = "sql"  # oder "filesystem"
    
    # Datenbank-Einstellungen
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # "sqlite", "postgresql", "mysql"
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "templates_db")
    
    # SQLite spezifische Einstellungen
    DB_PATH: str = os.getenv("DB_PATH", "data/templates.db")
    
    # Connection Pool Settings (nicht für SQLite)
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # Debug-Einstellungen
    SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        """Generiert die Datenbank-URL basierend auf der Konfiguration"""
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_PATH}"
        elif self.DB_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        elif self.DB_TYPE == "mysql":
            return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Nicht unterstützter Datenbanktyp: {self.DB_TYPE}")
    
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

def ensure_directory_permissions(directory: Path):
    """Stellt sicher, dass das Verzeichnis existiert und beschreibbar ist"""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        # Setze Berechtigungen (755 für Verzeichnisse)
        directory.chmod(0o755)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen/Setzen der Berechtigungen für {directory}: {e}")
        raise

# Erstelle notwendige Verzeichnisse mit korrekten Berechtigungen
for directory in [settings.DATA_DIR, settings.TEMP_DIR, settings.LOG_DIR, settings.TEMPLATE_DIR]:
    ensure_directory_permissions(directory) 
