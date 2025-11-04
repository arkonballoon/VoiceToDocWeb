# Beitragen zu VoiceToDoc

Vielen Dank für dein Interesse an VoiceToDoc!

## Workflow

### Für Bugs

1. **Issue erstellen** mit dem Bug-Report-Template
2. **Branch erstellen**: `fix/kurzbeschreibung`
   ```bash
   git checkout -b fix/mobile-transcript-error
   ```
3. **Änderungen committen**
4. **Pull Request erstellen** und verlinken (`Fixes #123`)

### Für Features

1. **Issue erstellen** (optional, aber empfohlen für größere Features)
2. **Branch erstellen**: `feature/kurzbeschreibung`
   ```bash
   git checkout -b feature/new-api-endpoint
   ```
3. **Änderungen committen**
4. **Pull Request erstellen**

### Für kleine Änderungen

- Direkt PR ohne Issue (Dokumentation, Typos, kleine Fixes)
- Branch: `docs/...` oder `fix/...`

## Commit-Messages

Kurz und klar:
- `feat: Mobile-Transkript-Anzeige hinzugefügt`
- `fix: Syntax-Fehler in TranscriptionService.vue behoben`
- `docs: README mit Mobile-Features erweitert`
- `refactor: API-Routen in separate Dateien ausgelagert`

## Pull Requests

- **Beschreibung**: Kurz beschreiben was geändert wurde
- **Issue-Link**: `Fixes #123` oder `Closes #123` (schließt Issue automatisch)
- **Screenshots**: Bei UI-Änderungen
- **Tests**: Sicherstellen, dass alles funktioniert

## Code-Standards

- **Backend**: PEP 8 (Python), Type Hints wo möglich
- **Frontend**: ESLint, Prettier
- **Commits**: Sinnvolle, aussagekräftige Messages
- **Tests**: Neue Features sollten Tests enthalten (falls möglich)

## Branch-Namenskonventionen

- `feature/kurzbeschreibung` - Neue Features
- `fix/kurzbeschreibung` - Bug-Fixes
- `docs/kurzbeschreibung` - Dokumentation
- `refactor/kurzbeschreibung` - Code-Refactoring

Beispiele:
- `feature/mobile-transcript-display`
- `fix/syntax-error-vue`
- `docs/update-readme`

## Fragen?

Öffne einfach ein Issue mit deiner Frage!

