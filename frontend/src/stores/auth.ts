import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const userId = ref<string | null>(localStorage.getItem('userId'))

  function setAuth(newToken: string, newUserId: string) {
    token.value = newToken
    userId.value = newUserId
    localStorage.setItem('token', newToken)
    localStorage.setItem('userId', newUserId)
  }

  function clearAuth() {
    token.value = null
    userId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
  }

  const isAuthenticated = () => !!token.value

  return {
    token,
    userId,
    setAuth,
    clearAuth,
    isAuthenticated
  }
})
