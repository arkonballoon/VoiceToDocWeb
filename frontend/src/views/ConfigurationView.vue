<template>
  <div class="config-page">
    <h1>Konfiguration</h1>
    
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
    
    <form @submit.prevent="saveConfig" class="config-form">
      <div class="config-grid">
        <!-- Basis-Konfiguration -->
        <div class="config-section">
          <h2>Basis</h2>
          <div class="form-group">
            <label for="app_name">App Name</label>
            <input type="text" id="app_name" v-model="config.APP_NAME">
          </div>
          <div class="form-group">
            <label for="debug">Debug Modus</label>
            <input type="checkbox" id="debug" v-model="config.DEBUG">
          </div>
        </div>

        <!-- Audio-Verarbeitung -->
        <div class="config-section">
          <h2>Audio</h2>
          <div class="form-group compact">
            <label for="min_silence_len">Min. Stille (ms)</label>
            <input type="number" id="min_silence_len" v-model="config.AUDIO_MIN_SILENCE_LEN" min="100" max="2000">
          </div>
          <div class="form-group compact">
            <label for="silence_thresh">Stille-Schwelle (dB)</label>
            <input type="number" id="silence_thresh" v-model="config.AUDIO_SILENCE_THRESH" min="-60" max="0">
          </div>
          <div class="form-group compact">
            <label for="min_chunk">Min. Chunk (ms)</label>
            <input type="number" id="min_chunk" v-model="config.AUDIO_MIN_CHUNK_LENGTH" min="1000" max="10000">
          </div>
          <div class="form-group compact">
            <label for="max_chunk">Max. Chunk (ms)</label>
            <input type="number" id="max_chunk" v-model="config.AUDIO_MAX_CHUNK_LENGTH" min="2000" max="15000">
          </div>
        </div>

        <!-- Transkription -->
        <div class="config-section">
          <h2>Transkription</h2>
          <div class="form-group">
            <label for="whisper_model">CPU Modell</label>
            <select id="whisper_model" v-model="config.WHISPER_MODEL">
              <option v-for="model in whisperModels" :key="model" :value="model">{{ model }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="whisper_model_cuda">GPU Modell</label>
            <select id="whisper_model_cuda" v-model="config.WHISPER_DEVICE_CUDA">
              <option v-for="model in whisperModels" :key="model" :value="model">{{ model }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="max_workers">Max. Workers</label>
            <input type="number" id="max_workers" v-model="config.MAX_WORKERS" min="1" max="10">
          </div>
        </div>

        <!-- Logging -->
        <div class="config-section">
          <h2>Logging</h2>
          <div class="form-group">
            <label for="log_level">Log Level</label>
            <select id="log_level" v-model="config.LOG_LEVEL">
              <option v-for="(value, name) in logLevels" :key="name" :value="value">
                {{ name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="button-group">
        <button type="submit" class="save-button" :disabled="isSaving">
          <span v-if="isSaving">Speichert...</span>
          <span v-else>Speichern</span>
        </button>
        <button type="button" @click="resetConfig" class="reset-button" :disabled="isSaving">
          Zurücksetzen
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { API_CONFIG } from '../config'

export default {
  name: 'ConfigurationView',
  data() {
    return {
      config: {
        APP_NAME: "VoiceToDoc",
        DEBUG: false,
        AUDIO_MIN_SILENCE_LEN: 500,
        AUDIO_SILENCE_THRESH: -32,
        AUDIO_MIN_CHUNK_LENGTH: 2000,
        AUDIO_MAX_CHUNK_LENGTH: 5000,
        WHISPER_MODEL: 'base',
        WHISPER_DEVICE_CUDA: 'large-v3',
        MAX_WORKERS: 3,
        LOG_LEVEL: 20
      },
      whisperModels: ["tiny", "base", "small", "medium", "large", "large-v3"],
      logLevels: {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
      },
      error: null,
      successMessage: null,
      isSaving: false,
      originalConfig: null
    }
  },
  async created() {
    await this.loadConfig()
  },
  methods: {
    async loadConfig() {
      try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CONFIG}`)
        if (!response.ok) throw new Error('Fehler beim Laden der Konfiguration')
        this.config = await response.json()
        this.originalConfig = { ...this.config }
      } catch (error) {
        this.error = `Fehler: ${error.message}`
      }
    },
    async saveConfig() {
      this.isSaving = true
      this.error = null
      this.successMessage = null
      
      try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CONFIG}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.config)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Fehler beim Speichern')
        }
        
        const result = await response.json()
        this.successMessage = "Konfiguration erfolgreich gespeichert"
        this.originalConfig = { ...this.config }
        
        // Erfolgsbenachrichtigung nach 3 Sekunden ausblenden
        setTimeout(() => {
          this.successMessage = null
        }, 3000)
        
      } catch (error) {
        this.error = `Fehler: ${error.message}`
      } finally {
        this.isSaving = false
      }
    },
    resetConfig() {
      if (this.originalConfig) {
        this.config = { ...this.originalConfig }
      }
    }
  }
}
</script>

<style scoped>
.config-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 4rem auto 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.config-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

h2 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.form-group {
  margin-bottom: 0.75rem;
}

.form-group.compact {
  display: grid;
  grid-template-columns: 1fr 80px;
  gap: 0.5rem;
  align-items: center;
}

.form-group.compact label {
  margin: 0;
}

label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

input, select {
  width: 100%;
  padding: 0.35rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

input[type="checkbox"] {
  width: auto;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.save-button {
  background: var(--primary-color);
  color: white;
}

.reset-button {
  background: #f5f5f5;
  color: var(--text-color);
}

.error-message {
  background: #fff3f3;
  color: #d32f2f;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.help-text {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.success-message {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease-in;
}

.save-button:disabled,
.reset-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style> 
