import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('contractiq_user')
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (user) {
      localStorage.setItem('contractiq_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('contractiq_user')
    }
  }, [user])

  const login = useCallback(async (email, password) => {
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800))
    const mockUser = {
      id: 'usr_' + Date.now(),
      name: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      email,
      role: 'admin',
      avatar: email[0].toUpperCase(),
      joinedAt: new Date().toISOString(),
    }
    setUser(mockUser)
    setIsLoading(false)
    return mockUser
  }, [])

  const signup = useCallback(async (name, email, password) => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    const mockUser = {
      id: 'usr_' + Date.now(),
      name,
      email,
      role: 'member',
      avatar: name[0].toUpperCase(),
      joinedAt: new Date().toISOString(),
    }
    setUser(mockUser)
    setIsLoading(false)
    return mockUser
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    localStorage.removeItem('contractiq_user')
  }, [])

  const updateProfile = useCallback((updates) => {
    setUser(prev => prev ? { ...prev, ...updates } : null)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      signup,
      logout,
      updateProfile,
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
