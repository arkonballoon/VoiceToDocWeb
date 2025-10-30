// Zentrale API-Konfiguration
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'localhost:8000'
const PROTOCOL = import.meta.env.VITE_PROTOCOL || 'http'
const WS_PROTOCOL = import.meta.env.VITE_WS_PROTOCOL || 'ws'

// API-Konfiguration
export const API_CONFIG = {
  BASE_URL: `${PROTOCOL}://${BACKEND_URL}`,
  WS_URL: `${WS_PROTOCOL}://${BACKEND_URL}`,
  ENDPOINTS: {
    UPLOAD: '/upload_audio',
    TEMPLATES: '/templates/',
    PROCESS: '/process_template',
    CONFIG: '/config',
    WS: '/ws',
    WS_TEMPLATE_PROCESSING: '/ws/template_processing'
  },
  TIMEOUTS: {
    UPLOAD: 30000, // 30 Sekunden
    REQUEST: 10000, // 10 Sekunden
    WS_RECONNECT: 5000 // 5 Sekunden
  }
}

// WebSocket-Konfiguration
export const WS_CONFIG = {
  HEARTBEAT_INTERVAL: parseInt(import.meta.env.VITE_WS_HEARTBEAT_INTERVAL) || 30000,
  MAX_RECONNECT_ATTEMPTS: parseInt(import.meta.env.VITE_WS_MAX_RECONNECT_ATTEMPTS) || 3,
  RECONNECT_DELAY: parseInt(import.meta.env.VITE_WS_RECONNECT_DELAY) || 5000
}

// Audio-Konfiguration
export const AUDIO_CONFIG = {
  SUPPORTED_FORMATS: ['audio/wav', 'audio/mp3', 'audio/webm'],
  MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE) || 50 * 1024 * 1024, // 50MB
  CHUNK_SIZE: parseInt(import.meta.env.VITE_AUDIO_CHUNK_SIZE) || 5000, // 5 Sekunden
  SAMPLE_RATE: parseInt(import.meta.env.VITE_AUDIO_SAMPLE_RATE) || 16000
}

// UI-Konfiguration
export const UI_CONFIG = {
  THEME: import.meta.env.VITE_THEME || 'light',
  LANGUAGE: import.meta.env.VITE_LANGUAGE || 'de',
  AUTO_SAVE_INTERVAL: parseInt(import.meta.env.VITE_AUTO_SAVE_INTERVAL) || 30000
}

// Legacy-Exports für Rückwärtskompatibilität
export const API_BASE_URL = API_CONFIG.BASE_URL
export const WS_BASE_URL = API_CONFIG.WS_URL
export const HEARTBEAT_INTERVAL = WS_CONFIG.HEARTBEAT_INTERVAL
export const MAX_RECONNECT_ATTEMPTS = WS_CONFIG.MAX_RECONNECT_ATTEMPTS 
