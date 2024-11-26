import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
from models.template import Template

class TemplateService:
    def __init__(self, storage_path: Path = Path("data/templates")):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def save_template(self, name: str, content: str, description: Optional[str] = None) -> Template:
        template = Template(
            id=str(uuid.uuid4()),
            name=name,
            content=content,
            description=description,
            created_at=datetime.now()
        )
        
        with open(self.storage_path / f"{template.id}.json", "w") as f:
            json.dump(template.dict(), f, default=str)
            
        return template
    
    def get_templates(self) -> List[Template]:
        templates = []
        for file in self.storage_path.glob("*.json"):
            with open(file, "r") as f:
                data = json.load(f)
                templates.append(Template(**data))
        return templates
    
    def delete_template(self, template_id: str) -> bool:
        template_file = self.storage_path / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()
            return True
        return False 