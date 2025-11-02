<template>
  <div class="page-container">
    <div class="processing-container">
      <!-- Fortschrittsanzeige -->
      <div v-if="isProcessing" class="progress-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progress * 100}%` }"
            :class="{ 'error': status === 'error' }"
          ></div>
        </div>
        <div class="progress-status">
          <span class="progress-message">{{ progressMessage }}</span>
          <span class="progress-percentage">{{ Math.round(progress * 100) }}%</span>
        </div>
      </div>

      <div class="accordion">
 

        <div v-if="processingResult" class="template-editor-section">
          <div class="template-header">
            <h3>Template Ausgabe</h3>
            <div class="validation-badge" 
              :class="{
                'valid': processingResult.validation_result?.is_valid,
                'needs-revision': processingResult.validation_result?.needs_revision
              }"
            >
              {{ getValidationStatus }}
            </div>
          </div>
          
          <QuillEditor
            v-model:content="templateContent"
            contentType="html"
            theme="snow"
            :toolbar="editorToolbar"
            :readonly="true"
            @ready="() => console.log('Editor ready with content:', templateContent)"
          />
        </div>

        <div v-if="processingResult" class="accordion-section" :class="{ 'collapsed': !showResult }">
          <div class="accordion-header" @click="toggleResult">
            <h3>Details zur Verarbeitung</h3>
            <i :class="['fas', showResult ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
          </div>
          <div class="accordion-content" v-show="showResult">
            <!--div v-if="processingResult.processed_text" class="processed-text">
              {{ processingResult.processed_text }}
            </div>
            <div v-if="processingResult.metadata" class="metadata">
              <h4>Metadaten:</h4>
              <p>Modell: {{ processingResult.metadata.model }}</p>
              <p>Tokens verwendet: {{ processingResult.metadata.total_tokens }}</p>
              <p>Response ID: {{ processingResult.metadata.response_id }}</p>
            </div-->
            
            <div v-if="processingResult.validation_result" class="validation-section">
              <h4>Validierung:</h4>
              <div class="validation-status">
                <span 
                  class="status-badge"
                  :class="{
                    'valid': processingResult.validation_result.is_valid,
                    'needs-revision': processingResult.validation_result.needs_revision
                  }"
                >
                  {{ processingResult.validation_result.is_valid ? 'Valide' : 'Nicht Valide' }}
                  {{ processingResult.validation_result.needs_revision ? '- Revision benötigt' : '' }}
                </span>
              </div>
              
              <div v-if="processingResult.validation_result.revision_comments" class="revision-comments">
                <h5>Revision Kommentare:</h5>
                <p>{{ processingResult.validation_result.revision_comments }}</p>
              </div>
              
              <div v-if="processingResult.validation_result.validation_details" class="validation-details">
                <h5>Validierungs-Details:</h5>
                <table class="validation-table">
                  <thead>
                    <tr>
                      <th>Eigenschaft</th>
                      <th>Wert</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(value, key) in processingResult.validation_result.validation_details" :key="key">
                      <td>{{ key }}</td>
                      <td>
                        <span v-if="typeof value === 'boolean'">
                          {{ value ? '✓' : '✗' }}
                        </span>
                        <span v-else-if="Array.isArray(value)">
                          <ul v-if="value.length > 0" class="issue-list">
                            <li v-for="(item, index) in value" :key="index">{{ item }}</li>
                          </ul>
                          <span v-else>Keine Einträge</span>
                        </span>
                        <span v-else-if="typeof value === 'number'">
                          {{ (value * 100).toFixed(1) }}%
                        </span>
                        <span v-else>
                          {{ value }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="processingResult.validation_result.improvement_suggestions" class="improvement-suggestions">
                <h5>Verbesserungsvorschläge</h5>
                <div class="general-feedback">
                  <h6>Allgemeines Feedback:</h6>
                  <p>{{ processingResult.validation_result.improvement_suggestions.general_feedback }}</p>
                </div>
                <div class="specific-suggestions">
                  <h6>Spezifische Vorschläge:</h6>
                  <ul class="suggestion-list">
                    <li v-for="(suggestion, index) in processingResult.validation_result.improvement_suggestions.specific_suggestions" 
                        :key="index">
                      {{ suggestion }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="accordion-section" :class="{ 'collapsed': !showEditor }">
          <div class="accordion-header" @click="toggleEditor">
            <h3>Transkription</h3>
            <i :class="['fas', showEditor ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
          </div>
          <div class="accordion-content" v-show="showEditor">
            <QuillEditor
              v-model:content="transcription"
              contentType="text"
              theme="snow"
              :toolbar="[
                ['bold', 'italic', 'underline'],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                ['clean']
              ]"
            />
          </div>
        </div>        
      </div>
      <div class="template-selection">
        <label for="template-select">Template auswählen:</label>
        <select 
          id="template-select" 
          v-model="selectedTemplateId"
          class="template-select"
        >
          <option v-for="template in templates" :key="template.id" :value="template.id">
            {{ template.name }}
          </option>
        </select>
      </div>

      <button 
        @click="processTemplate" 
        :disabled="isProcessing || !selectedTemplateId || !transcription"
        class="process-button"
      >
        {{ isProcessing ? 'Wird verarbeitet...' : 'Verarbeiten' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useTranscriptionStore } from '@/stores/transcription'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { v4 as uuidv4 } from 'uuid'
import { apiService } from '@/services/api.js'
import { API_CONFIG } from '@/config.js'

export default {
  name: 'TemplateProcessingView',
  components: {
    QuillEditor
  },
  setup() {
    const transcriptionStore = useTranscriptionStore()
    const templates = ref([])
    const selectedTemplateId = ref('')
    const transcription = ref('')
    const isProcessing = ref(false)
    const processingResult = ref(null)
    const error = ref(null)
    const showEditor = ref(true)
    const showResult = ref(true)
    const templateContent = ref('')
    const editorToolbar = [
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['clean']
    ]

    const progress = ref(0)
    const progressMessage = ref('')
    const status = ref('')
    const ws = ref(null)
    
    // Watch für Änderungen im Store
    watch(
      () => transcriptionStore.transcription,
      (newTranscription) => {
        if (newTranscription) {
          transcription.value = newTranscription
        }
      },
      { immediate: true } // Sofort beim Setup ausführen
    )

    const loadTemplates = async () => {
      try {
        templates.value = await apiService.getTemplates()
      } catch (error) {
        console.error('Fehler beim Laden der Templates:', error)
        // Optional: Zeige Fehlermeldung in der UI
        // errorMessage.value = error.message
      }
    }

    const connectWebSocket = (processId) => {
      // Verwende die konfigurierte WebSocket-URL aus config.js
      const wsUrl = `${API_CONFIG.WS_URL}${API_CONFIG.ENDPOINTS.WS_TEMPLATE_PROCESSING}/${processId}`
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onmessage = (event) => {
        const update = JSON.parse(event.data)
        progress.value = update.progress
        progressMessage.value = update.message
        status.value = update.status
        
        if (update.status === 'completed') {
          loadProcessingResult(processId)
        }
      }
      
      ws.value.onerror = (error) => {
        console.error('WebSocket Fehler:', error)
        error.value = 'Verbindungsfehler bei der Template-Verarbeitung'
      }
      
      // Heartbeat senden
      const heartbeat = setInterval(() => {
        if (ws.value && ws.value.readyState === WebSocket.OPEN) {
          ws.value.send('ping')
        }
      }, 30000)
      
      ws.value.onclose = () => {
        clearInterval(heartbeat)
      }
    }
    
    const loadProcessingResult = async (processId) => {
      try {
        processingResult.value = await apiService.getTemplateResult(processId)
      } catch (err) {
        console.error('Fehler:', err)
        error.value = 'Fehler beim Abrufen des Verarbeitungsergebnisses'
      } finally {
        isProcessing.value = false // Status zurücksetzen
      }
    }
    
    const processTemplate = async () => {
      if (!selectedTemplateId.value || !transcription.value) return
      
      isProcessing.value = true
      error.value = null
      progress.value = 0
      progressMessage.value = 'Initialisiere Verarbeitung...'
      
      try {
        const result = await apiService.processTemplate({
          template_id: selectedTemplateId.value,
          transcription: transcription.value
        })

        const { process_id } = result
        connectWebSocket(process_id)
        
      } catch (error) {
        console.error('Fehler:', error)
        error.value = error.message
        isProcessing.value = false
      }
    }

    // Watch für Änderungen in der Transkription
    if (transcriptionStore.transcription) {
      transcription.value = transcriptionStore.transcription
    }

    const toggleEditor = () => {
      showEditor.value = !showEditor.value
    }

    const toggleResult = () => {
      showResult.value = !showResult.value
    }

    // Automatisches Einklappen des Editors nach der Verarbeitung
    watch(processingResult, (newValue) => {
      if (newValue) {
        showEditor.value = false
        showResult.value = true
      }
    })

    // Computed property für Validierungsstatus
    const getValidationStatus = computed(() => {
      if (!processingResult.value?.validation_result) return ''
      if (processingResult.value.validation_result.is_valid) return 'Valide'
      if (processingResult.value.validation_result.needs_revision) return 'Revision benötigt'
      return 'Nicht valide'
    })

    // Watch für processingResult
    watch(processingResult, (newValue) => {
      console.log('ProcessingResult changed:', newValue)
      if (newValue?.processed_text) {
        console.log('Processed text:', newValue.processed_text)
        // Splitte den Text an der Struktur-Markierung
        const parts = newValue.processed_text.split(/^\s*#+\s*struktur\s*$/im)
        console.log('Split parts:', parts)
        if (parts.length > 1) {
          templateContent.value = parts[1].trim()
          console.log('Template content set to:', templateContent.value)
        } else {
          console.log('No structure marker found in text')
          templateContent.value = ''
        }
      } else {
        console.log('No processed_text in result')
        templateContent.value = ''
      }
    })

    onMounted(() => {
      loadTemplates()
    })

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close()
      }
    })

    return {
      templates,
      selectedTemplateId,
      transcription,
      isProcessing,
      processingResult,
      error,
      processTemplate,
      showEditor,
      showResult,
      toggleEditor,
      toggleResult,
      templateContent,
      editorToolbar,
      getValidationStatus,
      progress,
      progressMessage,
      status
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.processing-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.template-selection {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.template-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.transcription-editor {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.process-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  align-self: flex-start;
}

.process-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.result-section {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.processed-text {
  white-space: pre-wrap;
  font-family: monospace;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
}

.metadata {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.transcription-editor :deep(.ql-container) {
  min-height: 200px;
  font-size: 1rem;
}

.transcription-editor :deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.transcription-editor :deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.accordion {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.accordion-section {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f5f5f5;
  cursor: pointer;
  user-select: none;
}

.accordion-header h3 {
  margin: 0;
}

.accordion-content {
  padding: 1rem;
}

.accordion-section.collapsed {
  border-color: #eee;
}

.accordion-section.collapsed .accordion-header {
  border-bottom: none;
}

.validation-section {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #fafafa;
}

.validation-status {
  margin: 1rem 0;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
}

.status-badge.valid {
  background-color: #e6ffe6;
  color: #006400;
  border: 1px solid #00640033;
}

.status-badge.needs-revision {
  background-color: #fff3e6;
  color: #805300;
  border: 1px solid #80530033;
}

.revision-comments {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fff3e6;
  border-radius: 4px;
}

.revision-comments h5 {
  color: #805300;
  margin-top: 0;
}

.validation-details {
  margin-top: 1rem;
}

.validation-details pre {
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
}

.template-editor-section {
  margin-top: 2rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.validation-badge {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
}

.validation-badge.valid {
  background-color: #e6ffe6;
  color: #006400;
  border: 1px solid #00640033;
}

.validation-badge.needs-revision {
  background-color: #fff3e6;
  color: #805300;
  border: 1px solid #80530033;
}

.hidden {
  display: none;
}

:deep(.ql-editor) {
  min-height: 200px;
  font-size: 1rem;
  background-color: #fafafa;
}

:deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  background-color: #f5f5f5;
}

.issue-list {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.improvement-suggestions {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.general-feedback {
  margin-bottom: 1.5rem;
}

.general-feedback h6 {
  color: #495057;
  margin-bottom: 0.5rem;
}

.general-feedback p {
  margin: 0;
  color: #212529;
  line-height: 1.5;
}

.specific-suggestions h6 {
  color: #495057;
  margin-bottom: 0.5rem;
}

.suggestion-list {
  margin: 0;
  padding-left: 20px;
  list-style-type: circle;
}

.suggestion-list li {
  margin-bottom: 0.5rem;
  color: #212529;
  line-height: 1.5;
}

.validation-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.validation-table th,
.validation-table td {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  text-align: left;
}

.validation-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.validation-table td {
  color: #212529;
}

.progress-container {
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-fill.error {
  background-color: #dc3545;
}

.progress-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.progress-message {
  margin-right: 1rem;
}

.progress-percentage {
  font-weight: bold;
}
</style> 
