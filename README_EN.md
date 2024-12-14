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
- Template management for text modules
- Rich-text editor for transcriptions
- Template-based text processing
- Responsive design

## Technology Stack

- Frontend: Vue.js 3, Vue Router, Vue Quill, Pinia
- Backend: FastAPI, SQLAlchemy, OpenAI
- Database: SQLite
- API: REST

## Requirements

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API Key for template processing

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/arkonballoon/VoiceToDocWeb.git
```

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

This project uses:
- ESLint and Prettier for code formatting
- Vue Router for navigation
- Pinia for state management
- Vue Quill for rich-text editing
- FastAPI for RESTful API
- SQLAlchemy for database operations
- OpenAI for template processing
- Cursor.ai as IDE
- Claude-3.5 as AI assistant

Developed as a proof of concept for CHOP (Chat Oriented Programming)

--- 

Let me know if you'd like further assistance!