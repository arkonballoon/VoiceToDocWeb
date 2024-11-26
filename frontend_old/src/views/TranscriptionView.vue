<template>
  <div>
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