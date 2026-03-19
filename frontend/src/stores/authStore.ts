import { create } from 'zustand'

interface AuthState {
  accessToken: string | null
  isAuthenticated: boolean
  setToken: (token: string | null) => void
  clearAuth: () => void
}

const ACCESS_TOKEN_KEY = 'itinerai_access_token'

const loadInitialToken = (): string | null => {
  try {
    const stored = window.localStorage.getItem(ACCESS_TOKEN_KEY)
    return stored || null
  } catch {
    return null
  }
}

export const useAuthStore = create<AuthState>((set) => {
  const initialToken = loadInitialToken()

  return {
    accessToken: initialToken,
    isAuthenticated: Boolean(initialToken),
    setToken: (token) => {
      try {
        if (token) {
          window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
        } else {
          window.localStorage.removeItem(ACCESS_TOKEN_KEY)
        }
      } catch {
        // ignore storage errors
      }

      set(() => ({
        accessToken: token,
        isAuthenticated: Boolean(token),
      }))
    },
    clearAuth: () => {
      try {
        window.localStorage.removeItem(ACCESS_TOKEN_KEY)
      } catch {
        // ignore storage errors
      }

      set(() => ({
        accessToken: null,
        isAuthenticated: false,
      }))
    },
  }
})

