<template>
  <div class="transcription-service">
    <div class="upload-section">
      <div class="upload-card">
        <h2>Audio-Datei hochladen oder aufnehmen</h2>

        <!-- Mobile Focus Mode -->
        <div v-if="isMobileLike" class="mobile-focus">
          <div class="template-selection">
            <label for="template-select">Template:</label>
            <select 
              id="template-select"
              v-model="selectedTemplateId" 
              class="template-select"
            >
              <option value="">Kein Template (nur transkribieren)</option>
              <option 
                v-for="template in templates" 
                :key="template.id" 
                :value="template.id"
              >
                {{ template.name }}
              </option>
            </select>
          </div>

          <button 
            @click="toggleRecording" 
            :class="['record-button', { 'recording': isRecording }]"
            :disabled="isLoading"
          >
            {{ isRecording ? 'Aufnahme stoppen' : 'Aufnahme starten' }}
          </button>

          <div v-if="isRecording" class="recording-status" role="status" aria-live="polite">
            Aufnahme läuft... (Automatische Transkription alle 5 Sekunden)
          </div>

          <button 
            @click="handleTranscriptAction" 
            :disabled="isProcessing || !transcript"
            class="upload-button"
          >
            {{ isProcessing ? 'Wird verarbeitet...' 
               : (selectedTemplateId 
                  ? 'Fertig – Template verarbeiten' 
                  : 'Transkript speichern/teilen') }}
          </button>
        </div>

        <!-- Mobile Transkript-Anzeige -->
        <div v-if="isMobileLike && (transcript || isRecording)" class="mobile-transcript-view" ref="mobileTranscriptRef">
          <div class="mobile-transcript-header">
            <h3>Transkription</h3>
            <div class="mobile-transcript-actions">
              <button 
                v-if="canShare && transcript" 
                @click="shareTranscript" 
                class="share-button"
                title="Transkription teilen"
              >
                📤 Teilen
              </button>
              <div class="confidence-badge" v-if="confidence && !isRecording">
                Konfidenz: {{ (confidence * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
          <div class="mobile-transcript-text" v-html="mobileTranscriptContent"></div>
        </div>

        <!-- Desktop UI -->
        <template v-else>
          <!-- Template Auswahl -->
          <div class="template-selection">
            <label for="template-select">Template für Verarbeitung:</label>
            <select 
              id="template-select"
              v-model="selectedTemplateId" 
              class="template-select"
            >
              <option value="">Kein Template (nur transkribieren)</option>
              <option 
                v-for="template in templates" 
                :key="template.id" 
                :value="template.id"
              >
                {{ template.name }}
              </option>
            </select>
          </div>

          <!-- Mikrofon Auswahl (nur Desktop) -->
          <select 
            v-model="selectedMicrophone" 
            class="microphone-select"
            :disabled="isRecording"
          >
            <option value="">Mikrofon auswählen...</option>
            <option 
              v-for="device in audioDevices" 
              :key="device.deviceId" 
              :value="device.deviceId"
            >
              {{ device.label || `Mikrofon ${device.deviceId}` }}
            </option>
          </select>
          
          <!-- Aufnahme Button -->
          <button 
            @click="toggleRecording" 
            :class="['record-button', { 'recording': isRecording }]"
            :disabled="isLoading || !selectedMicrophone"
          >
            {{ isRecording ? 'Aufnahme stoppen' : 'Aufnahme starten' }}
          </button>

          <div v-if="isRecording" class="recording-status">
            Aufnahme läuft... (Automatische Transkription alle 5 Sekunden)
          </div>

          <div class="upload-area" 
               :class="{ 'drag-over': isDragging }"
               @drop.prevent="handleDrop"
               @dragover.prevent
               @dragenter.prevent="isDragging = true"
               @dragleave.prevent="isDragging = false">
            <input 
              type="file" 
              @change="handleFileSelect" 
              accept="audio/*"
              ref="fileInput"
              class="file-input"
            >
            <div class="upload-placeholder">
              <i class="upload-icon">📁</i>
              <p>{{ selectedFile ? selectedFile.name : 'Datei hierher ziehen oder klicken zum Auswählen' }}</p>
              <span class="file-types">Unterstützte Formate: WAV, MP3</span>
            </div>
          </div>
          <button 
            @click="uploadFile" 
            :disabled="!selectedFile || isLoading"
            class="upload-button"
          >
            {{ isLoading ? 'Wird verarbeitet...' : 'Transkribieren' }}
          </button>
        </template>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="!isMobileLike && transcript" class="editor-section">
      <div class="editor-header">
        <h3>Transkription</h3>
        <div class="editor-actions">
          <button 
            v-if="canShare" 
            @click="shareTranscript" 
            class="share-button"
            title="Transkription teilen"
          >
            📤 Teilen
          </button>
          <div class="confidence-badge" v-if="confidence">
            Konfidenz: {{ (confidence * 100).toFixed(2) }}%
          </div>
        </div>
      </div>
      <QuillEditor
        v-model:content="editableTranscript"
        @update:content="handleTranscriptChange"
        contentType="html"
        :toolbar="toolbarOptions"
        theme="snow"
        :options="editorOptions"
      />
    </div>

    <div v-if="isProcessing" class="progress-container">
      <div class="progress-status">
        {{ progressMessage }}
      </div>
    </div>
    
    <button 
      v-if="!isMobileLike"
      @click="processTemplate" 
      :disabled="isProcessing || !transcript"
      :class="{ 'processing': isProcessing }"
    >
      {{ isProcessing ? progressMessage : 'Verarbeiten' }}
    </button>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { useTranscriptionStore } from '../stores/transcription'
import RecordRTC from 'recordrtc'
import { apiService, wsService } from '../services/api.js'
import { API_CONFIG, WS_CONFIG, AUDIO_CONFIG } from '../config.js'

export default {
  name: 'TranscriptionService',
  components: {
    QuillEditor
  },
  setup() {
    const transcriptionStore = useTranscriptionStore()
    const selectedFile = ref(null)
    const transcript = ref('')
    const confidence = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const isDragging = ref(false)
    const editableTranscript = ref('')
    const isRecording = ref(false)
    const recorder = ref(null)
    const audioDevices = ref([])
    const selectedMicrophone = ref('')
    const mediaStream = ref(null)
    const lastUploadTime = ref(0)
    const currentBlob = ref(null)
    const processedText = ref('')
    const isProcessing = ref(false)
    const currentProcessId = ref(null)
    const socket = ref(null)
    const progressMessage = ref('')
    const progressStatus = ref('')
    const templates = ref([])
    const selectedTemplateId = ref(localStorage.getItem('lastSelectedTemplate') || '')
    const canShare = ref(navigator.share !== undefined)
    const isMobileLike = ref(false)
    let reconnectAttempts = 0
    let heartbeatInterval = null

    const toolbarOptions = [
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['clean']
    ]

    const editorOptions = {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['clean'],
          ['timestamp'] // Custom Button für Zeitstempel
        ]
      },
      formats: {
        // Erlaubte Formate definieren
        header: true,
        bold: true,
        italic: true,
        underline: true,
        strike: true,
        list: true,
        align: true,
        timestamp: true // Custom Format für Zeitstempel
      }
    }

    const loadAudioDevices = async () => {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true })
        const devices = await navigator.mediaDevices.enumerateDevices()
        audioDevices.value = devices.filter(device => device.kind === 'audioinput')
        navigator.mediaDevices.addEventListener('devicechange', loadAudioDevices)
      } catch (err) {
        error.value = `Mikrofon-Zugriff fehlgeschlagen: ${err.message}`
      }
    }

    const loadTemplates = async () => {
      try {
        templates.value = await apiService.getTemplates()
      } catch (err) {
        console.error('Fehler beim Laden der Templates:', err)
        templates.value = []
      }
    }

    // Watch für Template-Auswahl - speichere in LocalStorage
    watch(selectedTemplateId, (newTemplateId) => {
      if (newTemplateId) {
        localStorage.setItem('lastSelectedTemplate', newTemplateId)
      } else {
        localStorage.removeItem('lastSelectedTemplate')
      }
    })

    onMounted(() => {
      const computeIsMobileLike = () => {
        try {
          const coarse = window.matchMedia('(pointer: coarse)').matches
          const narrow = window.matchMedia('(max-width: 768px)').matches
          const uaMobile = /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(navigator.userAgent)
          const touchCapable = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0)
          // Touch allein (Convertible/Laptop) nicht ausreichen lassen – mit "narrow" koppeln
          isMobileLike.value = coarse || narrow || uaMobile || (touchCapable && narrow)
        } catch (_) {
          isMobileLike.value = false
        }
      }
      computeIsMobileLike()
      try {
        const mqCoarse = window.matchMedia('(pointer: coarse)')
        const mqNarrow = window.matchMedia('(max-width: 768px)')
        mqCoarse.addEventListener?.('change', computeIsMobileLike)
        mqNarrow.addEventListener?.('change', computeIsMobileLike)
        window.addEventListener?.('resize', computeIsMobileLike)
      } catch (_) { /* noop */ }
      loadAudioDevices()
      loadTemplates()
      connectWebSocket()
    })

    onUnmounted(() => {
      if (socket.value) {
        socket.value.close()
      }
      clearInterval(heartbeatInterval)
      try {
        window.removeEventListener?.('resize', () => {})
      } catch (_) { /* noop */ }
    })

    const mobileTranscriptRef = ref(null)

    // Computed property für Mobile-Transkript-Anzeige
    const mobileTranscriptContent = computed(() => {
      if (transcript.value) {
        return transcript.value
      }
      if (isRecording.value) {
        return '<p style="color: #666; font-style: italic;">Transkription läuft... Bitte warten.</p>'
      }
      return ''
    })

    const appendTranscription = (newText) => {
      if (!newText) return
      
      const formattedText = processTranscription(newText)
      
      if (transcript.value) {
        // Füge neuen Text am Ende ein
        transcript.value += formattedText
      } else {
        transcript.value = formattedText
      }
      
      editableTranscript.value = transcript.value
      transcriptionStore.setTranscription(transcript.value, confidence.value)
      
      // Auto-Scroll zum Ende für Mobile-View
      if (isMobileLike.value && mobileTranscriptRef.value) {
        setTimeout(() => {
          const textElement = mobileTranscriptRef.value?.querySelector('.mobile-transcript-text')
          if (textElement) {
            textElement.scrollTop = textElement.scrollHeight
          }
        }, 100)
      }
    }

    const uploadRecording = async () => {
      try {
        // Prüfe ob genügend Zeit seit dem letzten Upload vergangen ist
        const now = Date.now()
        if (now - lastUploadTime.value < 4000) {
          return
        }

        // Prüfe ob ein aktueller Blob vorhanden ist
        if (!currentBlob.value || currentBlob.value.size === 0) {
          console.warn('Kein Audio-Blob verfügbar')
          return
        }

        const file = new File([currentBlob.value], 'aufnahme.wav', { 
          type: 'audio/wav',
          lastModified: Date.now()
        })

        const formData = new FormData()
        formData.append('file', file)

        console.log('Sende Audio-Chunk:', {
          größe: file.size,
          typ: file.type,
          zeit: new Date().toISOString()
        })

        const result = await apiService.uploadAudio(file)
        
        // Füge neue Transkription hinzu statt zu überschreiben
        appendTranscription(result.text)
        confidence.value = result.confidence

        lastUploadTime.value = now

      } catch (err) {
        console.error('Fehler beim automatischen Upload:', err)
        // User-freundliche Fehlermeldung
        if (err.message.includes('Timeout') || err.name === 'AbortError') {
          error.value = 'Upload-Timeout: Die Transkription dauert länger als erwartet. Bitte erneut versuchen.'
        } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          error.value = 'Netzwerkfehler: Bitte Internetverbindung prüfen.'
        } else {
          error.value = `Upload-Fehler: ${err.message}`
        }
      }
    }

    const startRecording = async () => {
      try {
        // Setze Transkription zurück beim Start einer neuen Aufnahme
        transcript.value = ''
        editableTranscript.value = ''
        confidence.value = null
        error.value = null

        const audioConstraints = {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
        if (!isMobileLike.value && selectedMicrophone.value) {
          audioConstraints.deviceId = selectedMicrophone.value
        }
        mediaStream.value = await navigator.mediaDevices.getUserMedia({ 
          audio: audioConstraints
        })

        recorder.value = new RecordRTC(mediaStream.value, {
          type: 'audio',
          mimeType: 'audio/wav',
          recorderType: RecordRTC.StereoAudioRecorder,
          numberOfAudioChannels: 1,
          desiredSampRate: 16000,
          timeSlice: 5000, // Auf 5 Sekunden gesetzt für synchrone Chunks
          ondataavailable: async (blob) => {
            console.log('Neuer Audio-Chunk verfügbar:', blob.size, 'bytes')
            // Speichere den aktuellen Blob
            currentBlob.value = blob
            // Versuche sofort hochzuladen
            await uploadRecording()
          }
        })

        recorder.value.startRecording()
        isRecording.value = true
        lastUploadTime.value = Date.now()

      } catch (err) {
        error.value = `Mikrofon-Zugriff fehlgeschlagen: ${err.message}`
        console.error('Aufnahmefehler:', err)
      }
    }

    const stopRecording = () => {
      if (recorder.value) {
        recorder.value.stopRecording(async () => {
          try {
            // Warte kurz, bis der letzte Chunk verarbeitet wurde
            await new Promise(resolve => setTimeout(resolve, 500))
            
            const finalBlob = await recorder.value.getBlob()
            const file = new File([finalBlob], 'aufnahme.wav', { 
              type: 'audio/wav',
              lastModified: Date.now()
            })
            selectedFile.value = file
            error.value = null

            console.log('Finale Aufnahme:', {
              größe: file.size,
              typ: file.type
            })

            // Führe einen letzten Upload durch
            currentBlob.value = finalBlob
            await uploadRecording()

          } catch (err) {
            console.error('Fehler beim Stoppen der Aufnahme:', err)
            // User-freundliche Fehlermeldung
            if (err.message.includes('Timeout') || err.name === 'AbortError') {
              error.value = 'Upload-Timeout: Die finale Transkription dauert länger als erwartet. Bitte erneut versuchen.'
            } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
              error.value = 'Netzwerkfehler beim Finalen Upload: Bitte Internetverbindung prüfen.'
            } else {
              error.value = `Fehler beim Beenden der Aufnahme: ${err.message}`
            }
          } finally {
            // Cleanup
            if (mediaStream.value) {
              mediaStream.value.getTracks().forEach(track => track.stop())
              mediaStream.value = null
            }
            recorder.value = null
            currentBlob.value = null
          }
        })
        isRecording.value = false
      }
    }

    const toggleRecording = () => {
      if (isRecording.value) {
        stopRecording()
      } else {
        startRecording()
      }
    }

    watch(transcript, (newValue) => {
      if (newValue) {
        editableTranscript.value = newValue
      }
    })

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file && isValidAudioFile(file)) {
        selectedFile.value = file
        error.value = null
      } else {
        error.value = 'Bitte wählen Sie eine gültige Audio-Datei (WAV, MP3)'
      }
    }

    const handleDrop = (event) => {
      isDragging.value = false
      const file = event.dataTransfer.files[0]
      if (file && isValidAudioFile(file)) {
        selectedFile.value = file
        error.value = null
      } else {
        error.value = 'Bitte wählen Sie eine gültige Audio-Datei (WAV, MP3)'
      }
    }

    const isValidAudioFile = (file) => {
      const validTypes = ['.wav', '.mp3']
      return validTypes.some(type => file.name.toLowerCase().endsWith(type))
    }

    const uploadFile = async () => {
      if (!selectedFile.value) return

      isLoading.value = true
      error.value = null
      transcript.value = ''
      confidence.value = null

      const formData = new FormData()
      formData.append('file', selectedFile.value)

      try {
        console.log('Sende Datei:', selectedFile.value.name, 'Größe:', selectedFile.value.size)
        
        const result = await apiService.uploadAudio(selectedFile.value)
        
        // Verarbeite den Text vor dem Setzen
        const formattedText = processTranscription(result.text)
        transcript.value = formattedText
        editableTranscript.value = formattedText
        confidence.value = result.confidence
        transcriptionStore.setTranscription(formattedText, result.confidence)
        
      } catch (err) {
        error.value = `Fehler: ${err.message}`
        console.error('Upload error:', err)
      } finally {
        isLoading.value = false
      }
    }

    const handleTranscriptChange = (content) => {
      editableTranscript.value = content
      transcriptionStore.setTranscription(content)
    }

    // Funktion zum Verarbeiten der Transkription
    const processTranscription = (text) => {
      if (!text) return ''
      
      // Stelle sicher, dass der Text als HTML geparst wird
      const parser = new DOMParser()
      const doc = parser.parseFromString(text, 'text/html')
      
      // Füge Klassen für bessere Formatierung hinzu
      doc.querySelectorAll('p[data-timestamp]').forEach(p => {
        p.classList.add('transcript-segment')
      })
      
      return doc.body.innerHTML
    }

    // WebSocket-Verbindung aufbauen
    const connectWebSocket = () => {
      const clientId = Math.random().toString(36).substring(7)
      const wsEndpoint = `${API_CONFIG.ENDPOINTS.WS_TEMPLATE_PROCESSING}/${clientId}`
      
      console.log('Verbinde mit WebSocket:', wsEndpoint)
      
      if (socket.value?.readyState === WebSocket.OPEN) {
        console.log('WebSocket bereits verbunden')
        return
      }

      socket.value = wsService.connect(wsEndpoint, {
        onOpen: () => {
          console.log('WebSocket verbunden')
          reconnectAttempts = 0
          error.value = null
          
          // Heartbeat starten
          clearInterval(heartbeatInterval)
          heartbeatInterval = setInterval(() => {
            if (socket.value?.readyState === WebSocket.OPEN) {
              socket.value.send('ping')
            }
          }, WS_CONFIG.HEARTBEAT_INTERVAL)
        },
        onMessage: async (data) => {
          console.log('WebSocket Update:', data)
          
          switch(data.status) {
            case 'started':
              updateProgress('started', 'Starte Verarbeitung...')
              break
            case 'extracting':
              updateProgress('extracting', 'Extrahiere Informationen...')
              break
            case 'filling':
              updateProgress('filling', 'Verarbeite Template...')
              break
            case 'validating':
              updateProgress('validating', 'Validiere Template...')
              break
            case 'completed':
              updateProgress('completed', 'Verarbeitung abgeschlossen')
              await handleTemplateProcessingComplete(currentProcessId.value)
              isProcessing.value = false  // Button-Status zurücksetzen
              break
            case 'error':
              error.value = data.message
              isProcessing.value = false
              break
          }
        },
        onError: (error) => {
          console.error('WebSocket-Fehler beim Verarbeiten der Nachricht:', error)
        },
        onClose: () => {
          console.log('WebSocket geschlossen')
          clearInterval(heartbeatInterval)
        },
        onMaxReconnectAttempts: () => {
          error.value = 'Verbindung zum Server verloren. Bitte Seite neu laden.'
        }
      })
    }

    // Ergebnis der Verarbeitung abrufen
    const handleTemplateProcessingComplete = async (processId) => {
      try {
        const result = await apiService.getTemplateResult(processId)
        processedText.value = result.processed_text
        isProcessing.value = false
      } catch (err) {
        console.error('Fehler:', err)
        error.value = 'Fehler beim Abrufen des Verarbeitungsergebnisses'
        isProcessing.value = false
      }
    }

    const updateProgress = (status, message) => {
      progressStatus.value = status
      progressMessage.value = message
      console.log(`Status: ${status}, Message: ${message}`)
    }

    const processTemplate = async () => {
      if (!transcript.value || !selectedTemplateId.value) return

      isProcessing.value = true
      error.value = null
      progressMessage.value = 'Starte Verarbeitung...'

      try {
        const processId = `proc_${Date.now()}`
        currentProcessId.value = processId

        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PROCESS}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            template_id: selectedTemplateId.value,
            transcription: transcript.value,
            process_id: processId
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Fehler bei der Template-Verarbeitung')
        }

        // WebSocket wird Updates über den Fortschritt senden
      } catch (err) {
        error.value = `Fehler: ${err.message}`
        console.error('Template processing error:', err)
        isProcessing.value = false
      }
    }

    const saveTranscript = async () => {
      if (!transcript.value) return

      // Konvertiere HTML zu Plain Text
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = transcript.value
      const plainText = tempDiv.textContent || tempDiv.innerText || ''

      // Versuche Web Share API zu verwenden
      if (navigator.share) {
        try {
          await navigator.share({
            title: 'Transkription',
            text: plainText,
          })
          console.log('Transkription erfolgreich geteilt')
          return
        } catch (err) {
          // Falls Teilen abgebrochen oder nicht verfügbar, Download anbieten
          if (err.name === 'AbortError') {
            return // Benutzer hat abgebrochen
          }
        }
      }

      // Fallback: Download als Textdatei
      try {
        const blob = new Blob([plainText], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `transkription-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Fehler beim Download:', err)
        error.value = 'Fehler beim Speichern der Transkription'
      }
    }

    const handleTranscriptAction = async () => {
      if (!transcript.value) return

      if (selectedTemplateId.value) {
        // Mit Template: Template verarbeiten
        await processTemplate()
      } else {
        // Ohne Template: Transkript speichern/teilen
        await saveTranscript()
      }
    }

    const shareTranscript = async () => {
      if (!navigator.share) {
        console.log('Web Share API nicht verfügbar')
        return
      }

      try {
        // Konvertiere HTML zu Plain Text für besseres Teilen
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = editableTranscript.value || transcript.value
        const plainText = tempDiv.textContent || tempDiv.innerText || ''

        await navigator.share({
          title: 'Transkription',
          text: plainText,
        })
        console.log('Transkription erfolgreich geteilt')
      } catch (err) {
        // Benutzer hat Teilen abgebrochen oder Fehler
        if (err.name !== 'AbortError') {
          console.error('Fehler beim Teilen:', err)
        }
      }
    }

    return {
      selectedFile,
      transcript,
      confidence,
      isLoading,
      error,
      isDragging,
      editableTranscript,
      isRecording,
      toolbarOptions,
      editorOptions,
      audioDevices,
      selectedMicrophone,
      templates,
      selectedTemplateId,
      canShare,
      isMobileLike,
      mobileTranscriptRef,
      mobileTranscriptContent,
      handleFileSelect,
      handleDrop,
      uploadFile,
      handleTranscriptChange,
      toggleRecording,
      processTranscription,
      processedText,
      isProcessing,
      currentProcessId,
      socket,
      progressMessage,
      progressStatus,
      processTemplate,
      handleTranscriptAction,
      saveTranscript,
      shareTranscript
    }
  }
}
</script>

<style scoped>
.transcription-service {
  padding: 2rem 0;
}

.upload-section {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  padding: 2rem;
}

.microphone-select {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  font-size: 1rem;
}

.microphone-select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.recording-status {
  text-align: center;
  color: #dc3545;
  margin-bottom: 1rem;
  font-weight: bold;
}

.record-button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 1rem;
  width: 100%;
  transition: all 0.3s ease;
}

.record-button.recording {
  background: #dc3545;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.record-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  position: relative;
  margin: 1rem 0;
  transition: all 0.3s ease;
}

.upload-area.drag-over {
  border-color: var(--primary-color);
  background-color: rgba(255, 184, 0, 0.1);
}

.upload-area:hover {
  border-color: var(--primary-color);
}

.file-input {
  opacity: 0;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.upload-placeholder {
  pointer-events: none;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.file-types {
  display: block;
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.upload-button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
  transition: background 0.3s ease;
}

.upload-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Mobile Focus Mode */
.mobile-focus {
  display: grid;
  gap: 1rem;
}
.mobile-focus .template-selection {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

/* Mobile Transkript-View */
.mobile-transcript-view {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.mobile-transcript-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.mobile-transcript-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #111827);
}

.mobile-transcript-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mobile-transcript-text {
  flex: 1;
  overflow-y: auto;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 0.5rem 0;
  font-size: 0.95rem;
  color: var(--text-color, #111827);
  min-height: 50px;
}

.mobile-transcript-text::-webkit-scrollbar {
  width: 6px;
}

.mobile-transcript-text::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.mobile-transcript-text::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.mobile-transcript-text::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.mobile-transcript-text :deep(p) {
  margin: 0.5rem 0;
  padding: 0.25rem 0;
}

.mobile-transcript-text :deep(.transcript-segment) {
  background: #fff;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border-radius: 4px;
  border-left: 3px solid var(--primary-color, #10B981);
}

/* ——— Mobile Focus: Typografie, Abstände, Brandfarben, Button-Hierarchie ——— */
.mobile-focus {
  /* Brandfarben lokal definieren (nicht global überschreiben) */
  --brand-green: #10B981;
  --brand-green-darker: #059669;
  --brand-purple: #7C3AED;
  --brand-purple-ink: #5B21B6;
}

.mobile-focus {
  font-size: 16px;
}

.mobile-focus .template-selection label {
  font-weight: 600;
  color: var(--text-color, #111827);
}

.mobile-focus .template-select,
.mobile-focus .record-button,
.mobile-focus .upload-button {
  min-height: 52px;
  font-size: 1rem;
  border-radius: 10px;
}

/* Primärer CTA: Aufnahme */
.mobile-focus .record-button {
  background: var(--brand-green);
  border: none;
  color: #fff;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.25);
}
.mobile-focus .record-button:hover {
  background: var(--brand-green-darker);
}
.mobile-focus .record-button.recording {
  background: #dc3545;
  box-shadow: 0 0 0 4px rgba(220, 53, 69, 0.15);
}

/* Sekundärer CTA: Verarbeiten */
.mobile-focus .upload-button {
  background: transparent;
  color: var(--brand-purple);
  border: 2px solid var(--brand-purple);
}
.mobile-focus .upload-button:hover {
  color: #fff;
  background: var(--brand-purple);
  border-color: var(--brand-purple);
}
.mobile-focus .upload-button:disabled {
  opacity: 0.6;
  border-color: #ccc;
  color: #999;
}

/* Recording-Status als Badge mit Pulsindikator */
.mobile-focus .recording-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 999px;
  background: rgba(220, 53, 69, 0.1);
  color: #b91c1c;
  font-weight: 600;
  width: fit-content;
}
.mobile-focus .recording-status::before {
  content: '';
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #dc3545;
  box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.6);
  animation: pulse-dot 1.6s infinite;
}
@keyframes pulse-dot {
  0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.6); }
  70% { box-shadow: 0 0 0 12px rgba(220, 53, 69, 0); }
  100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
}

/* Card-Optik für Mobile-Template Section etwas stärker */
.mobile-focus .template-selection {
  border: 1px solid #e5e7eb;
}

.error-message {
  background: #fff2f2;
  color: #d63031;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
}

.editor-section {
  margin-top: 2rem;
  max-width: 800px;
  margin: 2rem auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.share-button {
  background: #10B981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.share-button:hover {
  background: #059669;
  transform: translateY(-1px);
}

.share-button:active {
  transform: translateY(0);
}

.confidence-badge {
  display: inline-block;
  background: var(--secondary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  white-space: nowrap;
}

:deep(.ql-container) {
  min-height: 200px;
  font-size: 16px;
  line-height: 1.5;
  font-family: inherit;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

:deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

:deep(.transcript-segment) {
  position: relative;
  padding: 0.5rem;
  margin: 0.25rem 0;
  border-radius: 4px;
  background: #f8f9fa;
}

:deep(.transcript-segment:hover) {
  background: #e9ecef;
}

:deep(.transcript-segment[data-timestamp]):after {
  content: attr(data-timestamp);
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  font-size: 0.8rem;
  color: #6c757d;
  opacity: 0.7;
}

:deep(.ql-container) {
  min-height: 200px;
  font-size: 16px;
  line-height: 1.5;
  font-family: inherit;
}

:deep(.ql-editor) {
  padding: 1rem;
}

:deep(.ql-editor p) {
  margin-bottom: 0.5rem;
}

.progress-container {
  margin: 1rem 0;
  padding: 1rem;
  background-color: var(--background-secondary);
  border-radius: 4px;
}

.progress-status {
  text-align: center;
  color: var(--text-color);
  font-size: 0.9rem;
}

button.processing {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Template Selection Styles */
.template-selection {
  margin-bottom: 1.5rem;
}

.template-selection label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color);
  font-weight: 500;
  font-size: 0.95rem;
}

.template-select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.template-select:hover {
  border-color: var(--primary-color);
}

.template-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Mobile Optimizations */
@media (max-width: 768px) {
  .transcription-service {
    padding: 1rem 0;
  }

  .upload-section {
    max-width: 100%;
    padding: 0 1rem;
  }

  .upload-card {
    padding: 1.5rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.08);
  }

  .upload-card h2 {
    font-size: 1.3rem;
    margin-bottom: 1.5rem;
  }

  /* Touch-optimierte Buttons */
  .record-button,
  .upload-button,
  .microphone-select,
  .template-select {
    min-height: 48px;
    font-size: 1rem;
    padding: 0.75rem 1rem;
  }

  /* Template-Auswahl prominent auf Mobile */
  .template-selection {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }

  .template-selection label {
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
  }

  /* Upload-Bereich kompakter */
  .upload-area {
    padding: 1.5rem 1rem;
    margin: 1rem 0;
  }

  .upload-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .upload-placeholder p {
    font-size: 0.9rem;
    margin: 0.5rem 0;
  }

  .file-types {
    font-size: 0.8rem;
  }

  /* Mobile Transkript-View */
  .mobile-transcript-view {
    margin-top: 1rem;
    padding: 0.75rem;
    max-height: 350px;
  }

  .mobile-transcript-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding-bottom: 0.75rem;
  }

  .mobile-transcript-header h3 {
    font-size: 1rem;
  }

  .mobile-transcript-actions {
    width: 100%;
    justify-content: space-between;
  }

  .mobile-transcript-text {
    font-size: 0.9rem;
    padding: 0.25rem 0;
  }

  /* Editor auf Mobile */
  .editor-section {
    margin: 1.5rem 0;
    padding: 0 1rem;
  }

  .editor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .editor-actions {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
  }

  .share-button {
    flex: 0 0 auto;
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }

  .confidence-badge {
    font-size: 0.85rem;
    padding: 0.4rem 0.8rem;
  }

  /* Quill Editor auf Mobile anpassen */
  :deep(.ql-container) {
    min-height: 250px;
    font-size: 16px; /* Verhindert Auto-Zoom auf iOS */
  }

  :deep(.ql-toolbar) {
    position: sticky;
    top: 0;
    z-index: 10;
    background: white;
  }

  :deep(.ql-editor) {
    padding: 0.75rem;
  }

  /* Progress Container */
  .progress-container {
    margin: 1rem;
    padding: 0.75rem;
  }

  .progress-status {
    font-size: 0.85rem;
  }

  /* Error Messages */
  .error-message {
    margin: 1rem;
    padding: 0.75rem;
    font-size: 0.9rem;
  }

  /* Recording Status */
  .recording-status {
    font-size: 0.9rem;
    padding: 0.5rem;
  }
}

/* Touch Feedback für alle Buttons */
@media (hover: none) and (pointer: coarse) {
  .record-button:active,
  .upload-button:active {
    transform: scale(0.98);
    opacity: 0.9;
  }

  .microphone-select:active,
  .template-select:active {
    background-color: #f8f9fa;
  }
}

/* Landscape Mode auf Mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .upload-card {
    padding: 1rem;
  }

  .upload-card h2 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }

  :deep(.ql-container) {
    min-height: 150px;
  }
}

/* Small screens (< 480px) */
@media (max-width: 480px) {
  .upload-card h2 {
    font-size: 1.2rem;
  }

  .template-selection,
  .upload-area {
    border-radius: 6px;
  }

  :deep(.ql-toolbar .ql-formats) {
    margin-right: 8px !important;
  }
}
</style>
