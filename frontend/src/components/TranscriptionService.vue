<template>
  <div class="transcription-service">
    <div class="upload-section">
      <div class="upload-card">
        <h2>Audio-Datei hochladen</h2>
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
            <span class="file-types">Unterstützte Formate: WebM, WAV, MP3</span>
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
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

export default {
  name: 'TranscriptionService',
  components: {
    QuillEditor
  },
  data() {
    return {
      selectedFile: null,
      transcript: '',
      confidence: null,
      isLoading: false,
      error: null,
      isDragging: false,
      editableTranscript: '',
      toolbarOptions: [
        ['bold', 'italic', 'underline', 'strike'],
        ['blockquote', 'code-block'],
        [{ 'header': 1 }, { 'header': 2 }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'script': 'sub'}, { 'script': 'super' }],
        [{ 'indent': '-1'}, { 'indent': '+1' }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
        ['clean']
      ],
      editorOptions: {
        theme: 'snow',
        modules: {
          toolbar: [
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
        }
      }
    }
  },
  watch: {
    transcript: {
      handler(newTranscript) {
        if (newTranscript) {
          this.editableTranscript = `<p>${newTranscript.replace(/\n/g, '</p><p>')}</p>`;
        }
      },
      immediate: true
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file && this.isValidAudioFile(file)) {
        this.selectedFile = file
        this.error = null
      } else {
        this.error = 'Bitte wählen Sie eine gültige Audio-Datei (WebM, WAV, MP3)'
      }
    },
    handleDrop(event) {
      this.isDragging = false
      const file = event.dataTransfer.files[0]
      if (file && this.isValidAudioFile(file)) {
        this.selectedFile = file
        this.error = null
      } else {
        this.error = 'Bitte wählen Sie eine gültige Audio-Datei (WebM, WAV, MP3)'
      }
    },
    isValidAudioFile(file) {
      const validTypes = ['.webm', '.wav', '.mp3']
      return validTypes.some(type => file.name.toLowerCase().endsWith(type))
    },
    async uploadFile() {
      if (!this.selectedFile) return

      this.isLoading = true
      this.error = null
      this.transcript = ''
      this.confidence = null

      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        console.log('Sende Datei:', this.selectedFile.name)
        
        const response = await fetch('http://192.168.178.67:8000/upload_audio', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Upload fehlgeschlagen: ${response.status} - ${errorText}`)
        }

        const result = await response.json()
        
        this.transcript = result.text
        this.confidence = result.confidence
        
      } catch (err) {
        this.error = `Fehler: ${err.message}`
        console.error('Upload error:', err)
      } finally {
        this.isLoading = false
      }
    },
    handleTranscriptChange(text) {
      // Entferne HTML-Tags für reinen Text
      const plainText = text.replace(/<[^>]*>/g, '\n').replace(/\n{2,}/g, '\n').trim();
      this.$emit('transcript-changed', plainText);
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