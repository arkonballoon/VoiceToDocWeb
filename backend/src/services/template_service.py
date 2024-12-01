import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from models.template import Template, TemplateUpdate
from utils.logger import log_function_call
import logging

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Konnte Verzeichnis nicht erstellen: {str(e)}")
        
    @log_function_call(logger)
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Template:
        if not name or not content:
            raise ValueError("Name und Content sind erforderlich")
            
        try:
            template = Template(
                id=str(uuid.uuid4()),
                name=name,
                content=content,
                description=description,
                created_at=datetime.now()
            )
            
            # Erstelle JSON-Daten
            template_data = template.dict()
            json_data = json.dumps(template_data, default=str, ensure_ascii=False)
            
            # Überprüfe, ob das JSON gültig ist
            try:
                json.loads(json_data)
            except json.JSONDecodeError as je:
                raise RuntimeError(f"Ungültiges JSON-Format: {str(je)}")
            
            # Speichere die Datei
            template_path = self.storage_path / f"{template.id}.json"
            try:
                template_path.write_text(json_data, encoding='utf-8')
            except IOError as ioe:
                raise RuntimeError(f"Fehler beim Schreiben der Datei: {str(ioe)}")
                
            return template
        except Exception as e:
            logger.error(f"Template Erstellung fehlgeschlagen: {str(e)}")
            logger.debug(f"Template Daten: name={name}, content={content}, description={description}")
            raise RuntimeError(f"Fehler beim Speichern des Templates: {str(e)}")
    
    def get_templates(self) -> List[Template]:
        templates = []
        try:
            for file in self.storage_path.glob("*.json"):
                try:
                    data = json.loads(file.read_text(encoding='utf-8'))
                    templates.append(Template(**data))
                except json.JSONDecodeError as e:
                    print(f"Fehler beim Dekodieren von {file}: {str(e)}")
                    continue  # Überspringt die fehlerhafte Datei
            return templates
        except Exception as e:
            raise RuntimeError(f"Fehler beim Laden der Templates: {str(e)}")
    
    def delete_template(self, template_id: str) -> bool:
        template_file = self.storage_path / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()
            return True
        return False 
    
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