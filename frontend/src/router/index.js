import { createRouter, createWebHistory } from 'vue-router'
import TranscriptionView from '../views/TranscriptionView.vue'
import TemplateManager from '../components/TemplateManager.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 