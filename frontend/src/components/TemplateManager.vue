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
            <div class="template-info">
              <span class="template-name">{{ template.name }}</span>
              <span v-if="template.file_format" class="template-format">
                {{ template.file_format.toUpperCase() }}
              </span>
              <span v-if="template.placeholders && Object.keys(template.placeholders).length > 0" 
                    class="template-placeholders">
                {{ Object.keys(template.placeholders).length }} Platzhalter
              </span>
            </div>
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
        <div class="create-actions">
          <button @click="showCreateDialog = true" class="create-button">
            <i class="fas fa-plus"></i> Neues Template (Markdown)
          </button>
          <label class="upload-button">
            <i class="fas fa-upload"></i> Word/Excel hochladen
            <input 
              type="file" 
              accept=".docx,.xlsx" 
              @change="handleFileUpload"
              style="display: none"
            />
          </label>
        </div>
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
          <!-- Platzhalter-Konfiguration -->
          <div v-if="currentTemplate.placeholders && Object.keys(currentTemplate.placeholders).length > 0" 
               class="placeholders-section">
            <h4>Platzhalter-Konfiguration</h4>
            <p class="placeholder-info">
              Konfiguriere die Prompts für jeden Platzhalter. Diese werden verwendet, um Informationen aus der Transkription zu extrahieren.
            </p>
            <table class="placeholders-table">
              <thead>
                <tr>
                  <th>Platzhalter</th>
                  <th>Prompt</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(prompt, placeholder) in currentTemplate.placeholders" :key="placeholder">
                  <td class="placeholder-name">{{ placeholder }}</td>
                  <td>
                    <textarea 
                      v-model="currentTemplate.placeholders[placeholder]"
                      class="prompt-input"
                      rows="2"
                    ></textarea>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Warnung wenn keine Platzhalter vorhanden -->
          <div v-if="currentTemplate.file_format && currentTemplate.file_format !== 'markdown' && (!currentTemplate.placeholders || Object.keys(currentTemplate.placeholders).length === 0)" 
               class="placeholder-warning">
            <h4>⚠️ Keine Platzhalter gefunden</h4>
            <p>
              In dieser {{ currentTemplate.file_format.toUpperCase() }}-Datei wurden keine Platzhalter im Format <code>&#123;&#123;feldname&#125;&#125;</code> gefunden.
            </p>
            <p>
              <strong>So fügen Sie Platzhalter hinzu:</strong>
            </p>
            <ul>
              <li>Fügen Sie Platzhalter im Format <code>&#123;&#123;feldname&#125;&#125;</code> in Ihre Excel-Datei ein</li>
              <li>Platzhalter können als Text in Zellen stehen, z.B.: <code>&#123;&#123;projektname&#125;&#125;</code></li>
              <li>Oder in Formeln verwendet werden, z.B.: <code>="Projekt: "&amp;&#123;&#123;projektname&#125;&#125;</code></li>
            </ul>
            <p>
              Laden Sie die Datei anschließend erneut hoch, um die Platzhalter zu erkennen.
            </p>
          </div>
          
          <div class="form-group editor-container" v-if="!currentTemplate.file_format || currentTemplate.file_format === 'markdown'">
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
          <div v-else class="file-info">
            <p><strong>Dateiformat:</strong> {{ currentTemplate.file_format.toUpperCase() }}</p>
            <p v-if="currentTemplate.file_path"><strong>Datei:</strong> {{ currentTemplate.file_path }}</p>
            <p class="info-text">Dieses Template wurde aus einer {{ currentTemplate.file_format.toUpperCase() }}-Datei erstellt. Bearbeiten Sie die Platzhalter-Prompts oben, um die Extraktion anzupassen.</p>
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
import { apiService } from '../services/api.js'
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
        content: '',
        placeholders: {},
        file_format: null,
        file_path: null
      },
      editorTheme: 'light',
      toolbars: [
        'bold', 'italic', 'strikethrough', '|',
        'header', 'list', 'ordered-list', '|',
        'link', 'table', '|',
        'preview', 'fullscreen'
      ],
      isUploading: false
    }
  },
  methods: {
    async loadTemplates() {
      try {
        this.templates = await apiService.getTemplates()
      } catch (error) {
        console.error('Fehler beim Laden der Templates:', error)
        this.templates = []
      }
    },
    editTemplate(template) {
      this.currentTemplate = { 
        ...template,
        placeholders: template.placeholders ? { ...template.placeholders } : {}
      }
      this.showEditDialog = true
    },
    closeDialog() {
      this.showCreateDialog = false
      this.showEditDialog = false
      this.currentTemplate = { 
        name: '', 
        description: '', 
        content: '',
        placeholders: {},
        file_format: null,
        file_path: null
      }
    },
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // Prüfe Dateiformat
      const extension = file.name.split('.').pop().toLowerCase()
      if (!['docx', 'xlsx'].includes(extension)) {
        alert('Nur .docx (Word) und .xlsx (Excel) Dateien werden unterstützt.')
        return
      }
      
      this.isUploading = true
      try {
        const template = await apiService.uploadTemplateFile(file)
        await this.loadTemplates()
        // Öffne Bearbeitungsdialog für das neue Template
        this.editTemplate(template)
        
        // Prüfe ob Warnung vorhanden ist (keine Platzhalter gefunden)
        if (template._warning) {
          alert('⚠️ ' + template._warning)
        } else if (template.placeholders && Object.keys(template.placeholders).length > 0) {
          alert(`✅ Template erfolgreich hochgeladen! ${Object.keys(template.placeholders).length} Platzhalter wurden automatisch erkannt.`)
        } else {
          alert('✅ Template erfolgreich hochgeladen!')
        }
      } catch (error) {
        console.error('Fehler beim Hochladen:', error)
        alert('❌ Fehler beim Hochladen der Datei: ' + (error.message || 'Unbekannter Fehler'))
      } finally {
        this.isUploading = false
        // Reset file input
        event.target.value = ''
      }
    },
    handleEditorChange(content) {
      this.currentTemplate.content = content
    },
    async handleSubmit() {
      try {
        const templateData = {
          name: this.currentTemplate.name,
          description: this.currentTemplate.description,
          content: this.currentTemplate.content
        }
        
        // Füge Platzhalter hinzu, wenn vorhanden
        if (this.currentTemplate.placeholders && Object.keys(this.currentTemplate.placeholders).length > 0) {
          templateData.placeholders = this.currentTemplate.placeholders
        }
        
        if (this.showCreateDialog) {
          await apiService.createTemplate(templateData)
        } else {
          await apiService.updateTemplate(this.currentTemplate.id, templateData)
        }
        
        await this.loadTemplates()
        this.closeDialog()
      } catch (error) {
        console.error('Fehler:', error)
        alert('Fehler beim Speichern: ' + (error.message || 'Unbekannter Fehler'))
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

.create-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.upload-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--secondary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.upload-button:hover {
  opacity: 0.9;
}

.template-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.template-format {
  font-size: 0.75rem;
  color: #666;
  background: #f0f0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.template-placeholders {
  font-size: 0.75rem;
  color: #666;
}

.placeholders-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.placeholders-section h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.placeholder-info {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.placeholders-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.placeholders-table th,
.placeholders-table td {
  padding: 0.75rem;
  border: 1px solid #ddd;
  text-align: left;
}

.placeholders-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.placeholder-name {
  font-weight: bold;
  color: var(--primary-color);
  font-family: monospace;
}

.prompt-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  resize: vertical;
}

.file-info {
  padding: 1rem;
  background: #f0f7ff;
  border: 1px solid #b3d9ff;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.file-info p {
  margin: 0.5rem 0;
}

.info-text {
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}

.placeholder-warning {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #fff3cd;
  border: 2px solid #ffc107;
  border-radius: 4px;
  color: #856404;
}

.placeholder-warning h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #856404;
}

.placeholder-warning p {
  margin: 0.5rem 0;
  line-height: 1.5;
}

.placeholder-warning code {
  background: #fff;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: monospace;
  color: #d63384;
  border: 1px solid #ffc107;
}

.placeholder-warning ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.placeholder-warning li {
  margin: 0.25rem 0;
}
</style> 
