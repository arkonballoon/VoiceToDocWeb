from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, WebSocketDisconnect, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from pathlib import Path
import uuid
import logging
from transcriber import Transcriber
from audio_processor import AudioProcessor
from queue_manager import TranscriptionQueueManager
import json
import backoff
from contextlib import asynccontextmanager
from services.template_service import TemplateService, TemplateNotFoundError
from models.template import Template, TemplateUpdate
from typing import List
from utils.logger import get_logger, configure_logging
from utils.exceptions import VoiceToDocException, AudioProcessingError, TranscriptionError, handle_voice_to_doc_exception
from config import settings
from pydantic import BaseModel
from services.template_processor import TemplateProcessor
import math

# Verzeichnisse erstellen
LOG_DIR = Path("/app/data/logs")
TEMPLATE_PATH = Path("/app/data/templates")
TEMP_DIR = Path("/app/data/temp")

# Verzeichnisse erstellen
for directory in [LOG_DIR, TEMPLATE_PATH, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Logger Setup
configure_logging(
    log_file=LOG_DIR / "app.log",
    level=settings.LOG_LEVEL
)

logger = get_logger(__name__)

# Speicher für Verarbeitungsergebnisse
processing_results: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan-Manager für FastAPI.
    Handhabt Startup- und Shutdown-Events der Anwendung.
    """
    try:
        # Startup
        logger.info("Starte Anwendung...")
        
        # Initialisiere Komponenten
        app.state.template_service = TemplateService()
        app.state.template_processor = TemplateProcessor()
        app.state.transcriber = Transcriber()
        app.state.audio_processor = AudioProcessor()
        
        # Queue-Manager mit Transcriber initialisieren
        app.state.queue_manager = TranscriptionQueueManager(
            max_workers=2,
            transcriber=app.state.transcriber
        )
        
        # Starte Dienste
        await app.state.queue_manager.start()
        logger.info("Alle Komponenten erfolgreich initialisiert")
        
        yield
    finally:
        # Shutdown
        logger.info("Fahre Anwendung herunter...")
        
        # Cleanup der Komponenten
        if hasattr(app.state, 'queue_manager'):
            await app.state.queue_manager.stop()
            
        # Bereinige temporäre Dateien
        if TEMP_DIR.exists():
            for file in TEMP_DIR.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Fehler beim Löschen von {file}: {e}")
            try:
                TEMP_DIR.rmdir()
            except Exception as e:
                logger.error(f"Fehler beim Löschen des TEMP_DIR: {e}")
        
        logger.info("Cleanup abgeschlossen")

app = FastAPI(
    title="Voice-to-Doc API",
    description="""
    Eine API für Audioaufnahme und Transkription.
    
    Features:
    * Upload von Audiodateien (WebM, WAV, MP3)
    * Echtzeit-Audiostreaming über WebSocket
    * Automatische Transkription mit Whisper
    * Fortschrittsanzeige und Statusupdates
    """,
    version="1.0.0",
    docs_url="/",  # Swagger UI auf Root-Pfad
    redoc_url="/redoc",  # ReDoc auf /redoc
    lifespan=lifespan
)

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Globaler Exception Handler"""
    logger.error(f"Unbehandelte Ausnahme: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Interner Serverfehler", "detail": str(exc)}
    )

@app.exception_handler(VoiceToDocException)
async def voice_to_doc_exception_handler(request, exc: VoiceToDocException):
    """Globaler Exception Handler für anwendungsspezifische Fehler"""
    http_exc = handle_voice_to_doc_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

class AudioUploadResponse(JSONResponse):
    def render(self, content: dict) -> bytes:
        def sanitize_content(obj):
            if isinstance(obj, dict):
                return {k: sanitize_content(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_content(x) for x in obj]
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return 0.0
                return obj
            return obj
            
        sanitized_content = sanitize_content(content)
        return super().render(sanitized_content)

@app.post("/upload_audio", 
    tags=["Audio"],
    summary="Audio-Datei hochladen und transkribieren",
    response_class=AudioUploadResponse,
    responses={
        200: {
            "description": "Erfolgreiche Transkription",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Beispieltext der Transkription",
                        "confidence": 0.95,
                        "status": "success"
                    }
                }
            }
        },
        400: {
            "description": "Ungültige Anfrage",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Nicht unterstütztes Audioformat. Erlaubt sind: WebM, WAV, MP3"
                    }
                }
            }
        },
        500: {
            "description": "Serverfehler",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Interner Serverfehler",
                        "detail": "Fehler bei der Verarbeitung"
                    }
                }
            }
        }
    }
)
@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def upload_audio(
    file: UploadFile = File(
        ...,
        description="Audio-Datei im WebM, WAV oder MP3 Format"
    )
):
    """
    Lädt eine Audiodatei hoch und transkribiert sie.
    
    - **file**: Die hochzuladende Audiodatei
    
    Returns:
        Ein Dictionary mit dem transkribierten Text, der Konfidenz und dem Status
    
    Raises:
        HTTPException: Bei ungültigen Dateiformaten oder Verarbeitungsfehlern
    """
    try:
        if not file.filename.endswith(('.webm', '.wav', '.mp3')):
            raise HTTPException(
                status_code=400,
                detail="Nicht unterstütztes Audioformat. Erlaubt sind: WebM, WAV, MP3"
            )
        
        # Eindeutigen Dateinamen generieren
        webm_file = TEMP_DIR / f"{uuid.uuid4()}.webm"
        wav_file = TEMP_DIR / f"{uuid.uuid4()}.wav"
        
        try:
            # WebM-Datei speichern
            content = await file.read()
            if len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Die Audiodatei ist leer"
                )
                
            with open(webm_file, "wb") as buffer:
                buffer.write(content)
            
            # Zu WAV konvertieren
            if not app.state.audio_processor.convert_webm_to_wav(webm_file, wav_file):
                raise HTTPException(
                    status_code=500,
                    detail="Fehler bei der Audio-Konvertierung"
                )
            
            # Transkription durchführen
            text, confidence = app.state.transcriber.transcribe_audio(wav_file)
            
            return {
                "text": text,
                "confidence": confidence,
                "status": "success"
            }
            
        except Exception as e:
            raise
        finally:
            # Aufräumen der temporären Dateien
            for file in [webm_file, wav_file]:
                if file.exists():
                    try:
                        file.unlink()
                    except Exception as e:
                        logger.warning(f"Fehler beim Löschen der temporären Datei {file}: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Hochladen/Transkribieren: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Verarbeitungsfehler: {str(e)}"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket-Endpunkt für Echtzeit-Audiostreaming und Transkription.
    """
    connection_id = str(uuid.uuid4())
    logger.info(f"Neue WebSocket-Verbindung: {connection_id}")
    
    await websocket.accept()
    previous_text = ""
    reconnect_attempts = 0
    MAX_RECONNECT_ATTEMPTS = 3
    
    async def send_transcription_update(update: Dict[str, Any]):
        """Callback-Funktion für Transkriptions-Updates mit Fehlerbehandlung"""
        try:
            await websocket.send_json(update)
        except WebSocketDisconnect:
            logger.warning(f"WebSocket-Verbindung verloren: {connection_id}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Senden des Updates: {str(e)}")
            await handle_websocket_error(e)
    
    async def handle_websocket_error(error: Exception):
        """Behandelt WebSocket-Fehler und versucht Wiederherstellung"""
        nonlocal reconnect_attempts
        
        if isinstance(error, WebSocketDisconnect):
            if reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
                reconnect_attempts += 1
                logger.info(f"Versuche Wiederverbindung {reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS}")
                await asyncio.sleep(1 * reconnect_attempts)  # Exponentielles Backoff
                try:
                    await websocket.accept()
                    reconnect_attempts = 0
                    return True
                except Exception as e:
                    logger.error(f"Wiederverbindung fehlgeschlagen: {str(e)}")
            return False
        return True
    
    try:
        while True:
            try:
                # Audio-Chunks empfangen
                data = await websocket.receive_bytes()
                
                # Validierung der Audiodaten
                if len(data) == 0:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Leere Audiodaten empfangen"
                    })
                    continue
                
                # Prüfen ob es sich um Stille handelt
                if app.state.audio_processor.is_silence(data):
                    await websocket.send_json({
                        "type": "info",
                        "message": "Stille erkannt"
                    })
                    continue
                
                # Audio in Chunks aufteilen
                chunks = app.state.audio_processor.process_audio_chunk(data)
                total_chunks = len(chunks)
                
                if total_chunks == 0:
                    await websocket.send_json({
                        "type": "warning",
                        "message": "Keine verarbeitbaren Audio-Chunks gefunden"
                    })
                    continue
                
                # Fortschritts-Update senden
                await websocket.send_json({
                    "type": "chunks_info",
                    "total_chunks": total_chunks
                })
                
                for i, chunk in enumerate(chunks, 1):
                    try:
                        # Chunk zur Verarbeitungsqueue hinzufügen
                        task_id = await app.state.queue_manager.add_task(
                            audio_data=chunk,
                            previous_text=previous_text,
                            websocket_id=connection_id,
                            callback=send_transcription_update,
                            total_chunks=total_chunks
                        )
                        
                        # Status-Update senden
                        await websocket.send_json({
                            "type": "task_created",
                            "task_id": task_id,
                            "chunk_number": i,
                            "total_chunks": total_chunks
                        })
                        
                    except Exception as chunk_error:
                        logger.error(f"Fehler bei der Chunk-Verarbeitung: {str(chunk_error)}")
                        await websocket.send_json({
                            "type": "error",
                            "chunk_number": i,
                            "error": str(chunk_error)
                        })
                
            except WebSocketDisconnect as disconnect_error:
                if not await handle_websocket_error(disconnect_error):
                    break
            except Exception as loop_error:
                logger.error(f"Fehler in der Hauptschleife: {str(loop_error)}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(loop_error)
                })
                if not await handle_websocket_error(loop_error):
                    break
                
    except Exception as e:
        logger.error(f"Kritischer WebSocket-Fehler: {str(e)}", exc_info=True)
    finally:
        logger.info(f"WebSocket-Verbindung geschlossen: {connection_id}")
        await websocket.close()

# Benutzerdefinierte OpenAPI-Dokumentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # WebSocket-Dokumentation hinzufügen
    openapi_schema["paths"]["/ws"] = {
        "get": {
            "tags": ["WebSocket"],
            "summary": "WebSocket-Verbindung für Echtzeit-Audiostreaming",
            "description": """
            Etabliert eine WebSocket-Verbindung für:
            * Echtzeit-Audio-Streaming
            * Live-Transkription
            * Fortschritts-Updates
            """,
            "responses": {
                "101": {
                    "description": "WebSocket-Verbindung hergestellt"
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.post("/templates/")
async def create_template(
    name: str = Body(...),
    content: str = Body(...),
    description: str | None = Body(None)
):
    try:
        template = await app.state.template_service.save_template(
            name=name,
            content=content,
            description=description
        )
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates/", response_model=List[Template])
async def get_templates():
    """Gibt alle verfügbaren Templates zurück"""
    try:
        templates = await app.state.template_service.get_templates()
        # Debug-Logging
        logger.debug(f"Geladene Templates: {templates}")
        return templates
    except Exception as e:
        logger.error(f"Fehler beim Laden der Templates: {str(e)}")
        # Stack Trace für besseres Debugging
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    if app.state.template_service.delete_template(template_id):
        return {"message": "Template erfolgreich gelöscht"}
    raise HTTPException(status_code=404, detail="Template nicht gefunden")

@app.put("/templates/{template_id}")
async def update_template(template_id: str, template_update: TemplateUpdate):
    """Aktualisiert ein bestehendes Template"""
    try:
        updated_template = app.state.template_service.update_template(template_id, template_update)
        return updated_template
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Template mit ID {template_id} nicht gefunden"
        )
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Interner Serverfehler beim Aktualisieren des Templates"
        )

# Definiere das Schema für Konfigurationsänderungen
class ConfigUpdate(BaseModel):
    """Schema für Konfigurationsänderungen"""
    AUDIO_MIN_SILENCE_LEN: int | None = None
    AUDIO_SILENCE_THRESH: int | None = None
    AUDIO_MIN_CHUNK_LENGTH: int | None = None
    AUDIO_MAX_CHUNK_LENGTH: int | None = None
    WHISPER_MODEL: str | None = None
    WHISPER_DEVICE_CUDA: str | None = None
    MAX_WORKERS: int | None = None
    LOG_LEVEL: int | None = None
    ALLOWED_ORIGINS: List[str] | None = None

# Füge die Endpunkte zur FastAPI-App hinzu
@app.get("/config", 
    tags=["Konfiguration"],
    summary="Aktuelle Konfiguration abrufen",
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "Aktuelle Konfigurationseinstellungen",
            "content": {
                "application/json": {
                    "example": {
                        "AUDIO_MIN_SILENCE_LEN": 500,
                        "AUDIO_SILENCE_THRESH": -32,
                        "WHISPER_MODEL": "base",
                        "MAX_WORKERS": 3
                    }
                }
            }
        }
    }
)
async def get_config():
    """
    Gibt die aktuelle Konfiguration zurück.
    
    Returns:
        Dict mit den aktuellen Konfigurationseinstellungen
    """
    config_dict = settings.model_dump()
    # Konvertiere Path-Objekte zu Strings
    for key, value in config_dict.items():
        if isinstance(value, Path):
            config_dict[key] = str(value)
    return config_dict

@app.put("/config")
async def update_config(config_update: ConfigUpdate):
    updated_settings = {}
    valid_models = ["tiny", "base", "small", "medium", "large", "large-v3"]
    needs_transcriber_reload = False
    
    update_dict = config_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            if key in ["WHISPER_MODEL", "WHISPER_DEVICE_CUDA"] and value not in valid_models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ungültiges Whisper-Modell für {key}: {value}"
                )
            if key == "MAX_WORKERS" and not (1 <= value <= 10):
                raise HTTPException(
                    status_code=400,
                    detail="MAX_WORKERS muss zwischen 1 und 10 liegen"
                )
            
            # Prüfe ob sich ein Whisper-Modell ändert
            if key in ["WHISPER_MODEL", "WHISPER_DEVICE_CUDA"] and getattr(settings, key) != value:
                needs_transcriber_reload = True
            
            setattr(settings, key, value)
            updated_settings[key] = value
    
    try:
        settings.save_to_file()
        
        # Transcriber neu initialisieren wenn nötig
        if needs_transcriber_reload:
            from transcriber import transcriber_instance
            transcriber_instance.reload_model()
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Speichern der Konfiguration: {str(e)}"
        )
    
    return {
        "message": "Konfiguration aktualisiert",
        "updated_settings": updated_settings,
        "transcriber_reloaded": needs_transcriber_reload
    }

class TemplateProcessingRequest(BaseModel):
    template_id: str
    transcription: str

@app.websocket("/ws/template_processing/{client_id}")
async def template_processing_websocket(websocket: WebSocket, client_id: str):
    """WebSocket-Endpunkt für Template-Verarbeitungs-Updates."""
    await websocket.accept()
    
    try:
        # WebSocket beim TemplateProcessor registrieren
        await app.state.template_processor.register_connection(client_id, websocket)
        
        while True:
            # Heartbeat empfangen aber nicht darauf warten
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket-Fehler: {str(e)}")
    finally:
        try:
            # Verbindung beim Beenden entfernen
            await app.state.template_processor.remove_connection(client_id)
            try:
                await websocket.close()
            except RuntimeError:
                # Ignoriere Fehler wenn die Verbindung bereits geschlossen ist
                pass
        except Exception as e:
            logger.error(f"Fehler beim Schließen der WebSocket-Verbindung: {str(e)}")

@app.post("/process_template")
async def process_template(
    request: TemplateProcessingRequest,
    background_tasks: BackgroundTasks
):
    """Startet die Template-Verarbeitung"""
    try:
        template = await app.state.template_service.get_template(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template nicht gefunden")
        
        process_id = str(uuid.uuid4())
        
        # Verarbeitung im Hintergrund starten
        background_tasks.add_task(
            process_template_background,
            template.content,
            request.transcription,
            process_id,
            app.state.template_processor
        )
        
        return {"process_id": process_id, "status": "processing"}
        
    except Exception as e:
        logger.error(f"Fehler bei der Template-Verarbeitung: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_template_background(
    template: str, 
    transcription: str, 
    process_id: str,
    template_processor: TemplateProcessor
):
    """Führt die Template-Verarbeitung im Hintergrund durch und speichert das Ergebnis"""
    try:
        result = await template_processor.process_template_with_updates(
            template, 
            transcription, 
            process_id
        )
        processing_results[process_id] = result
    except Exception as e:
        logger.error(f"Fehler bei der Hintergrundverarbeitung: {str(e)}")
        processing_results[process_id] = {"error": str(e)}

@app.get("/process_template/{process_id}")
async def get_template_result(process_id: str):
    """Gibt das Ergebnis der Template-Verarbeitung zurück"""
    if process_id not in processing_results:
        raise HTTPException(
            status_code=404,
            detail="Verarbeitungsergebnis nicht gefunden"
        )
    
    result = processing_results[process_id]
    # Optional: Ergebnis nach dem Abrufen löschen
    # del processing_results[process_id]
    
    return result

if __name__ == "__main__":
    import uvicorn
    
    # Uvicorn-Server mit Reload-Option für Entwicklung starten
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Automatisches Neuladen bei Code-Änderungen
        log_level="info"
    ) 