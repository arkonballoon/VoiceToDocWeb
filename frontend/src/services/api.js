/**
 * Zentrale API-Service-Klasse für alle Backend-Kommunikation
 * Bietet eine einheitliche Schnittstelle für HTTP- und WebSocket-Verbindungen
 */

import { API_CONFIG, WS_CONFIG } from '../config.js'

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL
    this.timeout = API_CONFIG.TIMEOUTS.REQUEST
  }

  /**
   * Generische HTTP-Anfrage mit Fehlerbehandlung
   * @param {string} endpoint - API-Endpunkt
   * @param {Object} options - Fetch-Optionen
   * @returns {Promise<Object>} - Antwort-Daten
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const headers = {}
    
    // Nur Content-Type setzen, wenn nicht explizit übersprungen
    if (!options.skipContentType) {
      headers['Content-Type'] = 'application/json'
    }
    
    // Timeout aus options verwenden oder Fallback auf Standard-Timeout
    const requestTimeout = options.timeout || this.timeout
    
    const config = {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), requestTimeout)

      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Anfrage-Timeout: Der Server antwortet nicht rechtzeitig')
      }
      throw error
    }
  }

  /**
   * GET-Anfrage
   * @param {string} endpoint - API-Endpunkt
   * @param {Object} params - Query-Parameter
   * @returns {Promise<Object>} - Antwort-Daten
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    return this.request(url, { method: 'GET' })
  }

  /**
   * POST-Anfrage
   * @param {string} endpoint - API-Endpunkt
   * @param {Object} data - Zu sendende Daten
   * @returns {Promise<Object>} - Antwort-Daten
   */
  async post(endpoint, data = null) {
    const options = { method: 'POST', headers: {} }
    
    if (data instanceof FormData) {
      // Für FormData KEINEN Content-Type setzen (Browser setzt automatisch mit boundary)
      options.skipContentType = true
      options.body = data
    } else if (data) {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(data)
    }

    return this.request(endpoint, options)
  }

  /**
   * PUT-Anfrage
   * @param {string} endpoint - API-Endpunkt
   * @param {Object} data - Zu sendende Daten
   * @returns {Promise<Object>} - Antwort-Daten
   */
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  /**
   * DELETE-Anfrage
   * @param {string} endpoint - API-Endpunkt
   * @returns {Promise<Object>} - Antwort-Daten
   */
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }

  // Spezifische API-Methoden

  /**
   * Audio-Datei hochladen
   * @param {File} file - Audio-Datei
   * @returns {Promise<Object>} - Transkriptionsergebnis
   */
  async uploadAudio(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    // Audio-Upload braucht längeres Timeout (Transkription + LLM-Processing)
    const options = { 
      method: 'POST', 
      headers: {},
      skipContentType: true,
      body: formData,
      timeout: 120000 // 2 Minuten Timeout für Audio-Verarbeitung
    }
    
    return this.request(API_CONFIG.ENDPOINTS.UPLOAD, options)
  }

  /**
   * Alle Templates abrufen
   * @returns {Promise<Array>} - Template-Liste
   */
  async getTemplates() {
    return this.get(API_CONFIG.ENDPOINTS.TEMPLATES)
  }

  /**
   * Template erstellen
   * @param {Object} template - Template-Daten
   * @returns {Promise<Object>} - Erstelltes Template
   */
  async createTemplate(template) {
    return this.post(API_CONFIG.ENDPOINTS.TEMPLATES, template)
  }

  /**
   * Template aktualisieren
   * @param {string} id - Template-ID
   * @param {Object} template - Template-Daten
   * @returns {Promise<Object>} - Aktualisiertes Template
   */
  async updateTemplate(id, template) {
    return this.put(`${API_CONFIG.ENDPOINTS.TEMPLATES}${id}`, template)
  }

  /**
   * Template löschen
   * @param {string} id - Template-ID
   * @returns {Promise<Object>} - Bestätigung
   */
  async deleteTemplate(id) {
    return this.delete(`${API_CONFIG.ENDPOINTS.TEMPLATES}${id}`)
  }

  /**
   * Template-Verarbeitung starten
   * @param {Object} request - Verarbeitungsanfrage
   * @returns {Promise<Object>} - Prozess-ID
   */
  async processTemplate(request) {
    return this.post(API_CONFIG.ENDPOINTS.PROCESS, request)
  }

  /**
   * Verarbeitungsergebnis abrufen
   * @param {string} processId - Prozess-ID
   * @returns {Promise<Object>} - Verarbeitungsergebnis
   */
  async getTemplateResult(processId) {
    return this.get(`${API_CONFIG.ENDPOINTS.PROCESS}/${processId}`)
  }

  /**
   * Konfiguration abrufen
   * @returns {Promise<Object>} - Aktuelle Konfiguration
   */
  async getConfig() {
    return this.get(API_CONFIG.ENDPOINTS.CONFIG)
  }

  /**
   * Konfiguration aktualisieren
   * @param {Object} config - Neue Konfiguration
   * @returns {Promise<Object>} - Aktualisierte Konfiguration
   */
  async updateConfig(config) {
    return this.put(API_CONFIG.ENDPOINTS.CONFIG, config)
  }
}

/**
 * WebSocket-Service für Echtzeit-Kommunikation
 */
class WebSocketService {
  constructor() {
    this.connections = new Map()
    this.reconnectAttempts = new Map()
  }

  /**
   * WebSocket-Verbindung erstellen
   * @param {string} endpoint - WebSocket-Endpunkt
   * @param {Object} callbacks - Event-Callbacks
   * @returns {WebSocket} - WebSocket-Instanz
   */
  connect(endpoint, callbacks = {}) {
    const url = `${API_CONFIG.WS_URL}${endpoint}`
    const ws = new WebSocket(url)
    
    ws.onopen = (event) => {
      console.log('WebSocket verbunden:', url)
      this.reconnectAttempts.set(url, 0)
      callbacks.onOpen?.(event)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        callbacks.onMessage?.(data, event)
      } catch (error) {
        console.error('Fehler beim Parsen der WebSocket-Nachricht:', error)
        callbacks.onError?.(error)
      }
    }

    ws.onerror = (event) => {
      console.error('WebSocket-Fehler:', event)
      callbacks.onError?.(event)
    }

    ws.onclose = (event) => {
      console.log('WebSocket geschlossen:', event.code, event.reason)
      callbacks.onClose?.(event)
      
      // Automatische Wiederverbindung
      this.handleReconnect(url, callbacks)
    }

    this.connections.set(url, ws)
    return ws
  }

  /**
   * Wiederverbindung handhaben
   * @param {string} url - WebSocket-URL (vollständige URL)
   * @param {Object} callbacks - Event-Callbacks
   */
  handleReconnect(url, callbacks) {
    const attempts = this.reconnectAttempts.get(url) || 0
    
    if (attempts < WS_CONFIG.MAX_RECONNECT_ATTEMPTS) {
      const delay = WS_CONFIG.RECONNECT_DELAY * Math.pow(2, attempts)
      console.log(`Wiederverbindung in ${delay}ms (Versuch ${attempts + 1}/${WS_CONFIG.MAX_RECONNECT_ATTEMPTS})`)
      
      setTimeout(() => {
        this.reconnectAttempts.set(url, attempts + 1)
        // Extrahiere den Endpoint aus der vollständigen URL
        // z.B. "wss://v2d.arkondev.de/ws/..." -> "/ws/..."
        // oder "wss://v2d.arkondev.de/api/ws/..." -> "/ws/..." (falls noch altes Format)
        let endpoint = url.replace(/^wss?:\/\/[^/]+/, '')
        // Entferne /api/ Prefix falls vorhanden (für WebSocket sollte es nicht da sein)
        endpoint = endpoint.replace(/^\/api\//, '/')
        this.connect(endpoint, callbacks)
      }, delay)
    } else {
      console.error('Maximale Wiederverbindungsversuche erreicht')
      callbacks.onMaxReconnectAttempts?.()
    }
  }

  /**
   * WebSocket-Verbindung schließen
   * @param {string} url - WebSocket-URL
   */
  disconnect(url) {
    const ws = this.connections.get(url)
    if (ws) {
      ws.close()
      this.connections.delete(url)
      this.reconnectAttempts.delete(url)
    }
  }

  /**
   * Alle Verbindungen schließen
   */
  disconnectAll() {
    this.connections.forEach((ws, url) => {
      ws.close()
    })
    this.connections.clear()
    this.reconnectAttempts.clear()
  }
}

// Singleton-Instanzen exportieren
export const apiService = new ApiService()
export const wsService = new WebSocketService()

// Für Rückwärtskompatibilität
export default apiService
