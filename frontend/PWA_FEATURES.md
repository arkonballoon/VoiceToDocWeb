# VoiceToDoc - Progressive Web App (PWA) Features

## Übersicht

VoiceToDoc ist jetzt als Progressive Web App optimiert und bietet eine native App-ähnliche Erfahrung auf mobilen Geräten, insbesondere Android-Smartphones.

## 🚀 Hauptfeatures

### 1. Installation als App

- **"Add to Home Screen"** auf Android
- Automatischer Installations-Prompt nach 3 Sekunden Nutzung
- App-Icon auf dem Home-Screen
- Standalone-Modus (läuft ohne Browser-UI)

### 2. Offline-Fähigkeit

- Service Worker cacht statische Assets
- Network-First-Strategie für API-Calls
- Offline-Status-Banner zeigt Verbindungsprobleme
- Lokale Speicherung der letzten Template-Auswahl

### 3. Mobile-optimierte UI

#### Touch-Optimierungen
- Mindestgröße 48x48px für alle interaktiven Elemente
- Touch-Feedback bei Buttons und Links
- Haptic Feedback (falls unterstützt)
- Verhindert ungewolltes Zoomen bei Input-Focus (iOS)

#### Responsive Design
- **Desktop (> 768px)**: Volle Features, Desktop-Layout
- **Tablet (768px)**: Angepasstes Layout, Touch-optimiert
- **Mobile (< 480px)**: Kompaktes Layout, Single-Column
- **Landscape**: Optimiertes Layout für Querformat

#### Template-Auswahl auf Mobile
- Prominente Platzierung über Mikrofon-Auswahl
- Speichert letzte Auswahl in LocalStorage
- Einfache Dropdown-Auswahl für unterwegs
- Keine Template-Verwaltung (Desktop-only)

### 4. Netzwerkstabilität

#### Verbindungs-Monitoring
- Echtzeit-Netzwerkstatus-Banner
- Anzeige bei Verbindungsverlust
- Automatische Reconnection mit Exponential Backoff
- Queue-Status für ausstehende Uploads

#### WebSocket-Reconnection
- Automatische Wiederverbindung bei Unterbrechung
- Heartbeat-Mechanismus (30s Intervall)
- Maximale Reconnect-Versuche: 3
- Exponential Backoff: 5s → 10s → 15s

### 5. Web Share API

- Teilen-Button im Transkriptions-Editor
- Native Share-Dialoge auf Android
- Teilen über WhatsApp, E-Mail, etc.
- Automatischer Fallback wenn nicht unterstützt

### 6. Performance-Optimierungen

#### Code-Splitting
- Lazy Loading für Desktop-Features:
  - Template-Manager
  - Template-Verarbeitung
  - Konfiguration
- Schnellerer initialer Ladevorgang auf Mobile

#### Caching-Strategie
- **Statische Assets**: Cache-First (30 Tage)
- **API-Calls**: Network-First (5 Minuten Cache)
- **Backend-Requests**: 10s Timeout

## 📱 Installation

### Android (Chrome)

1. Öffne die App in Chrome
2. Warte auf den Installations-Prompt (3 Sekunden)
   - ODER: Chrome-Menü → "App installieren"
3. Tippe auf "Installieren"
4. App erscheint auf dem Home-Screen

### iOS (Safari)

1. Öffne die App in Safari
2. Tippe auf das Teilen-Icon
3. Wähle "Zum Home-Bildschirm"
4. Tippe auf "Hinzufügen"

**Hinweis**: iOS hat eingeschränkte PWA-Unterstützung. Einige Features (z.B. Push-Notifications) sind nicht verfügbar.

## 🎨 Design & UX

### Markenfarben (Arkonballon)
- **Primär**: `#10B981` (Grün) - Buttons, Highlights
- **Sekundär**: `#7C3AED` (Lila) - Confidence-Badges, Akzente
- **Background**: `#003366` (Dunkelblau) - Header

### Touch-Targets
- Minimum: 44x44px (Apple HIG)
- Empfohlen: 48x48px (Material Design)
- Buttons mit visuellem Feedback bei Touch

### Accessibility
- Semantic HTML
- ARIA-Labels wo nötig
- Prefers-Reduced-Motion Support
- Kontrastreiche Farben

## 🔧 Technische Details

### Service Worker
- Generiert von `vite-plugin-pwa`
- Automatisches Update bei neuer Version
- Workbox Runtime-Caching
- Background Sync (vorbereitet)

### PWA-Manifest
- Standalone Display-Mode
- Portrait Orientation
- Theme Color: Grün (#10B981)
- Background Color: Lila (#7C3AED)
- Icons: 192x192, 512x512

### Browser-Kompatibilität
- ✅ Chrome/Edge (Android): Volle Unterstützung
- ✅ Samsung Internet: Volle Unterstützung
- ⚠️ Safari (iOS): Eingeschränkte PWA-Unterstützung
- ⚠️ Firefox: Basis-PWA-Support

## 📊 Lighthouse PWA Score (Ziel)

- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90
- PWA: 100

## 🚦 Testing

### Mobile Testing
```bash
# Chrome DevTools Device Emulation
1. F12 → Toggle Device Toolbar
2. Wähle Gerät (z.B. Pixel 5)
3. Teste Touch-Interaktionen

# Netzwerk-Throttling
1. DevTools → Network Tab
2. Wähle "Slow 3G" oder "Fast 3G"
3. Teste Reconnection-Logik
```

### Lighthouse Audit
```bash
# Im Browser
1. F12 → Lighthouse Tab
2. Wähle "Mobile" + "Progressive Web App"
3. "Generate report"

# CLI (optional)
npm install -g lighthouse
lighthouse http://localhost:3000 --view
```

### Real Device Testing
1. Deployment auf HTTPS (erforderlich für Service Worker)
2. Teste auf echtem Android-Gerät
3. Installiere als PWA
4. Teste Offline-Modus (Flugmodus)
5. Teste Netzwerkwechsel (WLAN → Mobile)

## 🔐 Sicherheit

### HTTPS Requirement
- Service Worker funktioniert nur über HTTPS
- Ausnahme: `localhost` für Entwicklung
- Produktion: Immer HTTPS verwenden

### Content Security Policy
- Kein Inline-JavaScript
- Nur vertrauenswürdige Quellen
- CSP-Header im Backend konfigurieren

## 📝 Bekannte Einschränkungen

### iOS
- Kein Background Sync
- Keine Push Notifications
- Limitierter Cache (50MB)
- Service Worker kann nach 3 Wochen gelöscht werden

### Android
- Battery Saver kann Background-Tasks einschränken
- Data Saver kann Netzwerk-Requests blockieren

## 🎯 Zukünftige Verbesserungen

### Phase 3 (Nice-to-Have)
- [ ] Chunked Upload für große Dateien (>10MB)
- [ ] Resume-Fähigkeit bei Verbindungsabbruch
- [ ] Background Sync für fehlgeschlagene Uploads
- [ ] Push Notifications bei Template-Verarbeitung
- [ ] Offline-Modus mit lokaler Transkription (WebAssembly Whisper)

## 🆘 Troubleshooting

### Service Worker wird nicht registriert
- Prüfe HTTPS-Verbindung
- Prüfe Browser-Konsole auf Fehler
- Lösche Browser-Cache und neu laden

### Installation-Prompt erscheint nicht
- Chrome: Prüfe `chrome://flags` → "App Banners"
- Bereits installiert? Deinstalliere und versuche erneut
- Warte 3 Sekunden nach Seitenaufruf

### Offline-Modus funktioniert nicht
- Service Worker muss vollständig installiert sein
- Erste Seite muss online geladen werden
- Prüfe Cache-Storage in DevTools

### Template-Auswahl wird nicht gespeichert
- Prüfe LocalStorage in DevTools
- Private Mode/Inkognito hat eingeschränkten Storage
- Browser-Einstellungen für Cookies prüfen

## 📚 Weitere Ressourcen

- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Web Share API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Share_API)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Workbox](https://developers.google.com/web/tools/workbox)
