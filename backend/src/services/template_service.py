import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from models.template import Template, TemplateUpdate
from utils.logger import log_function_call
import logging
from storage.storage_factory import StorageFactory

logger = logging.getLogger(__name__)

class TemplateNotFoundError(Exception):
    """Ausnahme, die ausgelöst wird, wenn ein Template nicht gefunden wird."""
    pass

class TemplateService:
    def __init__(self):
        self.storage = StorageFactory.get_adapter()
        logger.info("Template Service initialisiert")
    
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Template:
        template_data = await self.storage.save_template(name, content, description)
        return Template(**template_data)
    
    @log_function_call
    async def get_templates(self):
        try:
            templates = await self.storage.get_templates()
            logger.debug(f"Templates geladen: {templates}")
            return templates or []  # Stelle sicher, dass wir immer ein Array zurückgeben
        except Exception as e:
            logger.error(f"Fehler beim Laden der Templates: {str(e)}")
            logger.exception(e)
            return []
    
    @log_function_call
    def delete_template(self, template_id: str) -> bool:
        template_file = self.storage_path / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()
            return True
        return False 
    
    @log_function_call
    def update_template(self, template_id: str, template_update: TemplateUpdate) -> Template:
        """Aktualisiert ein bestehendes Template"""
        template_path = self.storage_path / f"{template_id}.json"
        
        if not template_path.exists():
            raise TemplateNotFoundError(f"Template mit ID {template_id} nicht gefunden")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Aktualisiere nur die bereitgestellten Felder
            if template_update.content is not None:
                template_data['content'] = template_update.content
            if template_update.name is not None:
                template_data['name'] = template_update.name
            if template_update.description is not None:
                template_data['description'] = template_update.description
            
            template_data['updated_at'] = datetime.now().isoformat()
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=4, ensure_ascii=False)
            
            return Template(**template_data)
        
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Templates: {str(e)}")
            raise
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Holt ein spezifisches Template anhand seiner ID.
        
        Args:
            template_id: Die ID des gesuchten Templates
            
        Returns:
            Template oder None wenn nicht gefunden
        """
        templates = self.get_templates()
        return next((t for t in templates if t.id == template_id), None)