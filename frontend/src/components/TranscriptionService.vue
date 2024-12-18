<template>
  <div class="transcription-service">
    <div class="upload-section">
      <div class="upload-card">
        <h2>Audio-Datei hochladen oder aufnehmen</h2>
        
        <!-- Mikrofon Auswahl -->
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
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="transcript" class="editor-section">
      <div class="editor-header">
        <h3>Transkription</h3>
        <div class="confidence-badge" v-if="confidence">
          Konfidenz: {{ (confidence * 100).toFixed(2) }}%
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
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { useTranscriptionStore } from '../stores/transcription'
import RecordRTC from 'recordrtc'

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
        toolbar: toolbarOptions
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

    onMounted(() => {
      loadAudioDevices()
    })

    const appendTranscription = (newText) => {
      if (!newText) return

      // Füge Leerzeichen zwischen Texten ein, wenn nötig
      if (transcript.value && !transcript.value.endsWith(' ') && !newText.startsWith(' ')) {
        transcript.value += ' '
      }
      
      transcript.value += newText
      editableTranscript.value = transcript.value
      transcriptionStore.setTranscription(transcript.value, confidence.value)
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

        const response = await fetch('http://192.168.178.67:8000/upload_audio', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Upload fehlgeschlagen: ${response.status} - ${errorText}`)
        }

        const result = await response.json()
        
        // Füge neue Transkription hinzu statt zu überschreiben
        appendTranscription(result.text)
        confidence.value = result.confidence

        lastUploadTime.value = now

      } catch (err) {
        console.error('Fehler beim automatischen Upload:', err)
      }
    }

    const startRecording = async () => {
      try {
        // Setze Transkription zurück beim Start einer neuen Aufnahme
        transcript.value = ''
        editableTranscript.value = ''
        confidence.value = null
        error.value = null

        mediaStream.value = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            deviceId: selectedMicrophone.value,
            channelCount: 1,
            sampleRate: 16000,
            echoCancellation: true,
            noiseSuppression: true
          }
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
            error.value = 'Fehler beim Beenden der Aufnahme'
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
        
        const response = await fetch('http://192.168.178.67:8000/upload_audio', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Upload fehlgeschlagen: ${response.status} - ${errorText}`)
        }

        const result = await response.json()
        
        transcript.value = result.text
        editableTranscript.value = result.text
        confidence.value = result.confidence
        transcriptionStore.setTranscription(result.text, result.confidence)
        
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
      handleFileSelect,
      handleDrop,
      uploadFile,
      handleTranscriptChange,
      toggleRecording
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
}

.confidence-badge {
  display: inline-block;
  background: var(--secondary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

:deep(.ql-container) {
  min-height: 200px;
  font-size: 16px;
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
</style>
