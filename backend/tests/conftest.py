"""
Pytest Konfiguration und Fixtures für Backend-Tests
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Füge src-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_settings():
    """Mock für Settings-Klasse"""
    with patch('config.settings') as mock:
        mock.LLM_API_KEY = "test-key"
        mock.WHISPER_MODEL = "tiny"
        mock.DB_TYPE = "sqlite"
        mock.DB_PATH = ":memory:"
        yield mock

@pytest.fixture
def temp_dir(tmp_path):
    """Temporäres Verzeichnis für Tests"""
    return tmp_path / "test_data"

@pytest.fixture
def sample_audio_file(tmp_path):
    """Erstellt eine Dummy-Audio-Datei für Tests"""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_bytes(b"dummy audio data")
    return audio_file

