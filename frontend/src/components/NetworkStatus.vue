<template>
  <transition name="slide-down">
    <div v-if="!isOnline" class="network-status offline">
      <div class="status-content">
        <span class="status-icon">📡</span>
        <div class="status-text">
          <strong>Keine Internetverbindung</strong>
          <span class="status-detail">
            {{ queuedUploads > 0 ? `${queuedUploads} Uploads warten` : 'Aufnahmen werden lokal gespeichert' }}
          </span>
        </div>
        <button v-if="queuedUploads > 0" @click="retryUploads" class="retry-button">
          Wiederholen
        </button>
      </div>
    </div>
  </transition>

  <transition name="slide-down">
    <div v-if="isReconnecting" class="network-status reconnecting">
      <div class="status-content">
        <span class="status-icon">🔄</span>
        <div class="status-text">
          <strong>Verbindung wird wiederhergestellt...</strong>
          <span class="status-detail">Versuch {{ reconnectAttempt }} von {{ maxReconnectAttempts }}</span>
        </div>
      </div>
    </div>
  </transition>

  <transition name="slide-down">
    <div v-if="justReconnected" class="network-status online">
      <div class="status-content">
        <span class="status-icon">✓</span>
        <div class="status-text">
          <strong>Verbindung wiederhergestellt</strong>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NetworkStatus',
  props: {
    queuedUploads: {
      type: Number,
      default: 0
    },
    reconnectAttempt: {
      type: Number,
      default: 0
    },
    maxReconnectAttempts: {
      type: Number,
      default: 3
    }
  },
  emits: ['retry'],
  setup(props, { emit }) {
    const isOnline = ref(navigator.onLine)
    const isReconnecting = ref(false)
    const justReconnected = ref(false)
    let reconnectedTimeout = null

    const handleOnline = () => {
      isOnline.value = true
      isReconnecting.value = false
      justReconnected.value = true

      // Verstecke "Verbindung wiederhergestellt" nach 3 Sekunden
      clearTimeout(reconnectedTimeout)
      reconnectedTimeout = setTimeout(() => {
        justReconnected.value = false
      }, 3000)

      console.log('Netzwerk online')
    }

    const handleOffline = () => {
      isOnline.value = false
      justReconnected.value = false
      console.log('Netzwerk offline')
    }

    const retryUploads = () => {
      emit('retry')
    }

    onMounted(() => {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)
    })

    onUnmounted(() => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      clearTimeout(reconnectedTimeout)
    })

    return {
      isOnline,
      isReconnecting,
      justReconnected,
      retryUploads
    }
  }
}
</script>

<style scoped>
.network-status {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999;
  padding: 0.75rem 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.network-status.offline {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.network-status.reconnecting {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.network-status.online {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.status-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.status-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status-text strong {
  font-size: 0.95rem;
  font-weight: 600;
}

.status-detail {
  font-size: 0.85rem;
  opacity: 0.9;
}

.retry-button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.retry-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.retry-button:active {
  transform: scale(0.98);
}

/* Animationen */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* Mobile Anpassungen */
@media (max-width: 768px) {
  .network-status {
    padding: 0.65rem 0.75rem;
  }

  .status-content {
    gap: 0.75rem;
  }

  .status-icon {
    font-size: 1.25rem;
  }

  .status-text strong {
    font-size: 0.9rem;
  }

  .status-detail {
    font-size: 0.8rem;
  }

  .retry-button {
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .status-content {
    flex-wrap: wrap;
  }

  .retry-button {
    width: 100%;
    margin-top: 0.5rem;
  }
}

/* Reconnecting Animation */
.network-status.reconnecting .status-icon {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
