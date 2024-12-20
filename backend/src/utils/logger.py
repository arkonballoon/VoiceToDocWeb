import logging
import sys
from pathlib import Path
from datetime import datetime
import json
from functools import wraps
import traceback
import asyncio

class CustomJsonFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
            
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        return json.dumps(log_obj)

class HumanReadableFormatter(logging.Formatter):
    def __init__(self):
        super().__init__('%(asctime)s - %(levelname)s - %(module)s - %(message)s')

def configure_logging(log_file: Path = None, level: int = logging.DEBUG):
    """
    Zentrale Logging-Konfiguration für die gesamte Anwendung
    """
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Console Handler mit menschenlesbarem Format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(HumanReadableFormatter())
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File Handler (optional) mit JSON Format
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomJsonFormatter())
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

def get_logger(name: str = None):
    """
    Erstellt einen Logger mit dem angegebenen Namen oder verwendet __name__ als Standard.
    
    Args:
        name (str, optional): Name des Loggers. Defaults to None.
    """
    logger = logging.getLogger(name if name else __name__)
    
    # Verhindert doppelte Handler
    if not logger.handlers:
        # Handler hinzufügen
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    
    return logger

def log_function_call(logger: logging.Logger):
    """
    Decorator für Funktions-Logging
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

