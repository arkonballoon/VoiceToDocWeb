from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Text
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from .storage_adapter import StorageAdapter

Base = declarative_base()

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class SQLAdapter(StorageAdapter):
    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Dict[str, Any]:
        template_id = str(uuid.uuid4())
        now = datetime.now()
        
        async with self.async_session() as session:
            template = Template(
                id=template_id,
                name=name,
                content=content,
                description=description,
                created_at=now,
                updated_at=now
            )
            session.add(template)
            await session.commit()
            
            return {
                "id": template_id,
                "name": name,
                "content": content,
                "description": description,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            } 