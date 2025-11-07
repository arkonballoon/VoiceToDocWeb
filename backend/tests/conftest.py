"""
Pytest Konfiguration und Fixtures für Backend-Tests
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

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

@pytest.fixture
def mock_numpy():
    """Mock für numpy mit korrigierter mean-Funktion"""
    with patch('numpy', create=True) as mock_np:
        def numpy_mean(values):
            """Mock für np.mean() der explizit float() zurückgibt"""
            if not values:
                return float(0.0)
            # Simuliere numpy.mean() Verhalten, gibt aber Python float zurück
            return float(sum(values) / len(values))
        
        mock_np.mean = numpy_mean
        mock_np.array = MagicMock()
        yield mock_np

