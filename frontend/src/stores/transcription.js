import { defineStore } from 'pinia'

export const useTranscriptionStore = defineStore('transcription', {
  state: () => ({
    transcription: '',
    confidence: null
  }),
  actions: {
    setTranscription(text, conf = null) {
      this.transcription = text
      this.confidence = conf
    }
  }
}) 
