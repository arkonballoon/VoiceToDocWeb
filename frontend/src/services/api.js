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
    
    // Header behandeln: FormData hat keine Content-Type, sonst JSON
    const headers = options.body instanceof FormData
      ? (options.headers || {})
      : {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        }
    
    // Timeout aus options verwenden oder Fallback auf Standard-Timeout
    const requestTimeout = options.timeout || this.timeout
    
    const config = {
      ...options,
      headers
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
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // JSON-Parsing fehlgeschlagen, verwende Standard-Fehlermeldung
        }
        throw new Error(errorMessage)
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
      // Für FormData den Content-Type nicht setzen (Browser setzt automatisch mit Boundary)
      options.headers = {} // Überschreibe headers komplett für FormData
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
   * Template-Datei hochladen (Word/Excel)
   * @param {File} file - Template-Datei (.docx oder .xlsx)
   * @param {string} name - Optional: Template-Name
   * @param {string} description - Optional: Beschreibung
   * @returns {Promise<Object>} - Erstelltes Template
   */
  async uploadTemplateFile(file, name = null, description = null) {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    if (description) formData.append('description', description)
    
    const options = {
      method: 'POST',
      headers: {},
      body: formData,
      timeout: 60000 // 60 Sekunden Timeout für Datei-Upload
    }
    
    // Entferne trailing slash von TEMPLATES und füge /upload hinzu
    const templatesEndpoint = API_CONFIG.ENDPOINTS.TEMPLATES.replace(/\/$/, '')
    return this.request(`${templatesEndpoint}/upload`, options)
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
   * Format-spezifische Ausgabedatei herunterladen
   * @param {string} processId - Prozess-ID
   * @returns {Promise<void>} - Löst Download aus
   */
  async downloadProcessedFile(processId) {
    const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.PROCESS}/${processId}/download`
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {}
      })

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // JSON-Parsing fehlgeschlagen, verwende Standard-Fehlermeldung
        }
        throw new Error(errorMessage)
      }

      // Hole Dateinamen aus Content-Disposition Header
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `processed_${processId}`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      // Erstelle Blob und löse Download aus
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      throw error
    }
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
    // Prüfe ob endpoint bereits eine vollständige URL ist
    const url = endpoint.startsWith('ws://') || endpoint.startsWith('wss://') 
      ? endpoint 
      : `${API_CONFIG.WS_URL}${endpoint}`
    
    // Prüfe ob URL gültig ist
    if (!url || url === API_CONFIG.WS_URL) {
      console.error('Ungültige WebSocket-URL:', url)
      callbacks.onError?.(new Error('Ungültige WebSocket-URL'))
      return null
    }
    
    let ws
    try {
      ws = new WebSocket(url)
    } catch (error) {
      console.error('Fehler beim Erstellen der WebSocket-Verbindung:', error)
      callbacks.onError?.(error)
      return null
    }
    
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
      console.log('WebSocket geschlossen:', event.code, event.reason || '<empty string>')
      callbacks.onClose?.(event)
      
      // Automatische Wiederverbindung nur wenn nicht manuell geschlossen
      if (event.code !== 1000) { // 1000 = normaler Close
        this.handleReconnect(url, callbacks)
      }
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
