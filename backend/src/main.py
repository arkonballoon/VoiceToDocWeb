from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, WebSocketDisconnect, Body
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
from services.template_service import TemplateService
from models.template import Template, TemplateUpdate
from typing import List

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Relativer Pfad von main.py aus zu den Templates
TEMPLATE_PATH = Path("data/templates").resolve()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan-Manager für FastAPI.
    Handhabt Startup- und Shutdown-Events der Anwendung.
    """
    try:
        # Startup
        logger.info("Starte Anwendung...")
        await queue_manager.start()
        yield
    finally:
        # Shutdown
        logger.info("Fahre Anwendung herunter...")
        await queue_manager.stop()

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
    redoc_url="/redoc"  # ReDoc auf /redoc
)

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.178.67:3000"],  # Explizit Frontend-Origin angeben
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporäres Verzeichnis für Audio-Dateien
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Transcriber-Instanz erstellen (nur einmal)
transcriber = Transcriber()
audio_processor = AudioProcessor()

# Queue-Manager erstellen und Transcriber übergeben
queue_manager = TranscriptionQueueManager(
    max_workers=2,
    transcriber=transcriber
)

# Template-Service initialisieren
template_service = TemplateService(storage_path=TEMPLATE_PATH)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Globaler Exception Handler"""
    logger.error(f"Unbehandelte Ausnahme: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Interner Serverfehler", "detail": str(exc)}
    )

@app.post("/upload_audio", 
    tags=["Audio"],
    summary="Audio-Datei hochladen und transkribieren",
    response_model=dict,
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
            if not audio_processor.convert_webm_to_wav(webm_file, wav_file):
                raise HTTPException(
                    status_code=500,
                    detail="Fehler bei der Audio-Konvertierung"
                )
            
            # Transkription durchführen
            text, confidence = transcriber.transcribe_audio(wav_file)
            
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
    
    Unterstützt:
    * Echtzeit-Audio-Streaming
    * Chunk-basierte Verarbeitung
    * Fortschrittsanzeige
    * Status-Updates
    * Fehlerbehandlung und Wiederverbindung
    
    Nachrichtentypen:
    * chunks_info: Informationen über die Anzahl der Chunks
    * task_created: Neue Transkriptionsaufgabe erstellt
    * progress_update: Fortschrittsupdate
    * transcription_result: Transkriptionsergebnis
    * error: Fehlermeldung
    * info: Informationsmeldung
    * warning: Warnmeldung
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
                if audio_processor.is_silence(data):
                    await websocket.send_json({
                        "type": "info",
                        "message": "Stille erkannt"
                    })
                    continue
                
                # Audio in Chunks aufteilen
                chunks = audio_processor.process_audio_chunk(data)
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
                        task_id = await queue_manager.add_task(
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
        template = template_service.save_template(
            name=name,
            content=content,
            description=description
        )
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates/", response_model=list[Template])
async def get_templates():
    return template_service.get_templates()

@app.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    if template_service.delete_template(template_id):
        return {"message": "Template erfolgreich gelöscht"}
    raise HTTPException(status_code=404, detail="Template nicht gefunden")

@app.put("/templates/{template_id}")
async def update_template(template_id: str, template_update: TemplateUpdate):
    """Aktualisiert ein bestehendes Template"""
    try:
        updated_template = template_service.update_template(template_id, template_update)
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