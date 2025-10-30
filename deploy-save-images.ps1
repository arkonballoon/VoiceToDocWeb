# PowerShell-Skript zum Exportieren der Docker-Images für Produktivserver
# Verwendung: .\deploy-save-images.ps1

Write-Host "Building Docker images..." -ForegroundColor Green
docker-compose build

Write-Host "Tagging images..." -ForegroundColor Green
docker tag voicetodocweb-backend:latest voicetodocweb-backend:prod
docker tag voicetodocweb-frontend:latest voicetodocweb-frontend:prod

Write-Host "Exporting images to tar files..." -ForegroundColor Green
docker save voicetodocweb-backend:prod -o backend-image.tar
docker save voicetodocweb-frontend:prod -o frontend-image.tar

Write-Host "Images exported successfully!" -ForegroundColor Green
Write-Host "Backend: backend-image.tar" -ForegroundColor Yellow
Write-Host "Frontend: frontend-image.tar" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy both .tar files to server (e.g., with WinSCP or scp)" -ForegroundColor White
Write-Host "2. On server, run: docker load -i backend-image.tar" -ForegroundColor White
Write-Host "3. On server, run: docker load -i frontend-image.tar" -ForegroundColor White

