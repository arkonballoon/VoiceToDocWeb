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
scp docker-compose.prod.images.yml user@server:/opt/voicetodocweb/
scp deploy-server-setup.sh user@server:/tmp/
scp deploy-start.sh user@server:/opt/voicetodocweb/
scp deploy-load-images.sh user@server:/tmp/
```

3) Auf dem Server (Linux):
```bash
cd /opt/voicetodocweb
chmod +x /tmp/deploy-server-setup.sh
/tmp/deploy-server-setup.sh

# Images importieren
chmod +x deploy-load-images.sh
./deploy-load-images.sh

# .env-Datei erstellen und anpassen
cp backend/.env.example backend/.env
nano backend/.env  # API-Schlüssel und Domain eintragen!

# Container starten (mit automatischer GPU-Erkennung)
chmod +x deploy-start.sh
./deploy-start.sh
```

Hinweis: Für Produktion später HTTPS aktivieren (z. B. via Caddy oder Nginx+Certbot). Ohne gültiges Zertifikat funktionieren Mikrofonzugriff und PWA auf dem Handy nicht zuverlässig.

## Methode 1: Docker Images als Tar-Dateien (Empfohlen)

### Schritt 1: Images lokal bauen und exportieren

**Auf deinem Windows-PC:**

```powershell
# PowerShell-Skript ausführen
.\deploy-save-images.ps1

# Oder manuell:
docker-compose -f docker-compose.prod.yml build
# Images werden automatisch mit :prod Tag erstellt
docker save voicetodocweb-backend:prod -o backend-image.tar
docker save voicetodocweb-frontend:prod -o frontend-image.tar
```

**Wichtig:** Images werden mit dem Tag `:prod` erstellt (siehe `docker-compose.prod.yml`). Die alten `:latest` Tags werden nicht mehr verwendet.

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

### Schritt 4: Verzeichnisstruktur auf Server erstellen

**Wichtig:** Auch wenn du nur die Docker-Images importierst, brauchst du auf dem Server eine Verzeichnisstruktur für:
- Die `.env`-Dateien (werden vom Container gelesen)
- Die Datenverzeichnisse (Volumes für Templates, Logs, etc.)

**Auf dem Linux-Server:**

```bash
# Arbeitsverzeichnis erstellen
mkdir -p /opt/voicetodocweb
cd /opt/voicetodocweb

# Verzeichnisstruktur für Backend-Daten erstellen
mkdir -p backend/data/templates
mkdir -p backend/data/logs
mkdir -p backend/data/temp
```

### Schritt 5: docker-compose.prod.images.yml auf Server kopieren

**Wichtig:** Verwende `docker-compose.prod.images.yml` (nicht `docker-compose.prod.yml`) für Production-Deployments mit Traefik.

```bash
# Auf deinem Windows-PC (PowerShell):
# Kopiere die fertige docker-compose.prod.images.yml
scp docker-compose.prod.images.yml user@produktivserver:/opt/voicetodocweb/

# Die Datei enthält bereits:
# - Traefik-Routing-Konfiguration
# - Healthcheck mit python3 (kein curl benötigt)
# - Image-Tags :prod statt :latest
# - Stripprefix-Middleware für /api-Routes
```

**Voraussetzung:** Traefik muss bereits auf dem Server laufen und im `proxy` Network konfiguriert sein.

### Schritt 6: Backend .env-Datei erstellen

**Auf dem Linux-Server:**

```bash
cd /opt/voicetodocweb

# .env-Datei erstellen
nano backend/.env
```

**Minimaler Inhalt der `backend/.env`-Datei:**

```env
# API-Schlüssel (erforderlich!)
LLM_API_KEY=sk-dein-api-schlüssel-hier

# CORS-Konfiguration (wichtig: mit deiner Domain!)
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Produktions-Einstellungen
DEBUG=false
LOG_LEVEL=30
DB_TYPE=sqlite
```

**Hinweis:** Das Frontend braucht keine `.env`-Datei in Production, da die Build-Argumente bereits beim Build-Zeitpunkt gesetzt wurden.

### Schritt 7: Helper-Skript auf Server ausführen (optional)

Das Skript `deploy-server-setup.sh` erstellt die Verzeichnisstruktur automatisch:

```bash
# Auf deinem Windows-PC (PowerShell):
scp deploy-server-setup.sh user@produktivserver:/tmp/

# Auf dem Server:
chmod +x /tmp/deploy-server-setup.sh
/tmp/deploy-server-setup.sh /opt/voicetodocweb
```

**Oder** manuell die Verzeichnisse erstellen (siehe Schritt 4).

### Schritt 8: Container starten

**Option A: Automatisches Start-Skript (empfohlen - prüft automatisch GPU)**

```bash
cd /opt/voicetodocweb

# Start-Skript kopieren (vom Windows-PC):
# scp deploy-start.sh user@server:/opt/voicetodocweb/

# Auf dem Server:
chmod +x deploy-start.sh
./deploy-start.sh
```

Das Skript prüft automatisch, ob eine GPU vorhanden ist, und startet entsprechend. Keine manuelle Konfiguration nötig!

**Option B: Manuell starten (ohne GPU)**

```bash
cd /opt/voicetodocweb
docker-compose -f docker-compose.prod.images.yml up -d

# Status prüfen
docker-compose -f docker-compose.prod.images.yml ps
docker-compose -f docker-compose.prod.images.yml logs
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
docker tag voicetodocweb-backend:prod deinusername/voicetodoc-backend:latest
docker tag voicetodocweb-frontend:prod deinusername/voicetodoc-frontend:latest

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

4. **Traefik** - Automatisches HTTPS, Docker-native (Aktuell verwendet)
   - Erkennt Container automatisch via Docker Provider
   - Automatisches HTTPS mit Let's Encrypt
   - Routing über Labels: API unter `/api`, WebSocket unter `/ws`
   - Siehe `docker-compose.prod.images.yml` für vollständige Konfiguration

**Aktuelle Traefik-Konfiguration:**
- Frontend: `https://yourdomain.com` → Frontend (Port 3000)
- API: `https://yourdomain.com/api/*` → Backend (Port 8000) mit `/api` Prefix-Stripping
- WebSocket: `wss://yourdomain.com/ws/*` → Backend (Port 8000)
- Healthcheck: Backend verwendet `python3` statt `curl` (Container hat kein curl)

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
   - **Automatisch:** Das `deploy-start.sh` Skript erkennt automatisch, ob eine GPU vorhanden ist, und konfiguriert entsprechend
   - Die `docker-compose.prod.images.yml` ist standardmäßig **ohne GPU** konfiguriert (funktioniert auf jedem Server)
   - Whisper fällt automatisch auf CPU zurück, wenn keine GPU verfügbar ist - funktioniert, ist aber langsamer

---

## Troubleshooting

### Images werden nicht geladen

```bash
# Prüfen, ob Images vorhanden sind (mit :prod Tag)
docker images | grep voicetodocweb

# Falls nicht, erneut importieren:
docker load -i backend-image.tar
docker load -i frontend-image.tar

# Prüfen ob Tags korrekt sind:
docker images | grep prod
```

### Traefik-Routing funktioniert nicht

```bash
# Prüfen ob Container im proxy Network sind:
docker network inspect proxy | grep -A 5 voicetodocweb

# Prüfen ob Container healthy ist:
docker ps | grep v2d-backend

# Prüfen ob Traefik die Container sieht:
docker logs traefik | grep -E "v2d-api|v2d-fe|v2d-ws"

# Prüfen ob Backend-Container unhealthy ist (würde ignoriert werden):
docker inspect v2d-backend --format='{{.State.Health.Status}}'
```

**Häufige Probleme:**
- Container ist `unhealthy` → Traefik ignoriert ihn → Healthcheck mit `python3` verwenden, nicht `curl`
- `tls=true` in Labels → Router wird nur für HTTPS erstellt → Für HTTP und HTTPS: `tls=true` entfernen
- Fehlende `stripprefix` Middleware → `/api/health` wird nicht zu `/health` → Middleware zu Router hinzufügen

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

