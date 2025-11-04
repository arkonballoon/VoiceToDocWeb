from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from .storage_adapter import StorageAdapter
from utils.logger import get_logger, log_function_call

logger = get_logger(__name__)

class SQLAdapter(StorageAdapter):
    def __init__(self, connection_string: str):
        if not connection_string:
            raise ValueError("connection_string darf nicht leer sein")
            
        self.engine = create_async_engine(connection_string)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self._initialized = False
        logger.info(f"SQLAdapter initialisiert mit Connection-String: {connection_string[:50]}...")
        
    async def _ensure_initialized(self):
        """Stellt sicher, dass die Datenbank initialisiert ist"""
        if not self._initialized:
            await self.initialize_database()
            self._initialized = True
        
    async def initialize_database(self):
        """Initialisiert die Datenbank-Tabellen"""
        try:
            from database.models import Base
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Datenbank-Tabellen erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler bei der Datenbank-Initialisierung: {str(e)}")
            raise
    
    @log_function_call
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Dict[str, Any]:
        await self._ensure_initialized()
        from database.models import Template
        template_id = str(uuid.uuid4())
        now = datetime.now()
        
        try:
            async with self.async_session() as session:
                template = Template(
                    id=template_id,
                    name=name,
                    content=content,
                    description=description,
                    created_at=now,
                    updated_at=now
                )
                session.add(template)
                await session.commit()
                await session.refresh(template)
                logger.info(f"Template {template_id} erfolgreich gespeichert: {name}")
                return self._to_dict(template)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Templates: {str(e)}")
            raise
    
    @log_function_call
    async def get_templates(self) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        from database.models import Template
        try:
            async with self.async_session() as session:
                result = await session.execute(select(Template))
                templates = result.scalars().all()
                logger.debug(f"{len(templates)} Templates aus Datenbank geladen")
                return [self._to_dict(t) for t in templates]
        except Exception as e:
            logger.error(f"Fehler beim Laden der Templates: {str(e)}")
            return []
    
    @log_function_call
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        await self._ensure_initialized()
        from database.models import Template
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(Template).where(Template.id == template_id)
                )
                template = result.scalar_one_or_none()
                return self._to_dict(template) if template else None
        except Exception as e:
            logger.error(f"Fehler beim Laden des Templates {template_id}: {str(e)}")
            return None
    
    @log_function_call
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_initialized()
        from database.models import Template
        try:
            async with self.async_session() as session:
                template = await session.get(Template, template_id)
                if not template:
                    raise ValueError(f"Template {template_id} nicht gefunden")
                
                for key, value in updates.items():
                    if hasattr(template, key):
                        setattr(template, key, value)
                
                template.updated_at = datetime.now()
                await session.commit()
                await session.refresh(template)
                logger.info(f"Template {template_id} erfolgreich aktualisiert")
                return self._to_dict(template)
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Templates {template_id}: {str(e)}")
            raise
    
    @log_function_call
    async def delete_template(self, template_id: str) -> bool:
        """Löscht ein Template aus der Datenbank"""
        await self._ensure_initialized()
        from database.models import Template
        try:
            async with self.async_session() as session:
                template = await session.get(Template, template_id)
                if not template:
                    logger.warning(f"Template {template_id} nicht gefunden")
                    return False
                
                await session.delete(template)
                await session.commit()
                logger.info(f"Template {template_id} erfolgreich gelöscht")
                return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Templates {template_id}: {str(e)}")
            return False
    
    def _to_dict(self, template: Optional['Template']) -> Dict[str, Any]:
        """Konvertiert ein Template-Objekt in ein Dictionary"""
        if not template:
            return {}
        return {
            "id": template.id,
            "name": template.name,
            "content": template.content,
            "description": template.description,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        } 
