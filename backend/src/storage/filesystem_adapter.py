import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from .storage_adapter import StorageAdapter
from utils.logger import get_logger

logger = get_logger(__name__)

class FilesystemAdapter(StorageAdapter):
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.templates_file = self.storage_path / "templates.json"
        
        # Initialisiere templates.json wenn nicht vorhanden oder leer
        if not self.templates_file.exists():
            self._initialize_templates_file()
        else:
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:  # Datei ist leer
                        self._initialize_templates_file()
                    else:
                        # Teste ob valid JSON
                        json.loads(content)
            except (json.JSONDecodeError, Exception):
                # Bei ungültigem JSON oder anderen Fehlern: neu initialisieren
                self._initialize_templates_file()
    
    def _initialize_templates_file(self):
        """Initialisiert die templates.json mit einem leeren Array"""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        logger.info(f"templates.json initialisiert in {self.templates_file}")
    
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Dict[str, Any]:
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
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
        templates = await self.get_templates()
        templates.append(template_data)
        
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=4, ensure_ascii=False)
            
        return template_data 
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Alle Templates laden"""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Templates: {str(e)}")
            return []
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Einzelnes Template laden"""
        template_path = self.storage_path / f"{template_id}.json"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Fehler beim Laden des Templates {template_id}: {str(e)}")
            return None
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Template aktualisieren"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} nicht gefunden")
        
        template.update(updates)
        template["updated_at"] = datetime.now().isoformat()
        
        # Speichere aktualisiertes Template
        template_path = self.storage_path / f"{template_id}.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        
        # Aktualisiere templates.json
        templates = await self.get_templates()
        templates = [t if t["id"] != template_id else template for t in templates]
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=4, ensure_ascii=False)
            
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Template löschen"""
        template_path = self.storage_path / f"{template_id}.json"
        try:
            # Lösche Template-Datei
            template_path.unlink(missing_ok=True)
            
            # Aktualisiere templates.json
            templates = await self.get_templates()
            templates = [t for t in templates if t["id"] != template_id]
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=4, ensure_ascii=False)
                
            return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Templates {template_id}: {str(e)}")
            return False 