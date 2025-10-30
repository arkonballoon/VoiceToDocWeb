<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Audio Transkriptions-Service</h2>
    </div>

    <div class="page-content">
      <TranscriptionService />
    </div>
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
</style> 
