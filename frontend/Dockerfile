FROM node:18-alpine

WORKDIR /app

# Abhängigkeiten installieren
COPY package*.json ./
RUN npm install

# Anwendungscode kopieren
COPY . .

# Umgebungsvariablen setzen
ENV VITE_API_URL=http://localhost:8000

# Port freigeben
EXPOSE 3000

# Entwicklungsserver starten
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 