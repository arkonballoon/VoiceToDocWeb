import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from models.template import Template, TemplateUpdate
from utils.logger import log_function_call
import logging

logger = logging.getLogger(__name__)

class TemplateNotFoundError(Exception):
    """Ausnahme, die ausgelöst wird, wenn ein Template nicht gefunden wird."""
    pass

class TemplateService:
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.templates_file = self.storage_path / "templates.json"
        
        logger.info(f"Template Service initialisiert mit Pfad: {self.storage_path}")
        
        # Initialisiere templates.json mit existierenden Template-Dateien
        if not self.templates_file.exists() or self._is_empty_json(self.templates_file):
            logger.info(f"Initialisiere templates.json in {self.templates_file}")
            existing_templates = []
            
            # Suche nach .json Dateien im Verzeichnis
            for file in self.storage_path.glob("*.json"):
                if file.name != "templates.json":
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            logger.info(f"Gefundenes Template in {file}: {template_data.get('name', 'Unbekannt')}")
                            existing_templates.append(template_data)
                    except Exception as e:
                        logger.error(f"Fehler beim Laden von {file}: {str(e)}")
            
            logger.info(f"Gefundene Template-Dateien: {len(existing_templates)}")
            
            # Speichere gefundene Templates
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(existing_templates, f, indent=4, ensure_ascii=False)

    def _is_empty_json(self, file_path: Path) -> bool:
        """Prüft ob die JSON-Datei leer ist oder nur ein leeres Array enthält"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return len(content) == 0
        except:
            return True
    
    @log_function_call
    def save_template(self, name: str, content: str, description: Optional[str] = None) -> Template:
        """Speichert ein neues Template"""
        now = datetime.now().isoformat()
        template_id = str(uuid.uuid4())
        
        template_data = {
            "id": template_id,
            "name": name,
            "content": content,
            "description": description or "",
            "created_at": now,
            "updated_at": now
        }
        
        # Speichere Template in separater Datei
        template_path = self.storage_path / f"{template_id}.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=4, ensure_ascii=False)
            
        # Aktualisiere templates.json
        templates = self.get_templates()
        templates.append(Template(**template_data))
        
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump([t.dict() for t in templates], f, indent=4, ensure_ascii=False)
            
        return Template(**template_data)
    
    @log_function_call
    def get_templates(self) -> List[Template]:
        """Gibt alle verfügbaren Templates zurück."""
        logger.debug(f"Lade Templates aus: {self.templates_file}")
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
                templates = [Template(**t) for t in templates_data]
                logger.info(f"Gefundene Templates: {len(templates)}")
                return templates
        except Exception as e:
            logger.error(f"Fehler beim Laden der Templates: {str(e)}")
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