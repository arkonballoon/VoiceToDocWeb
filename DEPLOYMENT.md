# Deployment-Anleitung für VoiceToDoc

Diese Anleitung beschreibt, wie du die Anwendung auf einen Produktivserver bringst – inklusive einer Variante, die den Transfer ohne HTTPS ermöglicht. Für den Live-Betrieb auf mobilen Geräten brauchst du später dennoch ein gültiges HTTPS-Zertifikat (wegen Mikrofonzugriff/PWA).

## TL;DR (Schnellstart)

1) Auf deinem Windows-PC (PowerShell):
```powershell
docker-compose -f docker-compose.prod.yml build
.\u005cdeploy-save-images.ps1
```

2) Dateien auf den Server kopieren (WinSCP oder scp):
```powershell
scp backend-image.tar frontend-image.tar user@server:/tmp/
scp docker-compose.prod.yml user@server:/opt/voicetodocweb/
```

3) Auf dem Server (Linux):
```bash
cd /opt/voicetodocweb
chmod +x deploy-load-images.sh
./deploy-load-images.sh
docker-compose -f docker-compose.prod.yml up -d
```

Hinweis: Für Produktion später HTTPS aktivieren (z. B. via Caddy oder Nginx+Certbot). Ohne gültiges Zertifikat funktionieren Mikrofonzugriff und PWA auf dem Handy nicht zuverlässig.

## Methode 1: Docker Images als Tar-Dateien (Empfohlen)

### Schritt 1: Images lokal bauen und exportieren

**Auf deinem Windows-PC:**

```powershell
# PowerShell-Skript ausführen
.\deploy-save-images.ps1

# Oder manuell:
docker-compose build
docker save voicetodocweb-backend:latest -o backend-image.tar
docker save voicetodocweb-frontend:latest -o frontend-image.tar
```

### Schritt 2: Dateien auf Server kopieren

**Über WinSCP, SCP oder andere SFTP-Tools:**

Die beiden `.tar`-Dateien auf den Server kopieren (z.B. nach `/tmp/`)

```powershell
# Mit OpenSSH (falls installiert)
scp backend-image.tar frontend-image.tar user@produktivserver:/tmp/
```

### Schritt 3: Images auf Server importieren

**Auf dem Linux-Server:**

```bash
# Skript ausführbar machen
chmod +x deploy-load-images.sh

# Images importieren
./deploy-load-images.sh

# Oder manuell:
docker load -i /tmp/backend-image.tar
docker load -i /tmp/frontend-image.tar
```

### Schritt 4: Config-Dateien kopieren

```bash
# docker-compose.prod.yml und .env-Dateien auf Server kopieren
# Dann anpassen:
nano backend/.env
nano frontend/.env  # Falls vorhanden
```

### Schritt 5: Container starten

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Methode 2: Code auf Server kopieren und dort bauen

### Option A: Git Clone (wenn Server Internetzugriff hat)

```bash
# Auf Server
git clone https://github.com/arkonballoon/VoiceToDocWeb.git
cd VoiceToDocWeb

# .env-Dateien anpassen
cp backend/.env.example backend/.env
nano backend/.env

# Images bauen
docker-compose -f docker-compose.prod.yml build

# Starten
docker-compose -f docker-compose.prod.yml up -d
```

### Option B: ZIP-Datei erstellen

**Auf Windows:**

```powershell
# Repository-Status prüfen (uncommitted Änderungen ggf. committen)
git status

# ZIP erstellen (ohne node_modules, __pycache__, etc.)
git archive -o voicetodoc-deploy.zip HEAD
```

**Auf Server:**

```bash
# ZIP-Datei entpacken
unzip voicetodoc-deploy.zip -d /opt/voicetodocweb
cd /opt/voicetodocweb

# .env-Dateien anpassen
cp backend/.env.example backend/.env
nano backend/.env

# Images bauen
docker-compose -f docker-compose.prod.yml build

# Starten
docker-compose -f docker-compose.prod.yml up -d
```

---

## Methode 3: Docker Registry (z.B. Docker Hub)

**Auf Windows:**

```powershell
# Bei Docker Hub anmelden
docker login

# Images taggen
docker tag voicetodocweb-backend:latest deinusername/voicetodoc-backend:latest
docker tag voicetodocweb-frontend:latest deinusername/voicetodoc-frontend:latest

# Images pushen
docker push deinusername/voicetodoc-backend:latest
docker push deinusername/voicetodoc-frontend:latest
```

**Auf Server:**

```bash
# Bei Docker Hub anmelden
docker login

# Images pullen
docker pull deinusername/voicetodoc-backend:latest
docker pull deinusername/voicetodoc-frontend:latest

# docker-compose.yml anpassen (image: statt build:)
# Dann starten:
docker-compose up -d
```

---

## HTTPS für Produktion

Für den Live-Betrieb auf mobilen Geräten ist HTTPS zwingend erforderlich (Mikrofonzugriff, PWA, Service Worker). Es gibt verschiedene Optionen:

### Optionen

1. **Cloudflare Tunnel** - Ideal für Server hinter NAT/Firewall, keine Portfreigaben nötig
   - Automatisches HTTPS via Cloudflare Zero Trust
   - Funktioniert ohne Portfreigaben (ideal hinter NAT/Firewall)

2. **Caddy** - Automatisches HTTPS mit Let's Encrypt, einfache Konfiguration
   - Reverse Proxy mit automatischer Zertifikatsverlängerung
   - Docker-Image verfügbar: `caddy:latest`

3. **Nginx + Certbot** - Klassische Lösung, sehr flexibel
   - Nginx als Reverse Proxy
   - Certbot für Let's Encrypt-Zertifikate
   - Standard für viele Produktionsumgebungen

4. **Traefik** - Automatisches HTTPS, Docker-native
   - Erkennt Container automatisch
   - Ideal für Docker-Umgebungen

**Wichtig:** Nach HTTPS-Setup:
- `ALLOWED_ORIGINS` in `backend/.env` auf deine HTTPS-Domain anpassen
- Frontend mit `VITE_PROTOCOL=https` und `VITE_WS_PROTOCOL=wss` neu bauen

---

## Produktionskonfiguration

### Backend .env-Beispiel

```env
LLM_API_KEY=sk-...
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
DEBUG=false
LOG_LEVEL=30
DB_TYPE=sqlite
# Oder für PostgreSQL:
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=voicetodoc
# DB_PASSWORD=...
# DB_NAME=voicetodoc_db
```

### Frontend Build-Argumente

In `docker-compose.prod.yml` oder beim Build:

```yaml
args:
  VITE_BACKEND_URL: api.yourdomain.com
  VITE_PROTOCOL: https
  VITE_WS_PROTOCOL: wss
```

---

## Wichtige Hinweise

1. **HTTPS für Produktion**: Auch wenn der Code-Transfer ohne HTTPS funktioniert, braucht die **laufende Anwendung** HTTPS für:
   - Mikrofonzugriff auf Mobilgeräten
   - PWA-Funktionalität
   - Service Worker

2. **Sicherheit**: 
   - `.env`-Dateien niemals ins Repository committen
   - API-Keys sicher aufbewahren
   - Firewall-Regeln prüfen

3. **Backups**: Regelmäßige Backups von:
   - Datenbank (`backend/data/templates.db`)
   - Templates (`backend/data/templates/`)
   - Logs (`backend/data/logs/`)

4. **Updates**: 
   - Neue Images bauen und erneut deployen
   - Oder via Git pull und rebuild auf Server

5. **GPU/ohne GPU**:
   - Wenn der Server keine NVIDIA-GPU hat, entferne die `deploy.resources.reservations.devices`-Sektion für den `backend`-Service in `docker-compose.prod.yml`.

---

## Troubleshooting

### Images werden nicht geladen

```bash
# Prüfen, ob Images vorhanden sind
docker images | grep voicetodocweb

# Falls nicht, erneut importieren
docker load -i backend-image.tar
```

### Container startet nicht

```bash
# Logs prüfen
docker-compose -f docker-compose.prod.yml logs

# Einzelnen Service prüfen
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

### Ports bereits belegt

```bash
# Anderen Container auf Port prüfen
sudo lsof -i :8000
sudo lsof -i :80

# Ports in docker-compose.prod.yml ändern
```

