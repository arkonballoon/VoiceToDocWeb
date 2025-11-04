# Konfigurationsanleitung

## Übersicht

Diese Anleitung erklärt, wie Sie die VoiceToDoc-Anwendung für verschiedene Umgebungen konfigurieren.

## Umgebungsvariablen

### Frontend (.env)

**Hinweis:** Die Frontend-Konfiguration ist meist nicht erforderlich, da die Backend-URL automatisch erkannt wird. Erstellen Sie eine `.env`-Datei nur, wenn Sie spezifische Einstellungen benötigen:

```bash
# Backend-Verbindung (optional - wird automatisch erkannt)
# VITE_BACKEND_URL=localhost:8000
# VITE_PROTOCOL=http
# VITE_WS_PROTOCOL=ws

# WebSocket-Konfiguration (optional)
# VITE_WS_HEARTBEAT_INTERVAL=30000
# VITE_WS_MAX_RECONNECT_ATTEMPTS=3
# VITE_WS_RECONNECT_DELAY=5000

# Audio-Konfiguration (optional)
# VITE_MAX_FILE_SIZE=52428800
# VITE_AUDIO_CHUNK_SIZE=5000
# VITE_AUDIO_SAMPLE_RATE=16000

# UI-Konfiguration (optional)
# VITE_THEME=light
# VITE_LANGUAGE=de
# VITE_AUTO_SAVE_INTERVAL=30000
```

**Einfachste Methode:** Kopieren Sie `frontend/.env.example` zu `frontend/.env` und kommentieren Sie die Zeilen aus, die Sie nicht benötigen.

### Backend (.env)

Erstellen Sie eine `.env`-Datei im `backend/`-Verzeichnis:

```bash
# API-Schlüssel (erforderlich)
LLM_API_KEY=your_openai_api_key_here

# CORS-Konfiguration
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://frontend:3000"]

# Datenbank-Konfiguration
DB_TYPE=sqlite
DB_PATH=data/templates.db

# Logging
LOG_LEVEL=20
SQL_DEBUG=false

# Audio-Verarbeitung
AUDIO_MIN_SILENCE_LEN=500
AUDIO_SILENCE_THRESH=-32
AUDIO_MIN_CHUNK_LENGTH=2000
AUDIO_MAX_CHUNK_LENGTH=5000

# Whisper-Konfiguration
WHISPER_MODEL=base
WHISPER_DEVICE_CUDA=large-v3
MAX_WORKERS=3
```

## Verschiedene Umgebungen

### Lokale Entwicklung

1. **Backend-Konfiguration**:
   ```bash
   cd backend
   cp .env.example .env
   # Bearbeiten Sie .env mit Ihren Einstellungen
   ```

2. **Frontend-Konfiguration**:
   ```bash
   cd frontend
   cp .env.example .env
   # Bearbeiten Sie .env mit Ihren Einstellungen
   ```

3. **Starten**:
   ```bash
   # Backend
   cd backend
   uvicorn src.main:app --reload

   # Frontend (in neuem Terminal)
   cd frontend
   npm run dev
   ```

### Docker-Entwicklung

1. **Konfiguration**:
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Bearbeiten Sie backend/.env

   # Frontend
   cp frontend/.env.example frontend/.env
   # Bearbeiten Sie frontend/.env
   ```

2. **Starten**:
   ```bash
   docker-compose up --build
   ```

### Produktionsumgebung

1. **Backend-Konfiguration**:
   ```bash
   # Produktions-spezifische Einstellungen
   ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
   LOG_LEVEL=30
   SQL_DEBUG=false
   ```

2. **Frontend-Konfiguration**:
   ```bash
   # Produktions-spezifische Einstellungen
   VITE_BACKEND_URL=api.yourdomain.com
   VITE_PROTOCOL=https
   VITE_WS_PROTOCOL=wss
   ```

3. **Docker-Produktion**:
   ```bash
   # Produktions-Dockerfile verwenden
   docker-compose -f docker-compose.prod.yml up --build
   ```

## Konfigurationsoptionen

### Backend-Konfiguration

| Variable | Beschreibung | Standard | Beispiel |
|----------|--------------|----------|----------|
| `LLM_API_KEY` | OpenAI API-Schlüssel | - | `sk-...` |
| `ALLOWED_ORIGINS` | Erlaubte CORS-Origins | `["http://localhost:3000"]` | `["https://app.com"]` |
| `DB_TYPE` | Datenbanktyp | `sqlite` | `postgresql` |
| `WHISPER_MODEL` | Whisper-Modell | `base` | `large-v3` |
| `MAX_WORKERS` | Maximale Worker-Anzahl | `3` | `5` |

### Frontend-Konfiguration

| Variable | Beschreibung | Standard | Beispiel |
|----------|--------------|----------|----------|
| `VITE_BACKEND_URL` | Backend-URL | `localhost:8000` | `api.example.com` |
| `VITE_PROTOCOL` | HTTP-Protokoll | `http` | `https` |
| `VITE_WS_PROTOCOL` | WebSocket-Protokoll | `ws` | `wss` |
| `VITE_MAX_FILE_SIZE` | Maximale Dateigröße | `52428800` | `104857600` |
| `VITE_THEME` | UI-Theme | `light` | `dark` |

## Sicherheitshinweise

1. **API-Schlüssel**: Niemals API-Schlüssel in den Code committen
2. **CORS**: Nur notwendige Origins erlauben
3. **Umgebungsvariablen**: Verwenden Sie `.env`-Dateien für sensible Daten
4. **Produktion**: Verwenden Sie HTTPS/WSS in der Produktion

## Troubleshooting

### Häufige Probleme

1. **CORS-Fehler**:
   - Überprüfen Sie `ALLOWED_ORIGINS` im Backend
   - Stellen Sie sicher, dass die Frontend-URL korrekt ist

2. **WebSocket-Verbindungsfehler**:
   - Überprüfen Sie `VITE_WS_PROTOCOL` und `VITE_BACKEND_URL`
   - Stellen Sie sicher, dass der Backend-Server läuft

3. **API-Verbindungsfehler**:
   - Überprüfen Sie `VITE_BACKEND_URL` und `VITE_PROTOCOL`
   - Testen Sie die Backend-API direkt

### Debug-Modus

Aktivieren Sie den Debug-Modus für detaillierte Logs:

```bash
# Backend
LOG_LEVEL=10
SQL_DEBUG=true

# Frontend (in der Browser-Konsole)
localStorage.setItem('debug', 'true')
```

## Weitere Informationen

- [Backend-API-Dokumentation](http://localhost:8000/docs)
- [Frontend-Konfiguration](frontend/src/config.js)
- [Backend-Konfiguration](backend/src/config.py)
