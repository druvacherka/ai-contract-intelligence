import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react'
import supabase from '../services/supabase'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('IntelliAnalyze AI_user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const [session, setSession] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [authError, setAuthError] = useState(null)
  const initialized = useRef(false)

  const extractUser = (supabaseUser) => {
    if (!supabaseUser) return null
    const meta = supabaseUser.user_metadata || {}
    return {
      id: supabaseUser.id,
      email: supabaseUser.email,
      name: meta.full_name || meta.name || supabaseUser.email?.split('@')[0] || 'User',
      avatar: meta.avatar_url || meta.picture || null,
      role: 'admin',
      joinedAt: supabaseUser.created_at || new Date().toISOString(),
    }
  }

  useEffect(() => {
    if (initialized.current) return
    initialized.current = true

    // Check if URL has an OAuth error
    const urlParams = new URLSearchParams(window.location.search)
    const hashParams = new URLSearchParams(window.location.hash.replace('#', ''))
    const oauthError = urlParams.get('error_description') || hashParams.get('error_description')
    
    if (oauthError) {
      console.error('[Auth] OAuth error:', oauthError)
      setAuthError(decodeURIComponent(oauthError))
      setIsLoading(false)
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname)
      return
    }

    // Check if URL has valid OAuth callback tokens (NOT error params)
    const hasOAuthCallback = window.location.hash.includes('access_token')

    let authResolved = false

    // 1. Set up the auth state change listener FIRST
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, newSession) => {
      console.log('[Auth] state change:', event, !!newSession)

      setSession(newSession)
      if (newSession?.user) {
        const extracted = extractUser(newSession.user)
        setUser(extracted)
        localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(extracted))
        setAuthError(null)
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
        localStorage.removeItem('IntelliAnalyze AI_user')
      }
      authResolved = true
      setIsLoading(false)
    })

    // 2. Then check for an existing session
    supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
      console.log('[Auth] initial session:', !!currentSession)
      if (currentSession?.user) {
        setSession(currentSession)
        const extracted = extractUser(currentSession.user)
        setUser(extracted)
        localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(extracted))
        authResolved = true
        setIsLoading(false)
      } else if (!hasOAuthCallback) {
        // No OAuth callback pending, safe to stop loading
        authResolved = true
        setIsLoading(false)
      }
    }).catch((err) => {
      console.error('[Auth] getSession error:', err)
      setIsLoading(false)
    })

    // Safety timeout: 3 seconds max wait
    const timeout = setTimeout(() => {
      if (!authResolved) {
        console.warn('[Auth] timeout — forcing isLoading=false')
        setIsLoading(false)
      }
    }, 3000)

    return () => {
      subscription.unsubscribe()
      clearTimeout(timeout)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    setIsLoading(true)
    setAuthError(null)
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      setIsLoading(false)
      throw error
    }
    const extracted = extractUser(data.user)
    setUser(extracted)
    setSession(data.session)
    localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(extracted))
    setIsLoading(false)
    return extracted
  }, [])

  const signup = useCallback(async (name, email, password) => {
    setIsLoading(true)
    setAuthError(null)
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: name } },
    })
    if (error) {
      setIsLoading(false)
      throw error
    }
    const extracted = extractUser(data.user)
    setUser(extracted)
    setSession(data.session)
    localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(extracted))
    setIsLoading(false)
    return extracted
  }, [])

  const logout = useCallback(async () => {
    await supabase.auth.signOut()
    setUser(null)
    setSession(null)
    localStorage.removeItem('IntelliAnalyze AI_user')
  }, [])

  const updateProfile = useCallback((updates) => {
    setUser(prev => {
      if (!prev) return null
      const updated = { ...prev, ...updates }
      localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(updated))
      return updated
    })
  }, [])

  const loginWithGoogle = useCallback(async () => {
    setAuthError(null)
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/dashboard',
      },
    })
    if (error) throw error
  }, [])

  const loginAsDemo = useCallback(() => {
    setIsLoading(true)
    const demoUser = {
      id: 'demo-user-id',
      email: 'demo@intellianalyze.ai',
      name: 'Demo Analyst',
      avatar: null,
      role: 'admin',
      joinedAt: new Date().toISOString(),
    }
    setUser(demoUser)
    localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(demoUser))
    setIsLoading(false)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      authError,
      login,
      signup,
      logout,
      updateProfile,
      loginWithGoogle,
      loginAsDemo,
      session,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
