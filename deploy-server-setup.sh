#!/bin/bash
# Helper-Skript zum Erstellen der Verzeichnisstruktur auf dem Server
# Verwendung: ./deploy-server-setup.sh

set -e

echo "Erstelle Verzeichnisstruktur für VoiceToDoc..."

# Arbeitsverzeichnis (wird als Argument übergeben oder verwendet /opt/voicetodocweb)
WORK_DIR="${1:-/opt/voicetodocweb}"

echo "Arbeitsverzeichnis: $WORK_DIR"

# Verzeichnisse erstellen
mkdir -p "$WORK_DIR/backend/data/templates"
mkdir -p "$WORK_DIR/backend/data/logs"
mkdir -p "$WORK_DIR/backend/data/temp"

echo "✓ Verzeichnisstruktur erstellt"

# .env-Beispiel-Datei erstellen, falls noch nicht vorhanden
if [ ! -f "$WORK_DIR/backend/.env" ]; then
    echo ""
    echo "Erstelle Beispiel .env-Datei..."
    cat > "$WORK_DIR/backend/.env.example" << 'EOF'
# API-Schlüssel (erforderlich!)
LLM_API_KEY=sk-dein-api-schlüssel-hier

# CORS-Konfiguration (wichtig: mit deiner Domain!)
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Produktions-Einstellungen
DEBUG=false
LOG_LEVEL=30
DB_TYPE=sqlite

# Optional: PostgreSQL
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=voicetodoc
# DB_PASSWORD=dein-passwort
# DB_NAME=voicetodoc_db
EOF
    echo "✓ Beispiel .env-Datei erstellt: $WORK_DIR/backend/.env.example"
    echo ""
    echo "WICHTIG: Kopiere .env.example zu .env und passe die Werte an:"
    echo "  cp $WORK_DIR/backend/.env.example $WORK_DIR/backend/.env"
    echo "  nano $WORK_DIR/backend/.env"
else
    echo "✓ .env-Datei existiert bereits"
fi

echo ""
echo "Verzeichnisstruktur:"
tree -L 3 "$WORK_DIR" || ls -laR "$WORK_DIR"

echo ""
echo "Nächste Schritte:"
echo "1. Passe backend/.env an (API-Schlüssel, Domain, etc.)"
echo "2. Kopiere docker-compose.prod.yml auf den Server"
echo "3. Passe docker-compose.prod.yml an (image: statt build:)"
echo "4. Importiere Docker-Images: docker load -i /tmp/backend-image.tar"
echo "5. Starte Container: docker-compose -f docker-compose.prod.yml up -d"

