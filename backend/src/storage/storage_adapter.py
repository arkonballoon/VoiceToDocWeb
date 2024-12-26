from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

class StorageAdapter(ABC):
    """Basis-Interface für Storage-Implementierungen"""
    
    @abstractmethod
    async def save_template(self, name: str, content: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Template speichern"""
        pass
    
    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Einzelnes Template laden"""
        pass
        
    @abstractmethod
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Alle Templates laden"""
        pass
    
    @abstractmethod
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Template aktualisieren"""
        pass
    
    @abstractmethod
    async def delete_template(self, template_id: str) -> bool:
        """Template löschen"""
        pass 