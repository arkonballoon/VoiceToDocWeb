<template>
  <div id="app">
    <header class="header">
      <nav class="nav">
        <div class="nav-links">
          <a href="#">Unternehmen</a>
          <a href="#" class="active">Dienstleistungen</a>
          <a href="#">Karriere</a>
          <a href="#">Kontakt</a>
        </div>
      </nav>
    </header>

    <div class="breadcrumb">
      Startseite \ Dienstleistungen \ Audio Transkription
    </div>

    <main class="main-content">
      <div class="hero-section">
        <h1>AUDIO TRANSKRIPTIONS-SERVICE</h1>
        <p class="subtitle">
          Digitalisieren Sie Ihre Audio-Inhalte mit unserer KI-gestützten Transkriptionslösung
        </p>
      </div>

      <TranscriptionService />
    </main>
  </div>
</template>

<script>
import TranscriptionService from './components/TranscriptionService.vue'

export default {
  name: 'App',
  components: {
    TranscriptionService
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

#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-color);
}

.header {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0.5rem 2rem;
}

.nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 40px;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
}

.nav-links a.active {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.breadcrumb {
  max-width: 1200px;
  margin: 1rem auto;
  padding: 0 2rem;
  color: #666;
  font-size: 0.9rem;
}

.hero-section {
  background: var(--background-gradient);
  color: white;
  padding: 4rem 2rem;
  text-align: center;
  margin-bottom: 2rem;
}

.hero-section h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  position: relative;
  display: inline-block;
}

.hero-section h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 100%;
  height: 4px;
  background: var(--primary-color);
}

.subtitle {
  font-size: 1.2rem;
  max-width: 800px;
  margin: 0 auto;
  opacity: 0.9;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
</style>
