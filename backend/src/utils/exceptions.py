from fastapi import HTTPException

class VoiceToDocException(Exception):
    """Basis-Ausnahme für alle anwendungsspezifischen Fehler"""
    pass

class AudioProcessingError(VoiceToDocException):
    """Fehler bei der Audioverarbeitung"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class TranscriptionError(VoiceToDocException):
    """Fehler während der Transkription"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class TemplateError(VoiceToDocException):
    """Fehler bei Template-Operationen"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

def handle_voice_to_doc_exception(exc: VoiceToDocException) -> HTTPException:
    """Konvertiert anwendungsspezifische Ausnahmen in HTTPException"""
    error_mappings = {
        AudioProcessingError: 400,
        TranscriptionError: 500,
        TemplateError: 400
    }
    
    status_code = error_mappings.get(type(exc), 500)
    detail = {
        "error": exc.__class__.__name__,
        "message": str(exc),
        "details": str(exc.original_error) if hasattr(exc, 'original_error') and exc.original_error else None
    }
    
    return HTTPException(status_code=status_code, detail=detail) 