<template>
  <div class="page-container">
    <div class="processing-container">

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
                          {{ value.join(', ') }}
                        </span>
                        <span v-else-if="typeof value === 'object'">
                          <table>
                            <tbody>
                              <tr v-for="(subValue, subKey) in value" :key="subKey">
                                <td>{{ subKey }}</td>
                                <td>{{ subValue }}</td>
                              </tr>
                            </tbody>
                          </table>
                        </span>
                        <span v-else>
                          {{ value }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useTranscriptionStore } from '@/stores/transcription'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

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
        const response = await fetch('http://localhost:8000/templates')
        if (!response.ok) throw new Error('Fehler beim Laden der Templates')
        templates.value = await response.json()
      } catch (error) {
        console.error('Fehler beim Laden der Templates:', error)
      }
    }

    const processTemplate = async () => {
      if (!selectedTemplateId.value || !transcription.value) return
      
      isProcessing.value = true
      error.value = null
      
      try {
        const response = await fetch('http://localhost:8000/process_template', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            template_id: selectedTemplateId.value,
            transcription: transcription.value
          })
        })

        if (!response.ok) {
          throw new Error('Fehler bei der Verarbeitung')
        }

        processingResult.value = await response.json()
        console.log('Verarbeitungsergebnis:', processingResult.value) // Debug-Log
      } catch (error) {
        console.error('Fehler:', error)
        error.value = error.message
      } finally {
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
      getValidationStatus
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
</style> 