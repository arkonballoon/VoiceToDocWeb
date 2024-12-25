// API Konfiguration
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'localhost:8000'
export const API_BASE_URL = `http://${BACKEND_URL}`
export const WS_BASE_URL = `ws://${BACKEND_URL}`

// Andere Konfigurationsoptionen
export const HEARTBEAT_INTERVAL = 30000 // 30 Sekunden
export const MAX_RECONNECT_ATTEMPTS = 3 