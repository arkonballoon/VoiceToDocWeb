from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Template(BaseModel):
    id: str
    name: str
    content: str
    description: Optional[str] = None
    created_at: datetime 

class TemplateUpdate(BaseModel):
    """Schema für Template-Updates"""
    content: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None 