"""
Gemeinsame Fixtures und Mock-Setup für alle Tests
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
import sys


def pytest_configure(config):
    """Wird vor dem Import der Test-Module aufgerufen - setzt Mocks früh"""
    # Import-Pfad anpassen
    backend_src = Path(__file__).parent.parent / "src"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))
    
    # Mocks für externe Dependencies setzen, bevor Tests importiert werden
    # Diese werden in den Fixtures überschrieben, aber verhindern Import-Fehler
    if "whisper" not in sys.modules:
        mock_whisper = MagicMock()
        # Mock load_model Funktion
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "", "segments": []}
        mock_whisper.load_model = MagicMock(return_value=mock_model)
        sys.modules["whisper"] = mock_whisper
    
    # Mock torch vor Import
    if "torch" not in sys.modules:
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.cuda.empty_cache = MagicMock()
        sys.modules["torch"] = mock_torch
    
    # Mock numpy vor Import (falls verwendet)
    if "numpy" not in sys.modules:
        mock_numpy = MagicMock()
        # Mock np.mean für Konfidenz-Berechnung
        mock_numpy.mean = lambda x: sum(x) / len(x) if x else 0.0
        sys.modules["numpy"] = mock_numpy
    
    # Mock openai vor Import
    if "openai" not in sys.modules:
        mock_openai = MagicMock()
        # Mock OpenAI-Klasse
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI = MagicMock(return_value=mock_client)
        sys.modules["openai"] = mock_openai


@pytest.fixture
def mock_whisper_model(monkeypatch):
    """Mock für Whisper-Modell und load_model-Funktion"""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "text": "Test Transkription",
        "segments": [
            {"avg_logprob": -0.5, "text": "Test"},
            {"avg_logprob": -0.3, "text": "Transkription"}
        ]
    }
    
    # Mock whisper.load_model
    import transcriber
    original_load_model = getattr(transcriber.whisper, 'load_model', None)
    transcriber.whisper.load_model = MagicMock(return_value=mock_model)
    
    yield {
        "model": mock_model,
        "load_model": transcriber.whisper.load_model
    }
    
    # Restore original
    if original_load_model:
        transcriber.whisper.load_model = original_load_model


@pytest.fixture
def mock_openai_client(monkeypatch):
    """Mock für OpenAI-Client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "<p>Formatierter Text</p>"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock OpenAI-Klasse
    import transcriber
    original_openai = getattr(transcriber, 'OpenAI', None)
    transcriber.OpenAI = MagicMock(return_value=mock_client)
    
    yield {
        "client": mock_client,
        "openai_class": transcriber.OpenAI,
        "response": mock_response
    }
    
    # Restore original
    if original_openai:
        transcriber.OpenAI = original_openai


@pytest.fixture
def mock_torch(monkeypatch):
    """Mock für torch und CUDA-Funktionen"""
    import transcriber
    original_torch = getattr(transcriber, 'torch', None)
    
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.cuda.empty_cache = MagicMock()
    transcriber.torch = mock_torch
    
    yield mock_torch
    
    # Restore original
    if original_torch:
        transcriber.torch = original_torch


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock für config.settings"""
    import transcriber
    original_settings = getattr(transcriber, 'settings', None)
    
    mock_settings = MagicMock()
    mock_settings.WHISPER_MODEL = "base"
    mock_settings.WHISPER_DEVICE_CUDA = "large-v3"
    mock_settings.LLM_API_KEY = "test-api-key"
    mock_settings.LLM_MODEL_LIGHT = "gpt-4o-mini"
    transcriber.settings = mock_settings
    
    yield mock_settings
    
    # Restore original
    if original_settings:
        transcriber.settings = original_settings


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock für utils.logger"""
    import transcriber
    original_logger = getattr(transcriber, 'logger', None)
    
    mock_logger = MagicMock()
    transcriber.logger = mock_logger
    
    yield mock_logger
    
    # Restore original
    if original_logger:
        transcriber.logger = original_logger


@pytest.fixture
def reset_singleton():
    """Fixture zum Zurücksetzen des Singleton vor/nach jedem Test"""
    import sys
    from pathlib import Path
    
    # Import-Pfad anpassen
    backend_src = Path(__file__).parent.parent / "src"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))
    
    from transcriber import Transcriber
    from utils.singleton import Singleton
    
    # Vor dem Test: Singleton zurücksetzen
    if Transcriber in Singleton._instances:
        del Singleton._instances[Transcriber]
    if Transcriber in Singleton._initialized:
        del Singleton._initialized[Transcriber]
    
    yield
    
    # Nach dem Test: Singleton wieder zurücksetzen
    if Transcriber in Singleton._instances:
        del Singleton._instances[Transcriber]
    if Transcriber in Singleton._initialized:
        del Singleton._initialized[Transcriber]


@pytest.fixture
def sample_audio_path(tmp_path):
    """Erstellt eine temporäre Audio-Datei für Tests"""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_bytes(b"fake audio data")
    return audio_file

