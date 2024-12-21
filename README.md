# Audio Transkription & Template Manager

Ein Projekt zur Demonstration von CHOP (Chat Oriented Programming) - entwickelt mit Vue.js und FastAPI.

## ⚠️ Wichtiger Hinweis

Dieses Projekt dient ausschließlich zu Testzwecken und zur Demonstration der CHOP-Entwicklungsmethodik. Es wird keine Gewährleistung für die Funktionalität, Sicherheit oder Eignung für einen bestimmten Zweck übernommen.

**Haftungsausschluss:**
- Die Nutzung erfolgt auf eigenes Risiko
- Keine Garantie für die Richtigkeit der Transkriptionen
- Keine Gewährleistung für die Datensicherheit
- Nicht für den produktiven Einsatz geeignet

## Was ist CHOP?

CHOP (Chat Oriented Programming) ist ein experimenteller Ansatz zur Softwareentwicklung, bei dem der Entwicklungsprozess durch einen strukturierten Dialog mit einem KI-Assistenten gesteuert wird. 

Hauptmerkmale:
- Iterative Entwicklung durch Chat-basierte Kommunikation
- Schnelle Prototypen-Entwicklung
- Dokumentationsgetriebene Entwicklung
- Kontinuierliche Code-Reviews durch KI

## Features

- Audio-Transkription (MP3, WAV, WebM)
- Live-Audioe mit Echtzeit-Transkription
 Template-Verwaltung für Textbausteine
 Rich-Text-Editor für Transkriptionen
 Template-basierte Textverarbeitung mit GPT-4
 Responsive Design
 Docker-Support für einfache Deployment
 Automatische Modellauswahl (CPU/CUDA)
 Konfigurierbare Whisper-Modelle
 Fortschrittsanzeige bei der Verarbeitung

## Technologie-Stack

- Frontend: Vue.js 3, Vue Router, Vue Quill, Pinia
 Backend: FastAPI, Whisper, OpenAI
 Container: Docker, Docker Compose
 API: REST + WebSocket für Live-Streaming

## Voraussetzungen

- Docker und Docker Compose
 OpenAI API Key für Template-Verarbeitung
 NVIDIA GPU (optional) für beschleunigte Transkription

## Installation und Setup

### Repository klonen

```bash
git clone https://github.com/arkonballoon/VoiceToDocWeb.git
cd VoiceToDocWeb
```

### Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```
OpenAI API Key in .env eintragen

### Container starten

```bash
docker-compose up -d
Frontend: http://localhost:3000
Backend API: http://localhost:8000
```
## Manuelles Starten
### Backend

```bash
# Python Virtual Environment erstellen und aktivieren
python -m venv venv
source venv/bin/activate # Unter Windows: venv\Scripts\activate
# In das Backend-Verzeichnis wechseln
cd backend
# Python-Abhängigkeiten installieren
pip install -r requirements.txt
# PyTorch Installation (optional, wenn nicht in requirements.txt)
bash ../install_pytorch.sh
# Umgebungsvariablen konfigurieren
cp .env.example .env
# Fügen Sie Ihren OpenAI API Key in .env ein

# Backend-Server starten
cd src
uvicorn main:app --reload
```

Der Backend-Server läuft dann unter `http://localhost:8000`

```bash
# In das Frontend-Verzeichnis wechseln
cd frontend
# NPM-Abhängigkeiten installieren
npm install
# Development-Server starten
npm run dev
```
Der Frontend-Server läuft dann unter `http://localhost:3000`

Beide Server müssen parallel laufen, damit die Anwendung funktioniert. 

## Entwicklung

Das Projekt verwendet:
- ESLint und Prettier für Code-Formatierung
- Vue Router für Navigation
- Pinia für State Management
- Vue Quill für Rich-Text-Bearbeitung
- FastAPI für RESTful API und WebSocket
- Whisper für Spracherkennung
- OpenAI GPT-4 für Template-Verarbeitung
- Docker für Containerisierung
- WebRTC für Audio-Streaming
- Cursor.ai als IDE
- Claude-3.5 als KI-Assistent

## Konfiguration

Die Anwendung kann über die Web-Oberfläche oder die `config.json` konfiguriert werden:
- Whisper-Modellgröße (tiny bis large-v3)
- Audio-Parameter (Silence Detection, Chunk Size)
- Worker-Anzahl für parallele Verarbeitung
- GPU/CPU Modellauswahl
- Template-Verarbeitung Parameter

Entwickelt als Proof of Concept für CHOP (Chat Oriented Programming)