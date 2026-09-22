import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { clearAccessToken, getAccessToken, getCurrentUser, register, setAccessToken, signIn } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getAccessToken()))
  useEffect(() => {
    if (!getAccessToken()) return
    getCurrentUser().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false))
  }, [])
  useEffect(() => {
    const cleared = () => setUser(null)
    window.addEventListener('structicode-auth-cleared', cleared)
    return () => window.removeEventListener('structicode-auth-cleared', cleared)
  }, [])
  const value = useMemo(() => ({ user, loading, authenticated: Boolean(user),
    async signIn(credentials) { const response = await signIn(credentials); setAccessToken(response.access_token); setUser(response.user); return response.user },
    async register(details) { const response = await register(details); setAccessToken(response.access_token); setUser(response.user); return response.user },
    signOut() { clearAccessToken(); setUser(null) },
  }), [user, loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error('AuthProvider is required'); return context }
