from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, JSON
from datetime import datetime
import json

Base = declarative_base()

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    file_format = Column(String)  # 'markdown', 'docx', 'xlsx'
    placeholders = Column(Text)  # JSON-String: {"platzhalter": "prompt"}
    file_path = Column(String)  # Pfad zur Originaldatei
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_placeholders_dict(self) -> dict:
        """Konvertiert den JSON-String in ein Dictionary"""
        if not self.placeholders:
            return {}
        try:
            return json.loads(self.placeholders)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_placeholders_dict(self, placeholders: dict):
        """Konvertiert ein Dictionary in einen JSON-String"""
        self.placeholders = json.dumps(placeholders) if placeholders else None 
