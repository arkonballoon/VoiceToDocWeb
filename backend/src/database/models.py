from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime

Base = declarative_base()

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 