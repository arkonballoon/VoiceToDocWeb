import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
import logging
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import io
import wave

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Klasse zur Verarbeitung von Audiodateien.
    """
    
    def __init__(
        self,
        min_silence_len: int = 500,    # Minimale Stille in ms
        silence_thresh: int = -32,      # Schwellenwert für Stille in dB
        min_chunk_length: int = 2000,   # Minimale Chunklänge in ms
        max_chunk_length: int = 5000    # Maximale Chunklänge in ms
    ):
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
    
    @staticmethod
    def convert_webm_to_wav(input_path: Path, output_path: Path) -> bool:
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
            
            subprocess.run(command, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg-Fehler: {e.stderr.decode()}")
            return False
        except Exception as e:
            logger.error(f"Konvertierungsfehler: {str(e)}")
            return False

    def process_audio_chunk(self, audio_data: bytes) -> List[bytes]:
        """
        Verarbeitet einen Audio-Chunk und teilt ihn in kleinere Chunks basierend auf Stille.
        
        Args:
            audio_data: Audio-Bytes im WAV-Format
            
        Returns:
            Liste von WAV-Chunks
        """
        try:
            # Audio-Bytes in AudioSegment konvertieren
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Nicht-stille Bereiche erkennen
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh
            )
            
            if not nonsilent_ranges:
                return []
            
            chunks = []
            current_chunk_start = nonsilent_ranges[0][0]
            
            for i in range(len(nonsilent_ranges)):
                chunk_end = nonsilent_ranges[i][1]
                next_start = nonsilent_ranges[i+1][0] if i < len(nonsilent_ranges)-1 else None
                
                # Prüfen, ob der aktuelle Chunk die maximale Länge überschreitet
                chunk_length = chunk_end - current_chunk_start
                if chunk_length >= self.max_chunk_length:
                    # Chunk extrahieren und speichern
                    chunk = audio[current_chunk_start:chunk_end]
                    chunks.append(self._segment_to_wav_bytes(chunk))
                    current_chunk_start = chunk_end
                
                # Prüfen, ob eine lange Pause folgt oder es das letzte Segment ist
                elif next_start is None or (next_start - chunk_end) >= self.min_silence_len:
                    if chunk_length >= self.min_chunk_length:
                        # Chunk extrahieren und speichern
                        chunk = audio[current_chunk_start:chunk_end]
                        chunks.append(self._segment_to_wav_bytes(chunk))
                    current_chunk_start = next_start if next_start is not None else chunk_end
            
            return chunks
            
        except Exception as e:
            logger.error(f"Fehler bei der Chunk-Verarbeitung: {str(e)}")
            raise

    def _segment_to_wav_bytes(self, segment: AudioSegment) -> bytes:
        """
        Konvertiert ein AudioSegment in WAV-Bytes.
        """
        buffer = io.BytesIO()
        
        # WAV-Parameter setzen
        wav_file = wave.open(buffer, 'wb')
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(16000)
        
        # Audio-Daten schreiben
        wav_file.writeframes(segment.raw_data)
        wav_file.close()
        
        return buffer.getvalue()

    def is_silence(self, audio_data: bytes, threshold_db: float = -32) -> bool:
        """
        Prüft, ob ein Audio-Chunk hauptsächlich aus Stille besteht.
        
        Args:
            audio_data: Audio-Bytes im WAV-Format
            threshold_db: Schwellenwert in dB für Stille
            
        Returns:
            True wenn der Chunk hauptsächlich Stille enthält
        """
        try:
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            return audio.dBFS < threshold_db
        except Exception as e:
            logger.error(f"Fehler bei der Stilleprüfung: {str(e)}")
            return False 