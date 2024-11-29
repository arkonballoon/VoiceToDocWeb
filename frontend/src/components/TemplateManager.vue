<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Template-Verwaltung</h2>
    </div>

    <div class="page-content">
      <div v-if="!showEditDialog && !showCreateDialog" class="template-section">
        <div class="template-list">
          <div v-for="template in templates" 
               :key="template.id" 
               class="template-card">
            <span class="template-name">{{ template.name }}</span>
            <div class="template-actions">
              <button @click="editTemplate(template)" class="edit-button" title="Bearbeiten">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteTemplate(template.id)" class="delete-button" title="Löschen">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
        <button @click="showCreateDialog = true" class="create-button">
          <i class="fas fa-plus"></i> Neues Template
        </button>
      </div>

      <!-- Edit/Create Template Section -->
      <div v-else class="editor-section">
        <div class="editor-header">
          <h3>{{ showCreateDialog ? 'Neues Template erstellen' : 'Template bearbeiten' }}</h3>
          <button @click="closeDialog" class="back-button">
            <i class="fas fa-arrow-left"></i> Zurück
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="editor-form">
          <div class="form-group editor-container">
            <label>Inhalt:</label>
            <MdEditor
              v-model="currentTemplate.content"
              language="de-DE"
              :theme="editorTheme"
              previewTheme="github"
              :toolbars="toolbars"
              @onChange="handleEditorChange"
            />
          </div>
          <div class="form-fields">
            <div class="form-group">
              <label>Name:</label>
              <input v-model="currentTemplate.name" required>
            </div>
            <div class="form-group">
              <label>Beschreibung:</label>
              <textarea v-model="currentTemplate.description"></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeDialog" class="cancel-button">Abbrechen</button>
              <button type="submit" class="save-button">
                {{ showCreateDialog ? 'Erstellen' : 'Speichern' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '../config.js'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

export default {
  name: 'TemplateManager',
  components: {
    MdEditor
  },
  data() {
    return {
      templates: [],
      showCreateDialog: false,
      showEditDialog: false,
      currentTemplate: {
        name: '',
        description: '',
        content: ''
      },
      editorTheme: 'light',
      toolbars: [
        'bold', 'italic', 'strikethrough', '|',
        'header', 'list', 'ordered-list', '|',
        'link', 'table', '|',
        'preview', 'fullscreen'
      ]
    }
  },
  methods: {
    async loadTemplates() {
      try {
        const response = await fetch(`${API_BASE_URL}/templates`)
        if (!response.ok) throw new Error('Fehler beim Laden der Templates')
        this.templates = await response.json()
      } catch (error) {
        console.error('Fehler:', error)
      }
    },
    editTemplate(template) {
      this.currentTemplate = { ...template }
      this.showEditDialog = true
    },
    closeDialog() {
      this.showCreateDialog = false
      this.showEditDialog = false
      this.currentTemplate = { name: '', description: '', content: '' }
    },
    handleEditorChange(content) {
      this.currentTemplate.content = content
    },
    async handleSubmit() {
      try {
        const url = this.showCreateDialog 
          ? `${API_BASE_URL}/templates/`
          : `${API_BASE_URL}/templates/${this.currentTemplate.id}`
        
        const response = await fetch(url, {
          method: this.showCreateDialog ? 'POST' : 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.currentTemplate)
        })

        if (!response.ok) throw new Error('Fehler beim Speichern des Templates')
        
        await this.loadTemplates()
        this.closeDialog()
      } catch (error) {
        console.error('Fehler:', error)
      }
    }
  },
  mounted() {
    this.loadTemplates()
  }
}
</script>

<style scoped>
.page-container {
  padding: 4rem 0 0 0;
  width: 100vw;
  min-height: 100vh;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.page-content {
  width: 100%;
  padding: 0;
  margin: 0;
}

.editor-section {
  position: absolute;
  left: 0;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  padding: 1rem;
  background: white;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--secondary-color);
  cursor: pointer;
  padding: 0.5rem;
}

.editor-form {
  width: 100%;
  margin: 0;
  padding: 0;
  text-align: left;
}

.form-group {
  margin-bottom: 0.75rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: bold;
}

.form-group input {
  height: 32px;
}

.form-group textarea {
  height: 48px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

:deep(.md-editor) {
  margin: 0;
  width: 100%;
  text-align: left;
}

:deep(.md-editor-area) {
  margin: 0;
  padding: 0;
}

:deep(.md-editor-input),
:deep(.md-editor-preview) {
  padding: 0 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.save-button {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.template-section {
  width: 100%;
}

.template-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.template-card {
  width: 100%;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

:deep(.md-editor-preview) {
  font-size: 0.8rem;
}

:deep(.md-editor-preview h1) {
  font-size: 1.2rem;
}

:deep(.md-editor-preview h2) {
  font-size: 1.1rem;
}

:deep(.md-editor-preview h3) {
  font-size: 1rem;
}

:deep(.md-editor-preview h4) {
  font-size: 0.9rem;
}

:deep(.md-editor-preview p) {
  font-size: 0.8rem;
  line-height: 1.3;
}

:deep(.md-editor-preview li) {
  font-size: 0.8rem;
}

:deep(.md-editor-input) {
  font-size: 0.8rem;
  text-align: left;
}

.editor-container {
  margin-bottom: 2rem;
}

.form-fields {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

:deep(.md-editor) {
  margin: 0;
  width: 100%;
  height: calc(70vh - 100px);
}

.form-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style> 