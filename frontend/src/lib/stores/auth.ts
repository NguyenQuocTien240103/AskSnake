import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  register: (email: string, username: string, password: string) => Promise<boolean>
  logout: () => void
  clearAuth: () => void
}

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string): Promise<boolean> => {
        set({ isLoading: true })
        try {
          const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          })

          if (response.ok) {
            const data = await response.json()
            const token = data.access_token

            // Get user info
            const userResponse = await fetch(`${API_URL}/me`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            })

            if (userResponse.ok) {
              const userData = await userResponse.json()
              set({
                user: userData,
                token,
                isAuthenticated: true,
                isLoading: false,
              })
              return true
            }
          }
          
          set({ isLoading: false })
          return false
        } catch (error) {
          console.error('Login error:', error)
          set({ isLoading: false })
          return false
        }
      },

      register: async (email: string, username: string, password: string): Promise<boolean> => {
        set({ isLoading: true })
        try {
          const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, username, password }),
          })

          if (response.ok) {
            set({ isLoading: false })
            return true
          }
          
          set({ isLoading: false })
          return false
        } catch (error) {
          console.error('Registration error:', error)
          set({ isLoading: false })
          return false
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      clearAuth: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)