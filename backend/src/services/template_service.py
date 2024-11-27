import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from models.template import Template

class TemplateService:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Konnte Verzeichnis nicht erstellen: {str(e)}")
        
    def save_template(self, name: str, content: str, description: Optional[str] = None) -> Template:
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
            print(f"Debug - Template Erstellung fehlgeschlagen: {str(e)}")
            print(f"Debug - Template Daten: name={name}, content={content}, description={description}")
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