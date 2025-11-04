# Mobile PWA Testing Guide

## Schnelltest-Checkliste

### ✅ PWA Installation
- [ ] Installation-Prompt erscheint nach 3 Sekunden
- [ ] "Add to Home Screen" funktioniert
- [ ] App-Icon erscheint auf Home-Screen
- [ ] App startet im Standalone-Modus (ohne Browser-UI)

### ✅ Mobile UI
- [ ] Alle Buttons sind mindestens 48x48px
- [ ] Touch-Feedback bei Button-Tap
- [ ] Keine horizontale Scrollbar
- [ ] Template-Auswahl ist prominent sichtbar
- [ ] Text ist lesbar ohne Zoomen
- [ ] Input-Focus zoomt nicht (iOS)

### ✅ Funktionalität
- [ ] Mikrofon-Auswahl funktioniert
- [ ] Aufnahme starten/stoppen funktioniert
- [ ] Live-Transkription erscheint während Aufnahme (alle 5 Sekunden)
- [ ] Transkription wird nach Stopp vollständig angezeigt
- [ ] Auto-Scroll funktioniert bei neuen Fragmenten
- [ ] Audio-Upload funktioniert
- [ ] Template-Auswahl wird gespeichert (LocalStorage)
- [ ] Transkript ohne Template speichern/teilen funktioniert
- [ ] Teilen-Button funktioniert (Android)

### ✅ Netzwerkstabilität
- [ ] Offline-Banner erscheint bei Verbindungsverlust
- [ ] WebSocket reconnected automatisch
- [ ] Service Worker cacht Assets

### ✅ Performance
- [ ] Initiale Ladezeit < 3 Sekunden
- [ ] Smooth Scrolling
- [ ] Keine Lag bei Button-Taps

## Detaillierte Test-Szenarien

### 1. Installation Flow (Android)

**Test 1.1: Automatischer Prompt**
1. Öffne App in Chrome (https://your-domain.com)
2. Warte 3 Sekunden
3. ✅ Installations-Banner erscheint unten
4. Tap "Installieren"
5. ✅ App wird installiert
6. ✅ Icon erscheint auf Home-Screen

**Test 1.2: Manueller Install**
1. Öffne App in Chrome
2. Chrome-Menü → "App installieren"
3. ✅ Installation-Dialog erscheint
4. Bestätige Installation
5. ✅ App installiert

**Test 1.3: Dismiss-Funktionalität**
1. Warte auf Installations-Banner
2. Tap "Später"
3. ✅ Banner verschwindet
4. Reload Seite
5. ✅ Banner erscheint nicht sofort

**Test 1.4: Dismiss Forever**
1. Warte auf Banner
2. Tap "X" (Schließen)
3. ✅ Banner verschwindet
4. Reload mehrmals
5. ✅ Banner erscheint nie wieder

### 2. Mobile UI Responsiveness

**Test 2.1: Portrait Mode (Haupttest)**
Gerät: Smartphone (< 768px)
1. Öffne App
2. ✅ Template-Auswahl ist prominent
3. ✅ Mikrofon-Auswahl ist groß genug
4. ✅ Aufnahme-Button ist prominent
5. ✅ Alle Touch-Targets ≥ 48px
6. Scroll nach unten
7. ✅ Editor ist gut nutzbar
8. ✅ Toolbar ist sticky

**Test 2.2: Landscape Mode**
1. Drehe Gerät ins Querformat
2. ✅ Layout passt sich an
3. ✅ Keine horizontale Scrollbar
4. ✅ Editor-Toolbar weiterhin sticky

**Test 2.3: Sehr kleine Geräte (< 480px)**
1. DevTools: Wähle "iPhone SE"
2. ✅ Alles lesbar
3. ✅ Keine Überlappungen
4. ✅ Buttons nutzbar

**Test 2.4: Tablet (768px - 1024px)**
1. DevTools: Wähle "iPad"
2. ✅ Zwischen Mobile und Desktop-Layout
3. ✅ Touch-optimiert
4. ✅ Gute Nutzung des Platzes

### 3. Aufnahme-Workflow

**Test 3.1: Mikrofon-Auswahl**
1. Öffne App
2. Tap Mikrofon-Dropdown
3. ✅ Liste zeigt alle Mikrofone
4. Wähle Mikrofon
5. ✅ Auswahl wird angezeigt
6. ✅ Aufnahme-Button wird enabled

**Test 3.2: Template-Auswahl**
1. Tap Template-Dropdown
2. ✅ Template-Liste lädt
3. Wähle Template
4. ✅ Auswahl wird gespeichert
5. Reload Seite
6. ✅ Letzte Auswahl ist pre-selected

**Test 3.3: Audio-Aufnahme**
1. Wähle Mikrofon
2. Tap "Aufnahme starten"
3. ✅ Button wird rot
4. ✅ "Aufnahme läuft..." erscheint
5. Spreche 10 Sekunden
6. ✅ Automatischer Upload nach 5s
7. ✅ Transkription erscheint im Editor
8. Spreche weitere 10 Sekunden
9. ✅ Weitere Transkription wird angehängt
10. Tap "Aufnahme stoppen"
11. ✅ Button wird wieder grün

**Test 3.4: Datei-Upload**
1. Tap Upload-Bereich
2. Wähle Audio-Datei
3. ✅ Dateiname wird angezeigt
4. Tap "Transkribieren"
5. ✅ Loading-Indicator
6. ✅ Transkription erscheint nach Verarbeitung

### 4. Netzwerk-Tests

**Test 4.1: Offline-Erkennung**
1. App ist geladen
2. Aktiviere Flugmodus
3. ✅ Offline-Banner erscheint: "Keine Internetverbindung"
4. Deaktiviere Flugmodus
5. ✅ "Verbindung wiederhergestellt" Banner (3s)
6. ✅ Banner verschwindet automatisch

**Test 4.2: Langsame Verbindung**
DevTools → Network → Slow 3G
1. Starte Aufnahme
2. ✅ Upload dauert länger
3. ✅ Loading-Indicator sichtbar
4. ✅ Request timeout nach 120s (falls nötig)
5. ✅ Error-Message bei Timeout

**Test 4.3: WebSocket Reconnect**
1. Starte Template-Verarbeitung
2. DevTools → Network → Offline (während Verarbeitung)
3. ✅ Reconnecting-Banner erscheint
4. ✅ "Versuch 1 von 3", "Versuch 2 von 3"
5. Aktiviere Netzwerk wieder
6. ✅ WebSocket verbindet neu
7. ✅ Verarbeitung läuft weiter

**Test 4.4: Netzwerkwechsel (WLAN → Mobile)**
1. Verbinde mit WLAN
2. Lade App
3. Starte Aufnahme
4. Wechsle zu Mobile Data während Aufnahme
5. ✅ Kurzer Reconnect
6. ✅ Aufnahme läuft weiter
7. ✅ Upload funktioniert

### 5. Web Share API

**Test 5.1: Share-Button verfügbar (Android)**
1. Erstelle Transkription
2. ✅ "Teilen"-Button ist sichtbar
3. ✅ Button hat grüne Farbe

**Test 5.2: Share-Funktionalität**
1. Tap "Teilen"-Button
2. ✅ Native Share-Dialog öffnet
3. ✅ Transkription als Text verfügbar
4. Wähle App (z.B. WhatsApp)
5. ✅ Text wird korrekt übertragen

**Test 5.3: Share abbrechen**
1. Tap "Teilen"
2. Tap "Abbrechen" im Share-Dialog
3. ✅ Keine Fehler-Meldung
4. ✅ App funktioniert weiter normal

**Test 5.4: Desktop/Nicht unterstützt**
Desktop Browser:
1. Erstelle Transkription
2. ✅ "Teilen"-Button erscheint NICHT (oder disabled)

### 6. Service Worker & Offline

**Test 6.1: Service Worker Installation**
1. Erste Seite laden
2. DevTools → Application → Service Workers
3. ✅ Service Worker "activated and is running"
4. ✅ Scope: "/" oder "/app/"

**Test 6.2: Cache**
DevTools → Application → Cache Storage
1. Öffne "workbox-precache"
2. ✅ index.html gecacht
3. ✅ CSS-Files gecacht
4. ✅ JS-Files gecacht
5. ✅ Icons gecacht

**Test 6.3: Offline-Navigation**
1. Lade App komplett
2. Aktiviere Flugmodus
3. Navigiere zu "/" (Transkription)
4. ✅ Seite lädt aus Cache
5. Navigiere zu "/templates"
6. ✅ Lazy-loaded Component funktioniert

**Test 6.4: Update-Mechanismus**
1. Deploy neue Version
2. Öffne App (alte Version)
3. ✅ Service Worker erkennt Update
4. Reload Seite
5. ✅ Neue Version wird geladen

### 7. Performance-Tests

**Test 7.1: Initial Load**
DevTools → Lighthouse
1. Run "Mobile" Audit
2. ✅ Performance Score > 90
3. ✅ PWA Score = 100
4. ✅ Accessibility > 90
5. ✅ First Contentful Paint < 2s
6. ✅ Time to Interactive < 3s

**Test 7.2: Lazy Loading**
DevTools → Network → JS
1. Lade App (Hauptseite)
2. ✅ Nur TranscriptionView.js geladen
3. Navigiere zu /templates
4. ✅ TemplateManager.js wird jetzt geladen
5. ✅ Nicht vorher

**Test 7.3: Bundle Size**
1. Check dist/assets/
2. ✅ index.js < 500KB
3. ✅ Lazy chunks separate
4. ✅ CSS optimiert (< 150KB)

**Test 7.4: Memory**
Chrome Task Manager
1. Öffne App
2. Nutze alle Features
3. ✅ Memory < 100MB
4. ✅ Keine Memory Leaks

### 8. Accessibility

**Test 8.1: Screen Reader**
Android TalkBack aktiviert:
1. ✅ Alle Buttons werden vorgelesen
2. ✅ Template-Auswahl hat Labels
3. ✅ Mikrofon-Auswahl hat Labels
4. ✅ Navigation funktioniert

**Test 8.2: Kontrast**
1. ✅ Text-Kontrast ≥ 4.5:1
2. ✅ Buttons haben guten Kontrast
3. ✅ Bei Sonnenlicht lesbar

**Test 8.3: Dark Mode**
System Dark Mode aktiviert:
1. ✅ App respektiert System-Einstellung
2. ✅ Farben passen sich an
3. ✅ Gute Lesbarkeit

## Browser-Kompatibilität

### Chrome/Edge (Android)
- [x] Alle Features unterstützt
- [x] PWA Installation
- [x] Service Worker
- [x] Web Share API
- [x] Audio Recording

### Samsung Internet (Android)
- [x] Alle Features unterstützt
- [x] PWA Installation
- [x] Gute Performance

### Safari (iOS)
- [x] Basis-Funktionalität
- [ ] Eingeschränkte PWA-Features
- [ ] Kein Web Share API
- [x] Audio Recording funktioniert

### Firefox (Android)
- [x] Basis-Funktionalität
- [ ] Kein automatischer Install-Prompt
- [x] Manuelle Installation möglich

## Real Device Testing

### Minimum
1. **Android Smartphone** (Android 10+, Chrome)
   - Template-Auswahl
   - Audio-Aufnahme
   - PWA-Installation
   - Offline-Test

### Empfohlen
1. Android Smartphone (3 verschiedene Größen)
2. Android Tablet
3. iOS iPhone (für Kompatibilitäts-Check)

### Test-Matrix

| Feature | Android 10+ | iOS 15+ | Tablet |
|---------|-------------|---------|--------|
| PWA Install | ✅ | ⚠️ | ✅ |
| Audio Record | ✅ | ✅ | ✅ |
| Template Select | ✅ | ✅ | ✅ |
| Offline | ✅ | ⚠️ | ✅ |
| Web Share | ✅ | ❌ | ✅ |
| Service Worker | ✅ | ⚠️ | ✅ |

Legend: ✅ Voll unterstützt | ⚠️ Eingeschränkt | ❌ Nicht unterstützt

## Troubleshooting Guide

### Problem: Installation-Prompt erscheint nicht
**Lösung:**
1. Prüfe HTTPS (erforderlich)
2. Prüfe manifest.json ist erreichbar
3. Prüfe Service Worker registriert
4. Chrome: `chrome://flags` → "App Banners" enabled
5. Warte volle 3 Sekunden

### Problem: Service Worker registriert nicht
**Lösung:**
1. DevTools → Console nach Errors
2. Prüfe HTTPS
3. Cache leeren + Hard Reload (Ctrl+Shift+R)
4. Prüfe sw.js ist erreichbar
5. `chrome://serviceworker-internals` → Unregister

### Problem: Template-Auswahl lädt nicht
**Lösung:**
1. DevTools → Network → Prüfe /templates/ Request
2. Prüfe Backend läuft
3. Prüfe CORS-Header
4. Console nach Errors

### Problem: Audio-Aufnahme funktioniert nicht
**Lösung:**
1. Prüfe Mikrofon-Berechtigung
2. Chrome Site Settings → Mikrofon erlauben
3. Prüfe HTTPS (erforderlich für getUserMedia)
4. Teste mit anderem Browser

### Problem: Offline-Modus funktioniert nicht
**Lösung:**
1. Service Worker muss aktiv sein
2. Cache muss gefüllt sein (einmal online laden)
3. Prüfe Cache-Storage in DevTools
4. workbox-precache sollte Dateien enthalten

## Automatisierte Tests (Optional)

### Playwright E2E Tests
```javascript
// tests/mobile-pwa.spec.js
test('PWA Installation Flow', async ({ page, context }) => {
  await page.goto('https://localhost:3000');
  await page.waitForTimeout(3000); // Wait for install prompt
  const installButton = page.locator('text=Installieren');
  await expect(installButton).toBeVisible();
});

test('Template Selection persists', async ({ page }) => {
  await page.goto('https://localhost:3000');
  await page.selectOption('#template-select', { index: 1 });
  await page.reload();
  const selected = await page.inputValue('#template-select');
  expect(selected).not.toBe('');
});
```

### Lighthouse CI
```bash
# .lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:pwa": ["error", {"minScore": 1.0}],
        "categories:accessibility": ["error", {"minScore": 0.9}]
      }
    }
  }
}
```

## Metrics Tracking

Nach Tests dokumentieren:
- [ ] Lighthouse Performance Score: ___
- [ ] Lighthouse PWA Score: ___
- [ ] Initial Load Time: ___ ms
- [ ] Time to Interactive: ___ ms
- [ ] Bundle Size (gzip): ___ KB
- [ ] Service Worker Cache Size: ___ MB
- [ ] Anzahl erfolgreicher Tests: ___ / ___
- [ ] Gefundene Bugs: ___
- [ ] Browser-Kompatibilität: Chrome ✅ Safari ⚠️ Firefox ✅
