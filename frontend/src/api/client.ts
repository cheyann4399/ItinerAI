import axios from 'axios'

import { useAuthStore } from '../stores/authStore'

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.toString().replace(/\/+$/, '') ||
  'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL,
  timeout: 15000,
})

apiClient.interceptors.request.use(
  (config) => {
    const state = useAuthStore.getState()
    const token = state.accessToken
    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response } = error
    if (!response) {
      return Promise.reject(error)
    }

    if (response.status === 401) {
      const auth = useAuthStore.getState()
      auth.clearAuth()
      return Promise.reject(error)
    }

    return Promise.reject(error)
  },
)

