import { create } from 'zustand'

interface ProfileState {
  nickname: string
  setNickname: (name: string) => void
}

const STORAGE_KEY = 'itinerai:nickname'

const getInitialNickname = (): string => {
  if (typeof window === 'undefined') return ''
  const stored = window.localStorage.getItem(STORAGE_KEY)
  return stored ?? ''
}

export const useProfileStore = create<ProfileState>((set) => ({
  nickname: getInitialNickname(),
  setNickname: (name) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, name)
    }
    set({ nickname: name })
  },
}))

