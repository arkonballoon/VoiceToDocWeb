import logging
import sys
from pathlib import Path
from datetime import datetime
import json
from functools import wraps
import traceback
import asyncio
import functools
import inspect

# Flag für die Logger-Konfiguration
_is_logging_configured = False

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
    global _is_logging_configured
    
    # Wenn das Logging bereits konfiguriert wurde, nichts tun
    if _is_logging_configured:
        return
        
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    
    # Alle existierenden Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
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
    
    _is_logging_configured = True

def get_logger(name: str = None) -> logging.Logger:
    """
    Zentrale Funktion zum Erstellen eines Loggers
    """
    return logging.getLogger(name or __name__)

def log_function_call(func=None):
    """
    Flexibler Decorator für Funktions-Logging
    Kann mit oder ohne Klammern verwendet werden: @log_function_call oder @log_function_call()
    """
    if func is None:
        return log_function_call  # Rekursiver Aufruf wenn ohne Funktion aufgerufen
        
    logger = get_logger(func.__module__)
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger.debug(f"Start: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Ende: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Fehler in {func.__name__}: {str(e)}")
            logger.exception(e)
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger.debug(f"Start: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Ende: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Fehler in {func.__name__}: {str(e)}")
            logger.exception(e)
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
