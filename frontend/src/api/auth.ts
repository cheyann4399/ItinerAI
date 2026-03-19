import { apiClient } from './client'
import { useAuthStore } from '../stores/authStore'

export interface LoginPayload {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterPayload {
  email: string
  name: string
  password: string
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', payload)
  useAuthStore.getState().setToken(data.access_token)
  return data
}

export async function register(payload: RegisterPayload): Promise<void> {
  await apiClient.post('/auth/register', payload)
}

