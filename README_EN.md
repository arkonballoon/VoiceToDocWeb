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
- Live audio recording with real-time transcription (every 5 seconds)
- Mobile-optimized UI with live transcript display
- Template management for text blocks
- Rich text editor for transcriptions
- Template-based text processing with GPT-4
- Responsive design (Desktop, Tablet, Mobile)
- Progressive Web App (PWA) with install prompt
- Docker support for easy deployment
- Automatic model selection (CPU/CUDA)
- Configurable Whisper models (via Web UI)
- Progress indication during processing
- WebSocket for live updates

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

The application requires environment variables for backend and frontend. Example files are included in the repository:

**Backend configuration:**
```bash
cd backend
cp .env.example .env
# Edit .env and add at least your OpenAI API Key:
# LLM_API_KEY=your_openai_api_key_here
```

**Frontend configuration:**
```bash
cd frontend
cp .env.example .env
# Optional: Adjust backend URL and other settings
```

> **Note:** The `.env.example` files contain all available configuration options with default values and detailed comments.

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
bash install_pytorch.sh
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
- RecordRTC for audio recording
- Cursor.ai as IDE
- Claude-3.5 as AI assistant

### Testing

- **Backend**: pytest (see `backend/tests/README.md`)
- **Frontend**: Vitest (prepared, see `frontend/tests/README.md`)

Run tests:
```bash
# Backend
cd backend
pytest

# Frontend (after installing Vitest)
cd frontend
npm run test
```

## Configuration

The application can be configured via the web interface or `config.json`:
- Whisper model size (tiny to large-v3) - **Now changeable via Web UI**
- Audio parameters (silence detection, chunk size)
- Worker count for parallel processing
- GPU/CPU model selection (WHISPER_DEVICE_CUDA)
- Template processing parameters

**Note:** Changes to the Whisper model are automatically loaded without restarting the backend.

## Mobile Features

VoiceToDoc is fully optimized for mobile devices:

- **Live Transcription**: Automatic transcription every 5 seconds during recording
- **Mobile UI**: Optimized user interface for smartphones
- **PWA**: Installable as an app on the home screen
- **Offline Capability**: Service Worker for offline usage
- **Touch Optimization**: Large buttons, touch feedback
- **Auto-Scroll**: Transcript automatically scrolls to the end on new fragments

For more details, see [frontend/PWA_FEATURES.md](frontend/PWA_FEATURES.md) and [frontend/MOBILE_TESTING.md](frontend/MOBILE_TESTING.md)

## Project Structure

For detailed information about the project structure, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## Contributing

Contributions are welcome!

**For Bugs:**
[Create Issue](https://github.com/arkonballoon/VoiceToDocWeb/issues/new?template=bug_report.md)

**For Features:**
[Suggest Feature](https://github.com/arkonballoon/VoiceToDocWeb/issues/new?template=feature_request.md)

**For Questions:**
[Ask Question](https://github.com/arkonballoon/VoiceToDocWeb/issues/new?template=question.md)

**Workflow:**
1. Create branch (`feature/...` or `fix/...`)
2. Commit changes
3. Create Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Developed as a proof of concept for CHOP (Chat Oriented Programming)
