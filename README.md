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
- Template-Verwaltung für Textbausteine
- Rich-Text-Editor für Transkriptionen
- Template-basierte Textverarbeitung
- Responsive Design

## Technologie-Stack

- Frontend: Vue.js 3, Vue Router, Vue Quill, Pinia
- Backend: FastAPI, SQLAlchemy, OpenAI
- Datenbank: SQLite
- API: REST

## Voraussetzungen

- Python 3.10 oder höher
- Node.js 18 oder höher
- OpenAI API Key für Template-Verarbeitung

## Installation und Setup

### Repository klonen

```bash
git clone https://github.com/arkonballoon/VoiceToDocWeb.git
```

## Backend
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
- FastAPI für RESTful API
- SQLAlchemy für Datenbankoperationen
- OpenAI für Template-Verarbeitung
- Cursor.ai als IDE
- Claude-3.5 als KI-Assistent

Entwickelt als Proof of Concept für CHOP (Chat Oriented Programming)