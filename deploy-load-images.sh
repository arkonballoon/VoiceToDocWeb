#!/bin/bash
# Bash-Skript zum Importieren der Docker-Images auf dem Produktivserver
# Verwendung: ./deploy-load-images.sh

echo "Loading Docker images..."
docker load -i backend-image.tar
docker load -i frontend-image.tar

echo "Images loaded successfully!"
echo ""
echo "Available images:"
docker images | grep voicetodocweb

echo ""
echo "Next steps:"
echo "1. Copy docker-compose.yml and .env files to server"
echo "2. Adjust .env files for production"
echo "3. Run: docker-compose up -d"

