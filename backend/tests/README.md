# Backend Tests

Dieses Verzeichnis enthält Tests für das VoiceToDoc Backend.

## Struktur

```
tests/
├── conftest.py          # Pytest-Konfiguration und gemeinsame Fixtures
├── unit/                # Unit Tests
│   └── test_transcriber.py
└── integration/         # Integration Tests (TODO)
```

## Ausführen

```bash
# Alle Tests
pytest

# Nur Unit Tests
pytest tests/unit/

# Mit Coverage
pytest --cov=src --cov-report=html

# Nur schnelle Tests (ohne @pytest.mark.slow)
pytest -m "not slow"
```

## Hinweise

- **Langsame Tests** (z.B. mit echten Whisper-Modellen) sollten mit `@pytest.mark.slow` markiert werden
- **Fixtures** in `conftest.py` sind für alle Tests verfügbar
- **Mocks** sollten für externe Dependencies verwendet werden (OpenAI API, Whisper, etc.)

## TODO

- [ ] Vollständige Transcriber-Tests
- [ ] Audio-Processor-Tests
- [ ] Template-Service-Tests
- [ ] API-Endpoint-Tests (Integration)
- [ ] WebSocket-Tests

