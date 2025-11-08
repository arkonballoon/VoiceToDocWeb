import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from models.template import Template, TemplateUpdate
from utils.logger import get_logger, log_function_call
import logging
from storage.storage_factory import StorageFactory
from utils.singleton import Singleton

logger = get_logger(__name__)

class TemplateNotFoundError(Exception):
    """Ausnahme, die ausgelöst wird, wenn ein Template nicht gefunden wird."""
    pass

class TemplateService(Singleton):
    def _init(self):
        """Initialisierung des TemplateService"""
        self.storage = StorageFactory.get_adapter()
        logger.info("Template Service initialisiert")
    
    async def save_template(
        self, 
        name: str, 
        content: str, 
        description: Optional[str] = None,
        file_format: Optional[str] = None,
        placeholders: Optional[Dict[str, str]] = None,
        file_path: Optional[str] = None
    ) -> Template:
        template_data = await self.storage.save_template(
            name, content, description, file_format, placeholders, file_path
        )
        return Template(**template_data)
    
    @log_function_call
    async def get_templates(self):
        try:
            templates_data = await self.storage.get_templates()
            logger.debug(f"Rohe Template-Daten geladen: {templates_data}")
            
            # Konvertiere die Rohdaten in Template-Objekte
            templates = []
            for template_data in templates_data or []:
                try:
                    template = Template(**template_data)
                    templates.append(template)
                except Exception as e:
                    logger.error(f"Fehler bei der Konvertierung des Templates: {str(e)}")
                    continue
            
            logger.debug(f"Konvertierte Templates: {templates}")
            return templates
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Templates: {str(e)}")
            logger.exception(e)
            return []
    
    @log_function_call
    async def delete_template(self, template_id: str) -> None:
        """Löscht ein Template"""
        try:
            # Prüfe ob das Template existiert
            template = await self.get_template(template_id)
            if not template:
                raise TemplateNotFoundError(f"Template mit ID {template_id} nicht gefunden")
            
            # Lösche das Template über den Storage-Adapter
            await self.storage.delete_template(template_id)
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Templates: {str(e)}")
            raise
    
    @log_function_call
    async def update_template(self, template_id: str, template_update: TemplateUpdate) -> Template:
        """Aktualisiert ein bestehendes Template"""
        try:
            # Hole das bestehende Template
            template = await self.get_template(template_id)
            if not template:
                raise TemplateNotFoundError(f"Template mit ID {template_id} nicht gefunden")
            
            # Aktualisiere die Felder
            update_data = template_update.model_dump(exclude_unset=True)
            
            # Aktualisiere das Template über den Storage-Adapter
            updated_template_data = await self.storage.update_template(
                template_id=template_id,
                updates=update_data
            )
            
            return Template(**updated_template_data)
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Templates: {str(e)}")
            raise
    
    async def get_template(self, template_id: str) -> Optional[Template]:
        """
        Holt ein spezifisches Template anhand seiner ID.
        
        Args:
            template_id: Die ID des gesuchten Templates
            
        Returns:
            Template oder None wenn nicht gefunden
        """
        templates = await self.get_templates()
        return next((t for t in templates if t.id == template_id), None)
