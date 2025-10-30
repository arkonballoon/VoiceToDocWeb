import { createRouter, createWebHistory } from 'vue-router'
// Eager loading für Haupt-View (wird auf Mobile am meisten genutzt)
import TranscriptionView from '../views/TranscriptionView.vue'

// Lazy loading für Desktop-Features
const TemplateManager = () => import('../components/TemplateManager.vue')
const ConfigurationView = () => import('../views/ConfigurationView.vue')
const TemplateProcessingView = () => import('../views/TemplateProcessingView.vue')

const routes = [
  {
    path: '/',
    name: 'Transkription',
    component: TranscriptionView
  },
  {
    path: '/templates',
    name: 'Templates',
    component: TemplateManager,
    meta: { title: 'Templates verwalten' }
  },
  {
    path: '/config',
    name: 'Konfiguration',
    component: ConfigurationView,
    meta: { title: 'Konfiguration' }
  },
  {
    path: '/process',
    name: 'process',
    component: TemplateProcessingView,
    meta: { title: 'Template Verarbeitung' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
