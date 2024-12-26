from typing import Dict, Type
from .storage_adapter import StorageAdapter
from .filesystem_adapter import FilesystemAdapter
from .sql_adapter import SQLAdapter
from config import settings

class StorageFactory:
    _adapters: Dict[str, Type[StorageAdapter]] = {
        "filesystem": FilesystemAdapter,
        "sql": SQLAdapter
    }
    
    @classmethod
    def get_adapter(cls, adapter_type: str = None) -> StorageAdapter:
        """Erstellt eine Storage-Adapter-Instanz basierend auf der Konfiguration"""
        adapter_type = adapter_type or settings.STORAGE_TYPE
        
        if adapter_type not in cls._adapters:
            raise ValueError(f"Unbekannter Storage-Typ: {adapter_type}")
            
        adapter_class = cls._adapters[adapter_type]
        
        if adapter_type == "filesystem":
            return adapter_class(storage_path=settings.TEMPLATE_DIR)
        elif adapter_type == "sql":
            return adapter_class(connection_string=settings.DATABASE_URL)
            
        raise ValueError(f"Keine Konfiguration für Storage-Typ: {adapter_type}") 