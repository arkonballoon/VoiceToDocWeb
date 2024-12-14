import { createRouter, createWebHistory } from 'vue-router'
import TranscriptionView from '../views/TranscriptionView.vue'
import TemplateManager from '../components/TemplateManager.vue'
import ConfigurationView from '../views/ConfigurationView.vue'
import TemplateProcessingView from '../views/TemplateProcessingView.vue'

const routes = [
  {
    path: '/',
    name: 'Transkription',
    component: TranscriptionView
  },
  {
    path: '/templates',
    name: 'Templates',
    component: TemplateManager
  },
  {
    path: '/config',
    name: 'Konfiguration',
    component: ConfigurationView
  },
  {
    path: '/process',
    name: 'process',
    component: TemplateProcessingView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 