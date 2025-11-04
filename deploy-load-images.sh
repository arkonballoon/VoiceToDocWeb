#!/bin/bash
# Bash-Skript zum Importieren der Docker-Images auf dem Produktivserver
# Verwendung: ./deploy-load-images.sh

set -e

echo "Loading Docker images..."
docker load -i backend-image.tar
docker load -i frontend-image.tar

echo "Images loaded successfully!"

# Images sind bereits mit :prod Tag geladen und können direkt verwendet werden
echo ""
echo "Images ready with :prod tag for docker-compose.prod.images.yml"
echo ""
echo "Available images:"
docker images | grep voicetodocweb

echo ""
echo "Next steps:"
echo "1. Copy docker-compose.prod.images.yml and .env files to server"
echo "2. Adjust .env files for production"
echo "3. Run: docker-compose -f docker-compose.prod.images.yml up -d"

