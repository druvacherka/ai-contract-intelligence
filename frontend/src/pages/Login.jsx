import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import ThemeToggle from '../components/ThemeToggle'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => { e.preventDefault(); navigate('/dashboard') }

  return (
    <div className="min-h-screen bg-auth flex items-center justify-center px-6">
      <div className="absolute top-5 right-8"><ThemeToggle /></div>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="text-2xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
          <p className="text-body mt-2">Sign in to your account</p>
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
          <div className="my-5 flex items-center gap-3"><div className="flex-1 h-px divider-line"></div><span className="text-xs text-muted">or</span><div className="flex-1 h-px divider-line"></div></div>
          <Link to="/dashboard" className="block w-full text-center btn-explore border py-3 rounded-xl font-semibold transition">🚀 Explore Dashboard</Link>
          <div className="mt-6 text-center text-sm text-body">Don't have an account? <Link to="/signup" className="text-brand-600 hover:text-brand-700 font-medium">Sign up</Link></div>
        </div>
      </div>
    </div>
  )
}
