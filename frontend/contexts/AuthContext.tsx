import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/router'
import api from '@/lib/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  username: string
  nickname: string
  first_name: string
  last_name: string
  full_name: string
  avatar?: string
  bio?: string
  is_verified: boolean
  created_at: string
  votes_count: number
  comments_count: number
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  updateUser: (data: Partial<User>) => void
}

interface RegisterData {
  email: string
  username: string
  nickname: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Konfiguracja api
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }, [])

  // Sprawdź czy użytkownik jest zalogowany
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          const response = await api.get('/auth/profile/')
          setUser(response.data)
        }
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        delete api.defaults.headers.common['Authorization']
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login/', { email, password })
      const { user: userData, tokens } = response.data
      
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`
      
      setUser(userData)
      toast.success('Zalogowano pomyślnie')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Błąd podczas logowania'
      toast.error(message)
      throw error
    }
  }

  const register = async (data: RegisterData) => {
    try {
      const response = await api.post('/auth/register/', data)
      const { user: userData, tokens } = response.data
      
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`
      
      setUser(userData)
      toast.success('Konto zostało utworzone pomyślnie')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Błąd podczas rejestracji'
      toast.error(message)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    toast.success('Wylogowano pomyślnie')
    router.push('/')
  }

  const updateUser = (data: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...data })
    }
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

