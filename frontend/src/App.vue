<template>
  <div id="app">
    <!-- Network Status Banner -->
    <NetworkStatus />
    
    <!-- PWA Install Prompt -->
    <InstallPrompt />
    
    <header class="header">
      <nav class="nav">
        <div class="nav-links">
          <router-link to="/" :class="{ active: $route.path === '/' }">Transkription</router-link>
          <router-link to="/templates" :class="{ active: $route.path === '/templates' }">Templates</router-link>
          <router-link to="/process" :class="{ active: $route.path === '/process' }">Template Verarbeitung</router-link>
          <router-link to="/help" :class="{ active: $route.path === '/help' }">Hilfe</router-link>
        </div>
        <div class="settings-icon">
          <router-link to="/config" :class="{ active: $route.path === '/config' }">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </router-link>
        </div>
      </nav>
    </header>

    <div class="main-container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import NetworkStatus from './components/NetworkStatus.vue'
import InstallPrompt from './components/InstallPrompt.vue'

export default {
  name: 'App',
  components: {
    NetworkStatus,
    InstallPrompt
  }
}
</script>

<style>
:root {
  --primary-color: #FFB800;
  --secondary-color: #003366;
  --text-color: #2c3e50;
  --background-gradient: linear-gradient(135deg, #001428 0%, #004080 100%);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #f5f6fa;
}

.header {
  background: var(--background-gradient);
  padding: 1rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 4rem;
}

.nav-links {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-links a.active,
.nav-links a:hover {
  background: rgba(255, 255, 255, 0.1);
}

.main-container {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.settings-icon {
  position: absolute;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
}

.settings-icon a {
  color: white;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.settings-icon a:hover,
.settings-icon a.active {
  opacity: 1;
}

/* Mobile Navigation */
@media (max-width: 768px) {
  .header {
    padding: 0.75rem 1rem;
    height: auto;
  }

  .nav-links {
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: flex-start;
  }

  .nav-links a {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }

  .settings-icon {
    right: 1rem;
  }

  .settings-icon svg {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0.5rem 0.75rem;
  }

  .nav-links {
    gap: 0.25rem;
  }

  .nav-links a {
    padding: 0.4rem 0.6rem;
    font-size: 0.85rem;
  }
}
</style>
