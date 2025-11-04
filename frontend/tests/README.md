# Frontend Tests

Dieses Verzeichnis enthält Tests für das VoiceToDoc Frontend.

## Struktur

```
tests/
├── unit/                # Unit Tests (TODO)
│   └── components/
└── e2e/                 # End-to-End Tests (optional, TODO)
```

## Test-Setup (TODO)

### Vitest Setup

```bash
# Vitest installieren
npm install --save-dev vitest @vue/test-utils

# Test-Skript in package.json hinzufügen
"test": "vitest",
"test:coverage": "vitest --coverage"
```

### Beispiel-Test-Struktur

```javascript
// tests/unit/components/TranscriptionService.spec.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TranscriptionService from '@/components/TranscriptionService.vue'

describe('TranscriptionService', () => {
  it('should render correctly', () => {
    const wrapper = mount(TranscriptionService)
    expect(wrapper.exists()).toBe(true)
  })
})
```

## TODO

- [ ] Vitest konfigurieren
- [ ] Komponenten-Tests
- [ ] Service-Tests (api.js)
- [ ] Store-Tests (transcription.js)
- [ ] E2E-Tests (optional, Playwright/Cypress)

