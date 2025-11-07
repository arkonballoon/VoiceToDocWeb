"""
Unit Tests für Transcriber-Klasse
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

# Entferne transcriber Modul aus sys.modules vor jedem Test
def setup_module():
    """Entfernt transcriber Modul aus sys.modules vor Tests"""
    if 'transcriber' in sys.modules:
        del sys.modules['transcriber']
    if 'src.transcriber' in sys.modules:
        del sys.modules['src.transcriber']

class TestTranscriber:
    """Tests für Transcriber-Klasse"""
    
    def setup_method(self):
        """Wird vor jedem Test aufgerufen - entfernt transcriber Modul"""
        # Entferne transcriber Modul aus sys.modules
        modules_to_remove = [k for k in sys.modules.keys() if 'transcriber' in k]
        for module in modules_to_remove:
            del sys.modules[module]
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_settings):
        """Automatische Mock-Setup für alle Tests"""
        # Mock für whisper Modul
        self.mock_whisper_module = MagicMock()
        self.mock_whisper_model = MagicMock()
        self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
        
        # Mock für OpenAI Client
        self.mock_openai_client = MagicMock()
        self.mock_openai_response = MagicMock()
        self.mock_openai_response.choices = [MagicMock()]
        self.mock_openai_response.choices[0].message.content = "Formatieter Text"
        self.mock_openai_client.chat.completions.create.return_value = self.mock_openai_response
        
        # Mock für torch
        self.mock_torch = MagicMock()
        self.mock_torch.cuda.is_available.return_value = False
        self.mock_torch.cuda.empty_cache = MagicMock()
    
    def test_transcriber_initialization(self, mock_settings):
        """Testet die Initialisierung des Transcribers"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            # Setze return_value vor dem Import
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            from transcriber import Transcriber
            
            transcriber = Transcriber(model_size="tiny")
            
            # Prüfe ob load_model aufgerufen wurde
            assert self.mock_whisper_module.load_model.called
            assert transcriber.model == self.mock_whisper_model
            assert transcriber.device == "cpu"
    
    def test_transcriber_singleton(self, mock_settings):
        """Testet Singleton-Pattern"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            from transcriber import Transcriber
            
            transcriber1 = Transcriber()
            transcriber2 = Transcriber()
            
            # Beide sollten die gleiche Instanz sein
            assert transcriber1 is transcriber2
    
    def test_load_model(self, mock_settings):
        """Testet das Laden des Modells"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            from transcriber import Transcriber
            
            transcriber = Transcriber(model_size="base")
            
            # Prüfe ob load_model mit korrekten Parametern aufgerufen wurde
            call_args = self.mock_whisper_module.load_model.call_args
            assert call_args is not None
            assert call_args[0][0] == "base"
            assert call_args[1]["device"] == "cpu"
    
    def test_reload_model(self, mock_settings):
        """Testet das Neuladen des Modells"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            # Zähle Aufrufe vor reload
            initial_call_count = self.mock_whisper_module.load_model.call_count
            
            # Setze return_value vor reload_model
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            transcriber.reload_model()
            
            # Prüfe ob load_model erneut aufgerufen wurde
            assert self.mock_whisper_module.load_model.call_count > initial_call_count
    
    def test_transcribe_audio_success(self, mock_settings, tmp_path):
        """Testet erfolgreiche Audio-Transkription"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('transcriber.np') as mock_np:
            
            # Setup Mocks
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Mock transcribe Ergebnis
            mock_transcribe_result = {
                "text": "Roher Transkriptionstext",
                "segments": [
                    {"avg_logprob": -0.5},
                    {"avg_logprob": -0.3}
                ]
            }
            self.mock_whisper_model.transcribe.return_value = mock_transcribe_result
            
            # Mock numpy mean
            def numpy_mean(values):
                return float(sum(values) / len(values)) if values else float(0.0)
            mock_np.mean = numpy_mean
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            # Erstelle Test-Audio-Datei
            audio_file = tmp_path / "test.wav"
            audio_file.write_bytes(b"dummy audio")
            
            # Führe Transkription durch
            text, confidence = transcriber.transcribe_audio(audio_file)
            
            # Prüfe Ergebnisse
            assert text == "Formatieter Text"
            # Direkter Vergleich mit Toleranz statt pytest.approx()
            assert abs(confidence - (-0.4)) < 0.01
            
            # Prüfe ob transcribe aufgerufen wurde
            call_args = self.mock_whisper_model.transcribe.call_args
            assert call_args is not None
            assert str(audio_file) in str(call_args[0][0])
    
    def test_transcribe_audio_with_confidence(self, mock_settings, tmp_path):
        """Testet Transkription mit Konfidenz-Berechnung"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('transcriber.np') as mock_np:
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            mock_transcribe_result = {
                "text": "Test Text",
                "segments": [
                    {"avg_logprob": -0.1},
                    {"avg_logprob": -0.2},
                    {"avg_logprob": -0.3}
                ]
            }
            self.mock_whisper_model.transcribe.return_value = mock_transcribe_result
            
            def numpy_mean(values):
                return float(sum(values) / len(values)) if values else float(0.0)
            mock_np.mean = numpy_mean
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            audio_file = tmp_path / "test.wav"
            audio_file.write_bytes(b"dummy audio")
            
            text, confidence = transcriber.transcribe_audio(audio_file)
            
            # Direkter Vergleich mit Toleranz
            expected_confidence = float((-0.1 + -0.2 + -0.3) / 3)
            assert abs(float(confidence) - expected_confidence) < 0.001
    
    def test_transcribe_audio_no_segments(self, mock_settings, tmp_path):
        """Testet Transkription ohne Segmente"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('transcriber.np') as mock_np:
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            mock_transcribe_result = {
                "text": "Test Text"
            }
            self.mock_whisper_model.transcribe.return_value = mock_transcribe_result
            
            def numpy_mean(values):
                return float(sum(values) / len(values)) if values else float(0.0)
            mock_np.mean = numpy_mean
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            audio_file = tmp_path / "test.wav"
            audio_file.write_bytes(b"dummy audio")
            
            text, confidence = transcriber.transcribe_audio(audio_file)
            
            # Konfidenz sollte 0.0 sein wenn keine Segmente vorhanden
            assert abs(float(confidence) - 0.0) < 0.001
    
    def test_transcribe_chunk_success(self, mock_settings):
        """Testet erfolgreiche Chunk-Transkription"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('transcriber.np') as mock_np, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pathlib.Path') as mock_path:
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            mock_transcribe_result = {
                "text": "Chunk Text",
                "segments": [{"avg_logprob": -0.5}]
            }
            self.mock_whisper_model.transcribe.return_value = mock_transcribe_result
            
            def numpy_mean(values):
                return float(sum(values) / len(values)) if values else float(0.0)
            mock_np.mean = numpy_mean
            
            # Mock für Path
            mock_temp_path = MagicMock()
            mock_temp_path.__truediv__ = MagicMock(return_value=mock_temp_path)
            mock_temp_path.unlink = MagicMock()
            mock_path.return_value = mock_temp_path
            
            # Mock für open
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            chunk_data = b"audio chunk data"
            text, confidence = transcriber.transcribe_chunk(chunk_data)
            
            assert text == "Chunk Text"
            # Direkter Vergleich mit Toleranz
            assert abs(float(confidence) - (-0.5)) < 0.01
    
    def test_post_process_transcription_success(self, mock_settings):
        """Testet erfolgreiche Text-Nachbearbeitung"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Setup OpenAI Mock
            self.mock_openai_response.choices[0].message.content = "Formatieter Text"
            self.mock_openai_client.chat.completions.create.return_value = self.mock_openai_response
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            result = transcriber.post_process_transcription("Roher Text")
            
            assert result == "Formatieter Text"
            
            # Prüfe ob OpenAI API aufgerufen wurde
            call_args = self.mock_openai_client.chat.completions.create.call_args
            assert call_args is not None
    
    def test_post_process_transcription_error(self, mock_settings):
        """Testet Fehlerbehandlung bei Text-Nachbearbeitung"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Mock soll Exception werfen
            self.mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            raw_text = "Roher Text"
            result = transcriber.post_process_transcription(raw_text)
            
            # Bei Fehler sollte Originaltext zurückgegeben werden
            assert result == raw_text
    
    def test_post_process_transcription_no_response(self, mock_settings):
        """Testet Fehlerbehandlung bei fehlender API-Antwort"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Mock gibt None zurück
            self.mock_openai_response.choices = []
            self.mock_openai_client.chat.completions.create.return_value = self.mock_openai_response
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            raw_text = "Roher Text"
            result = transcriber.post_process_transcription(raw_text)
            
            # Bei fehlender Antwort sollte Originaltext zurückgegeben werden
            assert result == raw_text
    
    def test_transcribe_audio_error(self, mock_settings, tmp_path):
        """Testet Fehlerbehandlung bei Audio-Transkription"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Mock soll Exception werfen
            self.mock_whisper_model.transcribe.side_effect = Exception("Transcription Error")
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            audio_file = tmp_path / "test.wav"
            audio_file.write_bytes(b"dummy audio")
            
            # Exception sollte weitergegeben werden
            with pytest.raises(Exception) as exc_info:
                transcriber.transcribe_audio(audio_file)
            
            assert "Transcription Error" in str(exc_info.value)
    
    def test_transcribe_chunk_error(self, mock_settings):
        """Testet Fehlerbehandlung bei Chunk-Transkription"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('builtins.open', create=True), \
             patch('pathlib.Path') as mock_path:
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            # Mock für Path
            mock_temp_path = MagicMock()
            mock_temp_path.__truediv__ = MagicMock(return_value=mock_temp_path)
            mock_path.return_value = mock_temp_path
            
            # Mock soll Exception werfen
            self.mock_whisper_model.transcribe.side_effect = Exception("Chunk Error")
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            chunk_data = b"audio chunk data"
            
            # Exception sollte weitergegeben werden
            with pytest.raises(Exception) as exc_info:
                transcriber.transcribe_chunk(chunk_data)
            
            assert "Chunk Error" in str(exc_info.value)
    
    def test_load_model_error(self, mock_settings):
        """Testet Fehlerbehandlung beim Laden des Modells"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch):
            
            # Mock soll Exception werfen
            self.mock_whisper_module.load_model.side_effect = Exception("Model Load Error")
            
            from transcriber import Transcriber
            
            # Exception sollte beim Initialisieren geworfen werden
            with pytest.raises(Exception) as exc_info:
                transcriber = Transcriber()
            
            assert "Model Load Error" in str(exc_info.value)
    
    def test_transcribe_audio_with_previous_text(self, mock_settings, tmp_path):
        """Testet Transkription mit previous_text Parameter"""
        with patch('transcriber.whisper', self.mock_whisper_module), \
             patch('transcriber.OpenAI', return_value=self.mock_openai_client), \
             patch('transcriber.torch', self.mock_torch), \
             patch('transcriber.np') as mock_np:
            
            self.mock_whisper_module.load_model.return_value = self.mock_whisper_model
            
            mock_transcribe_result = {
                "text": "Test Text",
                "segments": [{"avg_logprob": -0.5}]
            }
            self.mock_whisper_model.transcribe.return_value = mock_transcribe_result
            
            def numpy_mean(values):
                return float(sum(values) / len(values)) if values else float(0.0)
            mock_np.mean = numpy_mean
            
            from transcriber import Transcriber
            
            transcriber = Transcriber()
            
            audio_file = tmp_path / "test.wav"
            audio_file.write_bytes(b"dummy audio")
            
            previous_text = "Vorheriger Text"
            text, confidence = transcriber.transcribe_audio(audio_file, previous_text=previous_text)
            
            # Prüfe ob previous_text als initial_prompt übergeben wurde
            call_args = self.mock_whisper_model.transcribe.call_args
            assert call_args is not None
            assert call_args[1]["initial_prompt"] == previous_text
