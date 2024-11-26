<template>
  <div class="transcription-view">
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
import TranscriptionService from '../components/TranscriptionService.vue'

export default {
  name: 'TranscriptionView',
  components: {
    TranscriptionService
  }
}
</script>

<style scoped>
.transcription-view {
  width: 100%;
}

.breadcrumb {
  margin-bottom: 2rem;
  color: #666;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}

.hero-section h1 {
  font-size: 2.5rem;
  color: var(--secondary-color);
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
}
</style> 