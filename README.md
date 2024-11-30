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
- Markdown-Editor für Templates
- Echtzeit-Vorschau
- Responsive Design

## Technologie-Stack

- Frontend: Vue.js 3, Vue Router, MD Editor V3
- Backend: FastAPI, SQLAlchemy
- Datenbank: SQLite
- API: REST

---

# Installation und Setup

## Repository klonen

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
Der Frontend-Server läuft dann unter `http://localhost:5173`

Beide Server müssen parallel laufen, damit die Anwendung funktioniert. 

Entwickelt als Proof of Concept für CHOP (Chat Oriented Programming)
