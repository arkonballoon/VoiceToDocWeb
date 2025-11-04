from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger
from utils.singleton import Singleton
from config import settings
from .models import Base

logger = get_logger(__name__)

class DatabaseConnection(Singleton):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # URL-Schema für verschiedene Datenbanken
            url_map = {
                'sqlite': 'sqlite+aiosqlite:///{}',
                'postgresql': 'postgresql+asyncpg://{}:{}@{}:{}/{}',
                'mysql': 'mysql+aiomysql://{}:{}@{}:{}/{}',
                'mssql': 'mssql+pyodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'
            }
            
            if settings.DB_TYPE == 'sqlite':
                self.db_url = url_map['sqlite'].format(settings.DB_PATH)
            else:
                self.db_url = url_map[settings.DB_TYPE].format(
                    settings.DB_USER,
                    settings.DB_PASSWORD,
                    settings.DB_HOST,
                    settings.DB_PORT,
                    settings.DB_NAME
                )
            
            # Engine erstellen
            self.engine = create_async_engine(
                self.db_url,
                echo=settings.SQL_DEBUG,
                pool_size=None if settings.DB_TYPE == 'sqlite' else settings.DB_POOL_SIZE,
                max_overflow=None if settings.DB_TYPE == 'sqlite' else settings.DB_MAX_OVERFLOW
            )
            
            # Session Factory erstellen
            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info(f"Datenbankverbindung initialisiert: {settings.DB_TYPE}")
            self._initialized = True
    
    async def initialize_database(self):
        """Erstellt alle Tabellen"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def get_session(self) -> AsyncSession:
        """Gibt eine neue Datenbank-Session zurück"""
        async with self.async_session() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Datenbank-Fehler: {str(e)}")
                raise
            finally:
                await session.close() 
