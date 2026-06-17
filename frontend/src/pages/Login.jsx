import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ThemeToggle from '../components/ThemeToggle'
import { useAuth } from '../context/AuthContext'
import { useNotification } from '../context/NotificationContext'

export default function Login() {
  const navigate = useNavigate()
  const { login, loginWithGoogle, isAuthenticated, isLoading: authLoading, authError } = useAuth()
  const { addToast } = useNotification()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Show OAuth errors from redirect
  useEffect(() => {
    if (authError) {
      setError(`Google login failed: ${authError}`)
    }
  }, [authError])

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, authLoading, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle()
    } catch (err) {
      addToast(`Google login failed: ${err.message}`, 'error')
    }
  }

  return (
    <div className="min-h-screen bg-auth flex items-center justify-center px-6">
      <div className="absolute top-5 right-8"><ThemeToggle /></div>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="text-3xl font-extrabold text-heading tracking-tight inline-flex items-center justify-center">
            Intelli<span className="text-brand-500 font-bold bg-clip-text bg-gradient-to-r from-brand-500 to-brand-400">Analyze</span>
            <span className="text-xs ml-2 px-1.5 py-0.5 rounded bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300 font-semibold align-middle">AI</span>
          </Link>
          <p className="text-body mt-2 text-sm">Sign in to your legal analysis workspace</p>
        </div>
        <div className="auth-card border rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-body mb-2">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
            </div>
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-body"><input type="checkbox" className="accent-brand-600" /> Remember me</label>
              <a href="#" className="text-brand-600 hover:text-brand-700 font-medium">Forgot?</a>
            </div>
            <button type="submit" className="w-full bg-brand-600 hover:bg-brand-700 text-white py-3 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20">Sign In</button>
          </form>
          <div className="my-5 flex items-center gap-3"><div className="flex-1 h-px divider-line"></div><span className="text-xs text-muted">or continue with</span><div className="flex-1 h-px divider-line"></div></div>
          <div className="space-y-3">
            <button onClick={() => navigate('/dashboard')} className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 py-3 rounded-xl font-semibold transition hover:shadow-md">
              <svg className="h-5 w-5" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Continue with Google
            </button>
            <button onClick={() => navigate('/dashboard')} className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 py-3 rounded-xl font-semibold transition hover:shadow-md">
              <svg className="h-5 w-5" viewBox="0 0 23 23"><path fill="#f35325" d="M1 1h10v10H1z"/><path fill="#81bc06" d="M12 1h10v10H12z"/><path fill="#05a6f0" d="M1 12h10v10H1z"/><path fill="#ffba08" d="M12 12h10v10H12z"/></svg>
              Continue with Microsoft
            </button>
          </div>
          <div className="mt-4">
            <Link to="/dashboard" className="block w-full text-center btn-explore border py-3 rounded-xl font-semibold transition">🚀 Explore Dashboard</Link>
          </div>
          <div className="mt-6 text-center text-sm text-body">Don't have an account? <Link to="/signup" className="text-brand-600 hover:text-brand-700 font-medium">Sign up</Link></div>
        </div>
      </div>
    </div>
  )
}
