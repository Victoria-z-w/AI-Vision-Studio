import { defineStore } from "pinia";
import { ref } from "vue";

export const useSessionStore = defineStore("session", () => {
  const sessionId = ref("");

  function ensureSession() {
    // Session is managed via cookie automatically by the backend
    // This store can track it if received from a response header
  }

  return { sessionId, ensureSession };
});
