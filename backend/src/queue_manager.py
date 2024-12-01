import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable, List, Tuple, NamedTuple
import logging
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import tempfile
from pathlib import Path
from transcriber import Transcriber
import time
from utils.logger import get_logger, log_function_call

logger = get_logger(__name__)

class TranscriptionProgress(NamedTuple):
    """Repräsentiert den Fortschritt einer Transkription"""
    total_chunks: int
    processed_chunks: int
    estimated_time: float  # in Sekunden
    average_chunk_time: float  # in Sekunden

@dataclass
class TranscriptionTask:
    """Repräsentiert eine Transkriptionsaufgabe in der Queue"""
    id: str
    audio_data: bytes
    previous_text: str
    created_at: datetime
    websocket_id: str
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[TranscriptionProgress] = None
    start_time: Optional[float] = None
    chunk_times: List[float] = field(default_factory=list)

class TranscriptionQueueManager:
    """Verwaltet die asynchrone Verarbeitung von Transkriptionsaufgaben"""
    
    def __init__(
        self, 
        max_queue_size: int = 100,
        max_workers: int = 2,
        transcriber: Optional[Transcriber] = None
    ):
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.max_workers = max_workers
        self.active_tasks: Dict[str, TranscriptionTask] = {}
        self.workers: List[asyncio.Task] = []
        self.callbacks: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        
        if transcriber is None:
            raise ValueError("Transcriber instance must be provided")
        
        self.transcriber = transcriber
        self.transcriber_lock = asyncio.Semaphore(1)
        
        # Worker-ID-Counter
        self._worker_id = 0
        
    @property
    def worker_id(self) -> int:
        """Gibt eine eindeutige Worker-ID zurück"""
        self._worker_id = (self._worker_id + 1) % self.max_workers
        return self._worker_id
        
    @log_function_call(logger)
    async def start(self):
        """Startet die Worker-Tasks"""
        for worker_id in range(self.max_workers):
            worker = asyncio.create_task(
                self._process_queue(worker_id)
            )
            self.workers.append(worker)
        logger.info(f"{self.max_workers} Transkriptions-Worker gestartet")

    @log_function_call(logger)
    async def stop(self):
        """Stoppt alle Worker-Tasks"""
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("Transkriptions-Worker gestoppt")

    def _calculate_progress(self, task: TranscriptionTask) -> TranscriptionProgress:
        """Berechnet den Fortschritt einer Transkription"""
        processed_chunks = len(task.chunk_times)
        if processed_chunks == 0:
            return TranscriptionProgress(1, 0, 0.0, 0.0)
            
        # Durchschnittliche Zeit pro Chunk berechnen
        avg_chunk_time = sum(task.chunk_times) / processed_chunks
        
        # Geschätzte Restzeit berechnen
        remaining_chunks = max(0, task.total_chunks - processed_chunks)
        estimated_time = remaining_chunks * avg_chunk_time
        
        return TranscriptionProgress(
            total_chunks=task.total_chunks,
            processed_chunks=processed_chunks,
            estimated_time=estimated_time,
            average_chunk_time=avg_chunk_time
        )

    @log_function_call(logger)
    async def add_task(
        self, 
        audio_data: bytes, 
        previous_text: str,
        websocket_id: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        total_chunks: int = 1  # Neue Parameter für Fortschrittsanzeige
    ) -> str:
        """
        Fügt eine neue Transkriptionsaufgabe zur Queue hinzu
        
        Args:
            audio_data: Audio-Bytes im WAV-Format
            previous_text: Vorheriger Transkriptionstext
            websocket_id: ID der WebSocket-Verbindung
            callback: Async Callback-Funktion für Ergebnisse
            
        Returns:
            Task-ID
        """
        task_id = str(uuid.uuid4())
        task = TranscriptionTask(
            id=task_id,
            audio_data=audio_data,
            previous_text=previous_text,
            created_at=datetime.now(),
            websocket_id=websocket_id,
            total_chunks=total_chunks  # Gesamtanzahl der erwarteten Chunks
        )
        
        self.active_tasks[task_id] = task
        self.callbacks[task_id] = callback
        await self.queue.put(task_id)
        
        # Initiales Fortschritts-Update senden
        if callback:
            await callback({
                "type": "progress_update",
                "task_id": task_id,
                "status": "queued",
                "progress": {
                    "total_chunks": total_chunks,
                    "processed_chunks": 0,
                    "estimated_time": 0,
                    "average_chunk_time": 0
                }
            })
        
        return task_id

    @log_function_call(logger)
    async def _transcribe_audio(
        self,
        worker_id: int,
        audio_data: bytes,
        previous_text: str
    ) -> Tuple[str, float]:
        """
        Führt die Transkription mit dem gemeinsam genutzten Transcriber durch
        """
        async with self.transcriber_lock:
            # Temporäre Datei für Audio erstellen
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                try:
                    # Audio-Daten in temporäre Datei schreiben
                    temp_file.write(audio_data)
                    temp_file.flush()
                    
                    # Transkription durchführen
                    text, confidence = self.transcriber.transcribe_audio(
                        temp_path,
                        previous_text
                    )
                    
                    return text, confidence
                    
                finally:
                    # Temporäre Datei aufräumen
                    temp_path.unlink()

    async def _process_queue(self, worker_id: int):
        """Worker-Prozess für die Verarbeitung von Queue-Einträgen"""
        logger.info(f"Worker {worker_id} gestartet")
        
        while True:
            try:
                task_id = await self.queue.get()
                task = self.active_tasks.get(task_id)
                
                if not task:
                    self.queue.task_done()
                    continue
                
                task.status = "processing"
                task.start_time = time.time()
                callback = self.callbacks.get(task_id)
                
                try:
                    # Status-Update senden
                    if callback:
                        await callback({
                            "type": "status_update",
                            "task_id": task_id,
                            "status": "processing"
                        })
                    
                    # Transkription durchführen
                    chunk_start_time = time.time()
                    text, confidence = await self._transcribe_audio(
                        worker_id,
                        task.audio_data,
                        task.previous_text
                    )
                    
                    # Chunk-Zeit speichern
                    chunk_time = time.time() - chunk_start_time
                    task.chunk_times.append(chunk_time)
                    
                    # Fortschritt berechnen und Update senden
                    progress = self._calculate_progress(task)
                    if callback:
                        await callback({
                            "type": "progress_update",
                            "task_id": task_id,
                            "status": "processing",
                            "progress": progress._asdict()
                        })
                    
                    # Ergebnis speichern
                    task.result = {
                        "text": text,
                        "confidence": confidence,
                        "processing_time": time.time() - task.start_time
                    }
                    task.status = "completed"
                    
                    # Abschluss-Update senden
                    if callback:
                        await callback({
                            "type": "transcription_result",
                            "task_id": task_id,
                            "status": "completed",
                            "result": task.result,
                            "progress": progress._asdict()
                        })
                    
                except Exception as e:
                    logger.error(f"Fehler bei der Verarbeitung von Task {task_id}: {str(e)}")
                    task.status = "failed"
                    task.error = str(e)
                    
                    if callback:
                        await callback({
                            "type": "error",
                            "task_id": task_id,
                            "status": "failed",
                            "error": str(e)
                        })
                
                finally:
                    # Aufräumen
                    self.queue.task_done()
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]
                    if task_id in self.callbacks:
                        del self.callbacks[task_id]
                    
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} wird beendet")
                break
            except Exception as e:
                logger.error(f"Unerwarteter Fehler in Worker {worker_id}: {str(e)}") 