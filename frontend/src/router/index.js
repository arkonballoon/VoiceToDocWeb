import { createRouter, createWebHistory } from 'vue-router'
import TranscriptionView from '../views/TranscriptionView.vue'
import TemplateManager from '../components/TemplateManager.vue'
import ConfigurationView from '../views/ConfigurationView.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 