Here is the English translation of your document:

---

# Audio Transcription & Template Manager

A project to demonstrate CHOP (Chat Oriented Programming) - developed with Vue.js and FastAPI.

## ⚠️ Important Note

This project is for testing purposes only and to demonstrate the CHOP development methodology. No warranty is provided for functionality, security, or suitability for any specific purpose.

**Disclaimer:**
- Use at your own risk
- No guarantee for transcription accuracy
- No warranty for data security
- Not suitable for production use

## What is CHOP?

CHOP (Chat Oriented Programming) is an experimental approach to software development, where the development process is guided through a structured dialogue with an AI assistant.

Key features:
- Iterative development through chat-based communication
- Rapid prototyping
- Documentation-driven development
- Continuous code reviews by AI

## Features

- Audio transcription (MP3, WAV, WebM)
- Live audio recording with real-time transcription
- Template management for text blocks
- Rich text editor for transcriptions
- Template-based text processing with GPT-4
- Responsive design
- Docker support for easy deployment
- Automatic model selection (CPU/CUDA)
- Configurable Whisper models
- Progress indication during processing

## Technology Stack

- Frontend: Vue.js 3, Vue Router, Vue Quill, Pinia
- Backend: FastAPI, Whisper, OpenAI
- Container: Docker, Docker Compose
- API: REST + WebSocket for live streaming

## Prerequisites

- Docker and Docker Compose
- OpenAI API Key for template processing
- NVIDIA GPU (optional) for accelerated transcription

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/arkonballoon/VoiceToDocWeb.git
cd VoiceToDocWeb
```
### Configure environment variables

```bash
cp .env.example .env
Add OpenAI API Key to .env
```

### Start containers

```bash
docker-compose up -d
```
## Manual Installation

### Backend
```bash
# Create and activate a Python Virtual Environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
# Navigate to the backend directory
cd backend
# Install Python dependencies
pip install -r requirements.txt
# Install PyTorch (optional, if not included in requirements.txt)
bash ../install_pytorch.sh
# Configure environment variables
cp .env.example .env
# Add your OpenAI API Key to .env

# Start the backend server
cd src
uvicorn main:app --reload
```

The backend server will then run at `http://localhost:8000`

### Frontend
```bash
# Navigate to the frontend directory
cd frontend
# Install npm dependencies
npm install
# Start the development server
npm run dev
```
The frontend server will then run at `http://localhost:3000`

Both servers must run in parallel for the application to function.

## Development

The project uses:
- ESLint and Prettier for code formatting
- Vue Router for navigation
- Pinia for state management
- Vue Quill for rich text editing
- FastAPI for RESTful API and WebSocket
- Whisper for speech recognition
- OpenAI GPT-4 for template processing
- Docker for containerization
- WebRTC for audio streaming
- Cursor.ai as IDE
- Claude-3.5 as AI assistant

## Configuration

The application can be configured via the web interface or `config.json`:
- Whisper model size (tiny to large-v3)
- Audio parameters (silence detection, chunk size)
- Worker count for parallel processing
- GPU/CPU model selection
- Template processing parameters


Developed as a proof of concept for CHOP (Chat Oriented Programming)
