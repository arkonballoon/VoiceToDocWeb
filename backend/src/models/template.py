from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List

class Template(BaseModel):
    id: str
    name: str
    content: str
    description: Optional[str] = None
    created_at: datetime
    file_format: Optional[str] = None  # 'markdown', 'docx', 'xlsx'
    placeholders: Optional[Dict[str, str]] = None  # Platzhaltername -> Prompt
    file_path: Optional[str] = None  # Pfad zur Originaldatei (falls vorhanden)

class TemplateUpdate(BaseModel):
    """Schema für Template-Updates"""
    content: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    placeholders: Optional[Dict[str, str]] = None  # Platzhaltername -> Prompt 
