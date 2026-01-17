import React, { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'
import { api } from '../services/api'

interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'teacher' | 'student'
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (demoRole?: 'admin' | 'teacher' | 'student') => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Demo mode users for testing without OAuth
const DEMO_USERS = {
  admin: { id: 1, email: 'admin@demo.local', name: 'Admin Demo', role: 'admin' as const },
  teacher: { id: 2, email: 'teacher@demo.local', name: 'Teacher Demo', role: 'teacher' as const },
  student: { id: 3, email: 'student@demo.local', name: 'Student Demo', role: 'student' as const }
}

// Check if we're in demo mode (OAuth not configured)
const DEMO_MODE = true // Set to false once OAuth is configured

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log('🔐 AuthProvider initializing...')
    checkUser()
    
    if (!DEMO_MODE) {
      try {
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
          if (session) {
            verifyUser(session.access_token)
          } else {
            setUser(null)
            setLoading(false)
          }
        })

        return () => subscription.unsubscribe()
      } catch (error) {
        console.error('❌ Supabase auth error:', error)
        setLoading(false)
      }
    }
  }, [])

  const checkUser = async () => {
    try {
      console.log('👤 Checking user...')
      // Check localStorage for demo user
      const savedUser = localStorage.getItem('demo_user')
      if (savedUser && DEMO_MODE) {
        const parsedUser = JSON.parse(savedUser)
        console.log('✅ Found saved user:', parsedUser.role)
        setUser(parsedUser)
        setLoading(false)
        return
      }

      if (!DEMO_MODE) {
        const { data: { session } } = await supabase.auth.getSession()
        if (session) {
          await verifyUser(session.access_token)
        } else {
          setLoading(false)
        }
      } else {
        console.log('✅ Demo mode active, no saved user')
        setLoading(false)
      }
    } catch (error) {
      console.error('❌ Error checking user:', error)
      setLoading(false)
    }
  }

  const verifyUser = async (token: string) => {
    try {
      const response = await api.post('/auth/login', { token })
      if (response.data.success) {
        setUser(response.data.user)
      }
    } catch (error) {
      console.error('❌ Error verifying user:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (demoRole?: 'admin' | 'teacher' | 'student') => {
    if (DEMO_MODE && demoRole) {
      // Demo mode login
      const demoUser = DEMO_USERS[demoRole]
      setUser(demoUser)
      localStorage.setItem('demo_user', JSON.stringify(demoUser))
      console.log(`✅ Demo login as ${demoRole}`)
    } else {
      // Real OAuth login
      try {
        await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: `${window.location.origin}/auth/callback`
          }
        })
      } catch (error) {
        console.error('❌ OAuth error:', error)
        // Fallback to demo mode if OAuth fails
        if (demoRole) {
          const demoUser = DEMO_USERS[demoRole]
          setUser(demoUser)
          localStorage.setItem('demo_user', JSON.stringify(demoUser))
          console.log(`⚠️ OAuth failed, using demo login as ${demoRole}`)
        }
      }
    }
  }

  const logout = async () => {
    if (DEMO_MODE) {
      localStorage.removeItem('demo_user')
      setUser(null)
      console.log('👋 Logged out')
    } else {
      await supabase.auth.signOut()
      setUser(null)
    }
  }

  console.log('🔐 AuthProvider state:', { user: user?.role, loading })

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
