"""
Unit-Tests für die Transcriber-Klasse
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call, mock_open
import sys

# Import-Pfad anpassen für Tests (falls noch nicht gesetzt)
backend_src = Path(__file__).parent.parent.parent / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Import erst nachdem Mocks gesetzt wurden (in conftest.py)
from transcriber import Transcriber
from utils.singleton import Singleton


class TestTranscriberSingleton:
    """Tests für Singleton-Pattern"""
    
    def test_transcriber_singleton(self, reset_singleton, mock_whisper_model, 
                                   mock_openai_client, mock_torch, mock_settings, mock_logger):
        """Testet, dass das Singleton-Pattern funktioniert"""
        # Zwei Instanzen erstellen
        transcriber1 = Transcriber()
        transcriber2 = Transcriber()
        
        # Verifizieren, dass beide die gleiche Instanz sind
        assert id(transcriber1) == id(transcriber2)
        assert transcriber1 is transcriber2


class TestTranscribeAudio:
    """Tests für transcribe_audio Methode"""
    
    def test_transcribe_audio_success(self, reset_singleton, mock_whisper_model,
                                      mock_openai_client, mock_torch, mock_settings, 
                                      mock_logger, sample_audio_path):
        """Testet erfolgreiche Transkription"""
        transcriber = Transcriber()
        
        # Mock-Whisper-Result konfigurieren
        mock_whisper_model["model"].transcribe.return_value = {
            "text": "  Roher Transkriptionstext  ",
            "segments": [
                {"avg_logprob": -0.5, "text": "Roher"},
                {"avg_logprob": -0.3, "text": "Transkriptionstext"}
            ]
        }
        
        # Mock-OpenAI-Response konfigurieren
        mock_openai_client["response"].choices[0].message.content = "<p>Formatierter Text</p>"
        
        # Transkription durchführen
        text, confidence = transcriber.transcribe_audio(sample_audio_path)
        
        # Verifizieren
        assert text == "<p>Formatierter Text</p>"
        # Durchschnitt von -0.5 und -0.3 = -0.4
        assert abs(confidence - (-0.4)) < 0.001
        mock_whisper_model["model"].transcribe.assert_called_once()
        mock_openai_client["client"].chat.completions.create.assert_called_once()
    
    def test_transcribe_audio_file_not_found(self, reset_singleton, mock_whisper_model,
                                             mock_openai_client, mock_torch, mock_settings,
                                             mock_logger):
        """Testet Fehlerbehandlung bei fehlender Datei"""
        transcriber = Transcriber()
        
        # FileNotFoundError simulieren
        mock_whisper_model["model"].transcribe.side_effect = FileNotFoundError("Datei nicht gefunden")
        
        non_existent_path = Path("/nonexistent/audio.wav")
        
        # Exception sollte weitergegeben werden
        with pytest.raises(FileNotFoundError, match="Datei nicht gefunden"):
            transcriber.transcribe_audio(non_existent_path)
    
    def test_transcribe_audio_invalid_format(self, reset_singleton, mock_whisper_model,
                                             mock_openai_client, mock_torch, mock_settings,
                                             mock_logger, sample_audio_path):
        """Testet Fehlerbehandlung bei ungültigem Audio-Format"""
        transcriber = Transcriber()
        
        # ValueError für ungültiges Format simulieren
        mock_whisper_model["model"].transcribe.side_effect = ValueError("Ungültiges Audio-Format")
        
        # Exception sollte weitergegeben werden
        with pytest.raises(ValueError, match="Ungültiges Audio-Format"):
            transcriber.transcribe_audio(sample_audio_path)


class TestTranscribeChunk:
    """Tests für transcribe_chunk Methode"""
    
    def test_transcribe_chunk(self, reset_singleton, mock_whisper_model,
                              mock_openai_client, mock_torch, mock_settings,
                              mock_logger, tmp_path):
        """Testet Chunk-Transkription ohne LLM-Nachbearbeitung"""
        transcriber = Transcriber()
        
        # Mock-Whisper-Result für Chunk
        mock_whisper_model["model"].transcribe.return_value = {
            "text": "  Chunk Text  ",
            "segments": [
                {"avg_logprob": -0.4, "text": "Chunk"},
                {"avg_logprob": -0.2, "text": "Text"}
            ]
        }
        
        # Temporäres Verzeichnis für Chunk-Datei erstellen
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Mock Path("temp") um auf unser temporäres Verzeichnis zu zeigen
        def mock_path_constructor(path_str):
            if path_str == "temp":
                return temp_dir
            return Path(path_str)
        
        # Audio-Chunk-Daten
        audio_chunk = b"fake audio chunk data"
        
        # Mock Path-Konstruktor in transcriber-Modul
        with patch("transcriber.Path", side_effect=lambda x: mock_path_constructor(x) if isinstance(x, str) else Path(x)):
            # Chunk-Transkription durchführen
            text, confidence = transcriber.transcribe_chunk(audio_chunk)
        
        # Verifizieren
        assert text == "Chunk Text"  # Strip angewendet
        # Durchschnitt von -0.4 und -0.2 = -0.3
        assert abs(confidence - (-0.3)) < 0.001
        mock_whisper_model["model"].transcribe.assert_called_once()
        
        # Verifizieren, dass keine LLM-Nachbearbeitung stattfindet
        mock_openai_client["client"].chat.completions.create.assert_not_called()


class TestPostProcessTranscription:
    """Tests für post_process_transcription Methode"""
    
    def test_post_process_transcription_success(self, reset_singleton, mock_whisper_model,
                                                mock_openai_client, mock_torch, mock_settings,
                                                mock_logger):
        """Testet erfolgreiche LLM-Nachbearbeitung"""
        transcriber = Transcriber()
        
        # Mock-OpenAI-Response konfigurieren
        mock_openai_client["response"].choices[0].message.content = "<p>Formatierter Text mit Absätzen</p>"
        
        raw_text = "Roher Text ohne Formatierung"
        processed_text = transcriber.post_process_transcription(raw_text)
        
        # Verifizieren
        assert processed_text == "<p>Formatierter Text mit Absätzen</p>"
        mock_openai_client["client"].chat.completions.create.assert_called_once()
    
    def test_post_process_transcription_timeout(self, reset_singleton, mock_whisper_model,
                                                mock_openai_client, mock_torch, mock_settings,
                                                mock_logger):
        """Testet Timeout-Handling bei LLM"""
        transcriber = Transcriber()
        
        # TimeoutError simulieren
        import asyncio
        mock_openai_client["client"].chat.completions.create.side_effect = asyncio.TimeoutError("Timeout")
        
        raw_text = "Roher Text"
        processed_text = transcriber.post_process_transcription(raw_text)
        
        # Verifizieren, dass Originaltext zurückgegeben wird
        assert processed_text == raw_text
    
    def test_post_process_transcription_fallback(self, reset_singleton, mock_whisper_model,
                                                  mock_openai_client, mock_torch, mock_settings,
                                                  mock_logger):
        """Testet Fallback auf Originaltext bei LLM-Fehler"""
        transcriber = Transcriber()
        
        # Generische Exception simulieren
        mock_openai_client["client"].chat.completions.create.side_effect = Exception("API-Fehler")
        
        raw_text = "Roher Text"
        processed_text = transcriber.post_process_transcription(raw_text)
        
        # Verifizieren, dass Originaltext zurückgegeben wird
        assert processed_text == raw_text
    
    def test_post_process_transcription_empty_response(self, reset_singleton, mock_whisper_model,
                                                      mock_openai_client, mock_torch, mock_settings,
                                                      mock_logger):
        """Testet Fallback bei leerer LLM-Antwort"""
        transcriber = Transcriber()
        
        # Leere Response simulieren
        mock_openai_client["response"].choices = []
        
        raw_text = "Roher Text"
        processed_text = transcriber.post_process_transcription(raw_text)
        
        # Verifizieren, dass Originaltext zurückgegeben wird
        assert processed_text == raw_text


class TestReloadModel:
    """Tests für reload_model Methode"""
    
    def test_reload_model(self, reset_singleton, mock_whisper_model,
                         mock_openai_client, mock_torch, mock_settings,
                         mock_logger):
        """Testet Modell-Neuladen"""
        transcriber = Transcriber()
        
        # Initiales Modell sollte geladen sein
        assert transcriber.model is not None
        
        # Reload durchführen
        transcriber.reload_model()
        
        # Verifizieren, dass load_model aufgerufen wurde
        assert mock_whisper_model["load_model"].call_count >= 2  # Einmal bei Init, einmal bei Reload


class TestConfidenceCalculation:
    """Tests für Konfidenz-Berechnung"""
    
    def test_confidence_calculation(self, reset_singleton, mock_whisper_model,
                                   mock_openai_client, mock_torch, mock_settings,
                                   mock_logger, sample_audio_path):
        """Testet Konfidenz-Berechnung aus Segmenten"""
        transcriber = Transcriber()
        
        # Mock-Whisper-Result mit verschiedenen Log-Wahrscheinlichkeiten
        mock_whisper_model["model"].transcribe.return_value = {
            "text": "Test Text",
            "segments": [
                {"avg_logprob": -0.6, "text": "Test"},
                {"avg_logprob": -0.4, "text": "Text"},
                {"avg_logprob": -0.2, "text": "Ende"}
            ]
        }
        
        # Mock-OpenAI-Response
        mock_openai_client["response"].choices[0].message.content = "Formatierter Text"
        
        # Transkription durchführen
        text, confidence = transcriber.transcribe_audio(sample_audio_path)
        
        # Verifizieren, dass Konfidenz korrekt berechnet wurde
        # Durchschnitt von -0.6, -0.4, -0.2 = -0.4
        expected_confidence = sum([-0.6, -0.4, -0.2]) / len([-0.6, -0.4, -0.2])
        assert abs(confidence - expected_confidence) < 0.001
    
    def test_confidence_calculation_no_segments(self, reset_singleton, mock_whisper_model,
                                               mock_openai_client, mock_torch, mock_settings,
                                               mock_logger, sample_audio_path):
        """Testet Konfidenz-Berechnung ohne Segmente"""
        transcriber = Transcriber()
        
        # Mock-Whisper-Result ohne Segmente
        mock_whisper_model["model"].transcribe.return_value = {
            "text": "Test Text"
        }
        
        # Mock-OpenAI-Response
        mock_openai_client["response"].choices[0].message.content = "Formatierter Text"
        
        # Transkription durchführen
        text, confidence = transcriber.transcribe_audio(sample_audio_path)
        
        # Verifizieren, dass Konfidenz 0.0 ist wenn keine Segmente vorhanden
        assert confidence == 0.0
    
    def test_confidence_calculation_empty_segments(self, reset_singleton, mock_whisper_model,
                                                   mock_openai_client, mock_torch, mock_settings,
                                                   mock_logger, sample_audio_path):
        """Testet Konfidenz-Berechnung mit leeren Segmenten"""
        transcriber = Transcriber()
        
        # Mock-Whisper-Result mit leeren Segmenten
        mock_whisper_model["model"].transcribe.return_value = {
            "text": "Test Text",
            "segments": []
        }
        
        # Mock-OpenAI-Response
        mock_openai_client["response"].choices[0].message.content = "Formatierter Text"
        
        # Transkription durchführen
        text, confidence = transcriber.transcribe_audio(sample_audio_path)
        
        # Verifizieren, dass Konfidenz 0.0 ist
        assert confidence == 0.0

