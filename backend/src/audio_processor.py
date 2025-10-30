import subprocess
from pathlib import Path
from typing import List
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import io
import wave
from utils.logger import get_logger
from utils.exceptions import AudioProcessingError
from config import settings

logger = get_logger(__name__)

class AudioProcessor:
    """
    Klasse zur Verarbeitung von Audiodateien.
    """
    
    def __init__(self):
        """
        Initialisiert den AudioProcessor mit Werten aus der Konfiguration
        """
        self.min_silence_len = settings.AUDIO_MIN_SILENCE_LEN
        self.silence_thresh = settings.AUDIO_SILENCE_THRESH
        self.min_chunk_length = settings.AUDIO_MIN_CHUNK_LENGTH
        self.max_chunk_length = settings.AUDIO_MAX_CHUNK_LENGTH
        
        logger.debug(
            f"AudioProcessor initialisiert mit: "
            f"min_silence_len={self.min_silence_len}, "
            f"silence_thresh={self.silence_thresh}, "
            f"min_chunk_length={self.min_chunk_length}, "
            f"max_chunk_length={self.max_chunk_length}"
        )
    
    def convert_webm_to_wav(self, input_path: Path, output_path: Path) -> bool:
        """
        Konvertiert WebM-Audio zu WAV-Format mit den für Whisper erforderlichen Parametern.
        """
        try:
            command = [
                'ffmpeg',
                '-i', str(input_path),
                '-ar', '16000',       # Abtastrate auf 16 kHz
                '-ac', '1',           # Mono
                '-sample_fmt', 's16', # 16-bit PCM
                str(output_path)
            ]
            
            result = subprocess.run(command, check=True, capture_output=True)
            if result.returncode != 0:
                raise AudioProcessingError(
                    "FFmpeg-Konvertierung fehlgeschlagen",
                    original_error=subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
                )
            return True
            
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg-Fehler: {e.stderr.decode() if e.stderr else 'Unbekannter Fehler'}",
                original_error=e
            )
        except Exception as e:
            raise AudioProcessingError(
                "Unerwarteter Fehler bei der Audiokonvertierung",
                original_error=e
            )

    def detect_silence(self, audio_path: Path) -> List[tuple]:
        """
        Erkennt Stille in einer Audiodatei.
        """
        try:
            audio = AudioSegment.from_wav(str(audio_path))
            silence_ranges = detect_nonsilent(
                audio,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh
            )
            return silence_ranges
        except Exception as e:
            raise AudioProcessingError(
                "Fehler bei der Stilleerkennung",
                original_error=e
            )

    def split_audio(self, audio_path: Path, output_dir: Path) -> List[Path]:
        """
        Teilt eine Audiodatei an Stellen der Stille.
        """
        try:
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
                
            audio = AudioSegment.from_wav(str(audio_path))
            silence_ranges = self.detect_silence(audio_path)
            
            if not silence_ranges:
                raise AudioProcessingError("Keine geeigneten Stellen zum Teilen gefunden")
                
            chunks = []
            last_end = 0
            
            for start, end in silence_ranges:
                if start - last_end >= self.min_chunk_length:
                    chunk = audio[last_end:start]
                    chunk_path = output_dir / f"chunk_{len(chunks)}.wav"
                    chunk.export(str(chunk_path), format="wav")
                    chunks.append(chunk_path)
                last_end = end
                
            # Letztes Segment
            if len(audio) - last_end >= self.min_chunk_length:
                chunk = audio[last_end:]
                chunk_path = output_dir / f"chunk_{len(chunks)}.wav"
                chunk.export(str(chunk_path), format="wav")
                chunks.append(chunk_path)
                
            if not chunks:
                raise AudioProcessingError("Keine gültigen Audiochunks erzeugt")
                
            return chunks
            
        except AudioProcessingError:
            raise
        except Exception as e:
            raise AudioProcessingError(
                "Fehler beim Aufteilen der Audiodatei",
                original_error=e
            ) 
