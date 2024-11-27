<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Template-Verwaltung</h2>
    </div>

    <div class="page-content">
      <div class="template-list">
        <div v-for="template in templates" 
             :key="template.id" 
             class="template-card"
             :title="template.description || 'Keine Beschreibung'">
          <span class="template-name">{{ template.name }}</span>
          <div class="template-actions">
            <button @click="showPreview(template)" class="preview-button" title="Vorschau">
              <i class="fas fa-eye"></i>
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

    <!-- Create Template Dialog -->
    <div v-if="showCreateDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>Neues Template erstellen</h3>
        <form @submit.prevent="createTemplate">
          <div class="form-group">
            <label>Name:</label>
            <input v-model="newTemplate.name" required>
          </div>
          <div class="form-group">
            <label>Beschreibung:</label>
            <textarea v-model="newTemplate.description"></textarea>
          </div>
          <div class="form-group">
            <label>Inhalt:</label>
            <textarea v-model="newTemplate.content" required></textarea>
          </div>
          <div class="dialog-actions">
            <button type="button" @click="showCreateDialog = false">Abbrechen</button>
            <button type="submit">Erstellen</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Preview Dialog -->
    <div v-if="showPreviewDialog" class="dialog-overlay">
      <div class="dialog preview-dialog">
        <div class="dialog-header">
          <h3>{{ selectedTemplate?.name }}</h3>
          <button @click="showPreviewDialog = false" class="close-button">&times;</button>
        </div>
        <div class="preview-content">
          <pre class="template-content">{{ selectedTemplate?.content }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TemplateManager',
  data() {
    return {
      templates: [],
      showCreateDialog: false,
      showPreviewDialog: false,
      selectedTemplate: null,
      newTemplate: {
        name: '',
        description: '',
        content: ''
      }
    }
  },
  methods: {
    async loadTemplates() {
      try {
        const response = await fetch('http://localhost:8000/templates')
        if (!response.ok) throw new Error('Fehler beim Laden der Templates')
        this.templates = await response.json()
      } catch (error) {
        console.error('Fehler:', error)
      }
    },
    async createTemplate() {
      try {
        const response = await fetch('http://localhost:8000/templates/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: this.newTemplate.name,
            content: this.newTemplate.content,
            description: this.newTemplate.description
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        await this.loadTemplates()
        this.showCreateDialog = false
        this.newTemplate = { name: '', description: '', content: '' }
      } catch (error) {
        console.error('Fehler beim Erstellen des Templates:', error);
        throw error;
      }
    },
    async deleteTemplate(id) {
      if (!confirm('Template wirklich löschen?')) return
      
      try {
        const response = await fetch(`http://localhost:8000/templates/${id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) throw new Error('Fehler beim Löschen des Templates')
        
        await this.loadTemplates()
      } catch (error) {
        console.error('Fehler:', error)
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('de-DE')
    },
    showPreview(template) {
      this.selectedTemplate = template
      this.showPreviewDialog = true
    }
  },
  mounted() {
    this.loadTemplates()
  }
}
</script>

<style scoped>
.page-container {
  padding: 0 2rem;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 1.5rem;
  color: var(--text-color);
  margin: 0;
}

.page-content {
  padding: 0;
}

.create-button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.template-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.template-name {
  font-weight: bold;
  margin-right: 1rem;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-button, .delete-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.preview-button {
  background: var(--secondary-color);
  color: white;
}

.delete-button {
  background: var(--danger-color, #dc3545);
  color: white;
}

.preview-button i, .delete-button i {
  font-size: 1rem;
}

.preview-dialog {
  max-width: 800px;
  width: 90%;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #666;
}

.preview-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.template-content {
  white-space: pre-wrap;
  font-family: monospace;
  line-height: 1.5;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
</style> 