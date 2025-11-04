# Projektstruktur VoiceToDoc

Diese Dokumentation beschreibt die Struktur des VoiceToDoc-Projekts und erläutert wichtige Design-Entscheidungen.

## Übersicht

```
VoiceToDocWeb/
├── backend/              # FastAPI Backend
├── frontend/             # Vue.js Frontend
├── docker-compose.yml    # Entwicklung
├── docker-compose.prod.* # Produktion
└── deploy-*.sh           # Deployment-Skripte
```

## Backend-Struktur

```
backend/
├── Dockerfile            # Container-Image Definition
├── install_pytorch.sh    # PyTorch Installation (für lokale Entwicklung)
├── requirements.txt      # Python-Abhängigkeiten
├── .env.example          # Umgebungsvariablen-Vorlage
├── .env                  # Lokale Umgebungsvariablen (nicht im Repo)
├── data/                 # Produktions-Daten (für Docker Volumes)
│   └── templates/        # Template-Dateien
└── src/                  # Quellcode
    ├── main.py           # FastAPI App & Endpunkte
    ├── config.py         # Konfigurationsmanagement
    ├── transcriber.py    # Whisper-Integration
    ├── audio_processor.py # Audio-Verarbeitung
    ├── queue_manager.py  # Transkriptions-Queue
    ├── data/             # Development-Daten
    │   ├── config.json   # App-Konfiguration
    │   ├── logs/         # Log-Dateien
    │   ├── temp/         # Temporäre Dateien
    │   └── templates/    # Template-Dateien
    ├── models/           # Datenmodelle
    │   └── template.py   # Template-Modell
    ├── services/         # Business-Logik
    │   ├── template_service.py
    │   └── template_processor.py
    ├── storage/          # Storage-Adapter (Pattern)
    │   ├── storage_adapter.py
    │   ├── filesystem_adapter.py
    │   ├── sql_adapter.py
    │   └── storage_factory.py
    ├── database/        # Datenbank-Verbindung
    │   ├── connection.py
    │   └── models.py
    └── utils/            # Hilfsfunktionen
        ├── logger.py
        ├── exceptions.py
        └── singleton.py
```

### Wichtige Design-Entscheidungen

#### Data-Verzeichnisse

Es gibt zwei Data-Verzeichnisse aus gutem Grund:

1. **`backend/src/data/`** - Für lokale Entwicklung
   - Wird im Development-Mode verwendet
   - Pfad im Code: `BASE_DIR / "src" / "data"`
   - Wird von Docker als Volume gemountet: `./backend/src:/app/src`

2. **`backend/data/`** - Für Docker Volumes (Produktion)
   - Wird in Docker-Containern verwendet
   - Pfad im Container: `/app/data`
   - Wird als separates Volume gemountet: `./backend/data/templates:/app/data/templates`
   - Persistiert Daten über Container-Neustarts hinweg

**Im Code verwendet:** `/app/data/` (Container-Pfad, siehe `main.py` Zeile 28-30)

#### Konfiguration

- **`config.py`**: Zentrale Konfiguration mit Pydantic Settings
- **`.env`**: Umgebungsvariablen (sensible Daten, nicht im Repo)
- **`.env.example`**: Vorlage für .env (im Repo)
- **`src/data/config.json`**: Persistierte Konfiguration (optional)

#### Storage-Adapter Pattern

Flexible Storage-Abstraktion:
- **FilesystemAdapter**: Speichert Templates als JSON-Dateien
- **SQLAdapter**: Speichert Templates in Datenbank (SQLite/PostgreSQL/MySQL)
- **StorageFactory**: Erstellt Adapter basierend auf Konfiguration

## Frontend-Struktur

```
frontend/
├── Dockerfile            # Development Container
├── Dockerfile.prod       # Production Container (optimiert)
├── package.json          # NPM-Abhängigkeiten
├── vite.config.js        # Vite-Konfiguration
├── .env.example          # Umgebungsvariablen-Vorlage (optional)
├── public/               # Statische Assets
│   ├── icons/            # PWA Icons
│   ├── manifest.json     # PWA Manifest
│   └── index.html
└── src/
    ├── main.js           # App-Einstiegspunkt
    ├── App.vue           # Root-Komponente
    ├── config.js         # Konfiguration (Backend-URL, etc.)
    ├── style.css         # Globale Styles
    ├── router/           # Vue Router
    │   └── index.js
    ├── stores/           # Pinia State Management
    │   └── transcription.js
    ├── services/         # API-Services
    │   └── api.js        # Zentrale API-Klasse
    ├── components/       # Wiederverwendbare Komponenten
    │   ├── TranscriptionService.vue
    │   ├── TemplateManager.vue
    │   ├── InstallPrompt.vue
    │   └── NetworkStatus.vue
    └── views/            # Seiten-Komponenten
        ├── TranscriptionView.vue
        ├── TemplateProcessingView.vue
        └── ConfigurationView.vue
```

### Frontend-Architektur

- **Config.js**: Zentrale Konfiguration mit automatischer Erkennung
  - Entwickelt automatisch Backend-URL (localhost:8000 vs. Produktion)
  - Unterstützt lokale Entwicklung und Production-Traefik-Routing

- **Services**: API-Service-Klasse für alle Backend-Kommunikation
  - Einheitliche Fehlerbehandlung
  - Timeout-Management
  - WebSocket-Service

- **Stores**: Pinia für State Management
  - Transcription-Store für Transkriptions-Daten

- **Mobile-Features**: Optimierte UI für mobile Geräte
  - Live-Transkript-Anzeige während Aufnahme
  - Auto-Scroll zum Ende
  - Computed Properties für reaktive Updates
  - Template-optional für einfache Transkription

## Deployment-Struktur

### Entwicklung
- `docker-compose.yml`: Lokale Entwicklung mit Hot-Reload
- Volumes für Source-Code für schnelle Iteration

### Produktion
- `docker-compose.prod.images.yml`: Verwendet vorgebaute Images
- `docker-compose.prod.yml`: Baut Images lokal
- `deploy-*.sh`: Deployment-Skripte für verschiedene Szenarien

## Umgebungsvariablen

### Backend (.env)

**Erforderlich:**
- `LLM_API_KEY`: OpenAI API-Schlüssel

**Optional:**
- `WHISPER_MODEL`: Whisper-Modell (tiny bis large-v3)
- `DB_TYPE`: Datenbank-Typ (sqlite, postgresql, mysql)
- `STORAGE_TYPE`: Storage-Typ (sql, filesystem)
- Siehe `backend/.env.example` für vollständige Liste

### Frontend (.env)

**Optional** - Meist nicht nötig, da automatisch erkannt:
- `VITE_BACKEND_URL`: Spezifische Backend-URL
- `VITE_WS_HEARTBEAT_INTERVAL`: WebSocket-Heartbeat
- Siehe `frontend/.env.example` für vollständige Liste

## Testing (Zukünftig)

```
backend/tests/
├── conftest.py
├── unit/
│   ├── test_transcriber.py
│   └── test_audio_processor.py
└── integration/
    └── test_api.py

frontend/tests/
├── unit/
│   └── components/
└── e2e/ (optional)
```

## Verbesserungsvorschläge (TODO)

1. ✅ .env.example Dateien hinzugefügt
2. ✅ Root-Verzeichnis aufgeräumt (install_pytorch.sh verschoben)
3. ✅ Tests einrichten (pytest für Backend, Vitest vorbereitet für Frontend)
4. ✅ GitHub-Workflow eingerichtet (Issue Templates, PR Template, Contributing)
5. ⏳ API-Routen in separate Dateien auslagern
6. ⏳ Composables für Frontend hinzufügen
7. ⏳ CI/CD Pipeline einrichten
8. ✅ Mobile-Transkript-Anzeige implementiert

## Wichtige Pfade

### Backend
- Code: `/app/src/` (Container)
- Daten: `/app/data/` (Container)
- Logs: `/app/data/logs/`
- Templates: `/app/data/templates/`
- Temp: `/app/data/temp/`

### Frontend
- Build: `frontend/dist/`
- Public: `frontend/public/`
- Source: `frontend/src/`

