FROM node:18-alpine

WORKDIR /app

# Abhängigkeiten installieren
COPY package*.json ./
RUN npm install

# Anwendungscode kopieren
COPY . .

# Umgebungsvariablen setzen (mit Fallback-Werten)
ENV VITE_BACKEND_URL=localhost:8000
ENV VITE_PROTOCOL=http
ENV VITE_WS_PROTOCOL=ws
ENV VITE_WS_HEARTBEAT_INTERVAL=30000
ENV VITE_WS_MAX_RECONNECT_ATTEMPTS=3
ENV VITE_WS_RECONNECT_DELAY=5000
ENV VITE_MAX_FILE_SIZE=52428800
ENV VITE_AUDIO_CHUNK_SIZE=5000
ENV VITE_AUDIO_SAMPLE_RATE=16000
ENV VITE_THEME=light
ENV VITE_LANGUAGE=de
ENV VITE_AUTO_SAVE_INTERVAL=30000

# Port freigeben
EXPOSE 3000

# Entwicklungsserver starten
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 
