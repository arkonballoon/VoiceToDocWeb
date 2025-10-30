from pathlib import Path
from typing import List, Optional
import logging
import json
import os
import importlib

# Laufzeitimport für optionale Abhängigkeiten, um Linter-Fehler zu vermeiden
try:
    BaseSettings = importlib.import_module("pydantic_settings").BaseSettings  # type: ignore[attr-defined]
except Exception:
    try:
        BaseSettings = importlib.import_module("pydantic").BaseSettings  # type: ignore[attr-defined]
    except Exception:
        class BaseSettings:  # Fallback für Entwicklungsumgebungen ohne Paket
            pass

try:
    load_dotenv = importlib.import_module("dotenv").load_dotenv  # type: ignore[attr-defined]
except Exception:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False

# Logger konfigurieren
logger = logging.getLogger(__name__)

# .env aus dem Backend-Verzeichnis laden (falls vorhanden)
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f".env geladen: {env_path}")
else:
    # Fallback: Standardauflösung (falls global gesetzt)
    load_dotenv()
    logger.info(".env nicht gefunden, verwende Prozess-ENV")

# API-Key optional: Warnung statt Abbruch
if not os.getenv("LLM_API_KEY"):
    logger.warning(
        "LLM_API_KEY fehlt; LLM-Funktionen sind deaktiviert, bis der Key gesetzt ist."
    )

class Settings(BaseSettings):
    """Zentrale Konfigurationsklasse für die Anwendung"""
    
    # Basis-Konfiguration
    APP_NAME: str = "VoiceToDoc"
    DEBUG: bool = False
    
    # Basis-Pfad (dynamisch, per ENV überschreibbar)
    # Standard: Projekt-Backend-Root (…/backend)
    BASE_DIR: Path = Path(os.getenv("BASE_DIR", Path(__file__).resolve().parents[1]))
    
    # Abgeleitete Pfade
    # Standard-Datenordner innerhalb des Repos (…/backend/src/data)
    DATA_DIR: Path = BASE_DIR / "src" / "data"
    TEMP_DIR: Path = DATA_DIR / "temp"
    LOG_DIR: Path = DATA_DIR / "logs"
    TEMPLATE_DIR: Path = DATA_DIR / "templates"
    CONFIG_FILE: Path = DATA_DIR / "config.json"
    
    # Logging
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    
    # CORS (Default-Entwicklungs-Origins; ENV kann überschreiben)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://frontend:3000"  # Docker internal network
    ]
    
    # Dynamische CORS-Origins aus Umgebungsvariablen
    @property
    def dynamic_allowed_origins(self) -> List[str]:
        """Lädt CORS-Origins aus Umgebungsvariablen"""
        env_origins = os.getenv("ALLOWED_ORIGINS", "")
        if env_origins:
            try:
                # Unterstützt sowohl Komma-getrennte als auch JSON-Format
                if env_origins.startswith("["):
                    import json
                    return json.loads(env_origins)
                else:
                    return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
            except Exception as e:
                logger.warning(f"Fehler beim Parsen der ALLOWED_ORIGINS: {e}")
        
        return self.ALLOWED_ORIGINS
    
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
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
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
        # Stelle sicher, dass das Zielverzeichnis existiert
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
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
