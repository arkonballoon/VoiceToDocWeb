<template>
  <div v-if="showPrompt" class="install-prompt">
    <div class="prompt-content">
      <div class="prompt-icon">📱</div>
      <div class="prompt-text">
        <h3>VoiceToDoc installieren</h3>
        <p>Installiere die App für schnelleren Zugriff und bessere Performance.</p>
      </div>
      <div class="prompt-actions">
        <button @click="install" class="install-button">
          Installieren
        </button>
        <button @click="dismiss" class="dismiss-button">
          Später
        </button>
      </div>
      <button @click="dismissForever" class="close-button" aria-label="Schließen">
        ×
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'InstallPrompt',
  setup() {
    const showPrompt = ref(false)
    const deferredPrompt = ref(null)

    onMounted(() => {
      // Prüfe ob Installation bereits abgelehnt wurde
      const dismissed = localStorage.getItem('pwa-install-dismissed')
      if (dismissed === 'forever') {
        return
      }

      // Höre auf beforeinstallprompt Event
      window.addEventListener('beforeinstallprompt', (e) => {
        // Verhindere Standard Chrome Mini-Infobar
        e.preventDefault()
        deferredPrompt.value = e

        // Zeige eigenen Prompt nach kurzer Verzögerung
        setTimeout(() => {
          showPrompt.value = true
        }, 3000) // 3 Sekunden Verzögerung
      })

      // Prüfe ob App bereits installiert ist
      window.addEventListener('appinstalled', () => {
        showPrompt.value = false
        deferredPrompt.value = null
        console.log('PWA wurde installiert')
      })
    })

    const install = async () => {
      if (!deferredPrompt.value) return

      // Zeige nativen Installationsdialog
      deferredPrompt.value.prompt()

      // Warte auf Benutzer-Antwort
      const { outcome } = await deferredPrompt.value.userChoice
      console.log(`Benutzer-Antwort: ${outcome}`)

      // Setze deferredPrompt zurück
      deferredPrompt.value = null
      showPrompt.value = false
    }

    const dismiss = () => {
      showPrompt.value = false
      // Zeige Prompt nach 7 Tagen wieder
      const dismissedUntil = Date.now() + (7 * 24 * 60 * 60 * 1000)
      localStorage.setItem('pwa-install-dismissed-until', dismissedUntil.toString())
    }

    const dismissForever = () => {
      showPrompt.value = false
      localStorage.setItem('pwa-install-dismissed', 'forever')
    }

    return {
      showPrompt,
      install,
      dismiss,
      dismissForever
    }
  }
}
</script>

<style scoped>
.install-prompt {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 1rem;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.prompt-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.15);
  padding: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  align-items: center;
  position: relative;
}

.prompt-icon {
  font-size: 2.5rem;
  grid-row: 1 / 3;
}

.prompt-text {
  grid-column: 2;
}

.prompt-text h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #1a202c;
}

.prompt-text p {
  margin: 0;
  font-size: 0.9rem;
  color: #4a5568;
}

.prompt-actions {
  grid-column: 3;
  grid-row: 1 / 3;
  display: flex;
  gap: 0.5rem;
}

.install-button {
  background: #10B981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.install-button:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.install-button:active {
  transform: translateY(0);
}

.dismiss-button {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.dismiss-button:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.close-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-button:hover {
  background: #f3f4f6;
  color: #4b5563;
}

/* Mobile Anpassungen */
@media (max-width: 768px) {
  .install-prompt {
    padding: 0.5rem;
  }

  .prompt-content {
    grid-template-columns: auto 1fr;
    gap: 0.75rem;
    padding: 1rem;
  }

  .prompt-icon {
    font-size: 2rem;
    grid-row: 1;
  }

  .prompt-text {
    grid-column: 2;
    grid-row: 1;
  }

  .prompt-text h3 {
    font-size: 1rem;
  }

  .prompt-text p {
    font-size: 0.85rem;
  }

  .prompt-actions {
    grid-column: 1 / 3;
    grid-row: 2;
    justify-content: stretch;
  }

  .install-button,
  .dismiss-button {
    flex: 1;
    padding: 0.65rem 1rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .prompt-actions {
    flex-direction: column-reverse;
  }

  .install-button,
  .dismiss-button {
    width: 100%;
  }
}
</style>
