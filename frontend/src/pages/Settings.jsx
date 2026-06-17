import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'
import { useAuth } from '../context/AuthContext'
import { useNotification } from '../context/NotificationContext'

export default function Settings() {
  const navigate = useNavigate()
  const { user, updateProfile, logout } = useAuth()
  const { addToast } = useNotification()

  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')
  const [avatar, setAvatar] = useState(user?.avatar || '')
  const [company, setCompany] = useState(user?.company || 'IntelliAnalyze AI Inc.')
  const [role, setRole] = useState(user?.role || 'Admin')
  const [timezone, setTimezone] = useState(user?.timezone || 'Asia/Kolkata')
  const [language, setLanguage] = useState(user?.language || 'English')
  
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    riskAlerts: true,
    weeklyDigest: false,
    contractExpiry: true,
    teamUpdates: false,
  })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    try {
      updateProfile({
        name,
        email,
        avatar,
        company,
        role,
        timezone,
        language
      })
      setSaved(true)
      addToast('Settings saved successfully!', 'success')
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      addToast(`Error saving settings: ${err.message}`, 'error')
    }
  }

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span> AI</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/settings" className="text-sm text-nav-active font-semibold">Profile</Link>
          <ThemeToggle />
          <div className="flex items-center gap-2">
            <Link to="/settings" className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white text-xs font-bold uppercase cursor-pointer hover:scale-105 transition" title={user?.name || 'User'}>
              {user?.name?.[0] || 'U'}
            </Link>
            <button
              onClick={async () => {
                await logout()
                navigate('/login')
              }}
              className="text-xs bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-600 dark:text-red-400 px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-heading mb-2">Settings</h1>
        <p className="text-body mb-8">Manage your account preferences and notifications.</p>

        {saved && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium flex items-center gap-2">
            ✅ Settings saved successfully!
          </div>
        )}

        {/* Profile Section */}
        <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme mb-6">
          <h2 className="font-semibold text-heading mb-4 flex items-center gap-2">👤 Profile Information</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-body mb-2">Full Name</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Company</label>
              <input type="text" value={company} onChange={e => setCompany(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Role</label>
              <select value={role} onChange={e => setRole(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
                <option>Admin</option>
                <option>Manager</option>
                <option>Analyst</option>
                <option>Viewer</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Timezone</label>
              <select value={timezone} onChange={e => setTimezone(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
                <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                <option value="America/New_York">America/New_York (EST)</option>
                <option value="Europe/London">Europe/London (GMT)</option>
                <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Language</label>
              <select value={language} onChange={e => setLanguage(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
                <option>English</option>
                <option>Hindi</option>
                <option>Kannada</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme mb-6">
          <h2 className="font-semibold text-heading mb-4 flex items-center gap-2">🔔 Notification Preferences</h2>
          <div className="space-y-4">
            {Object.entries(notifications).map(([key, val]) => (
              <label key={key} className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm text-body group-hover:text-heading transition">
                  {key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}
                </span>
                <div className={`relative h-6 w-11 rounded-full transition-colors duration-200 ${val ? 'bg-brand-600' : 'bg-gray-300'}`} onClick={() => setNotifications({...notifications, [key]: !val})}>
                  <div className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${val ? 'translate-x-5' : 'translate-x-0.5'}`} />
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-card border border-red-200 rounded-2xl p-6 shadow-theme mb-6">
          <h2 className="font-semibold text-red-600 mb-2 flex items-center gap-2">⚠️ Danger Zone</h2>
          <p className="text-sm text-body mb-4">Permanently delete your account and all associated data.</p>
          <button className="px-5 py-2 text-sm font-semibold text-red-600 border border-red-300 rounded-xl hover:bg-red-50 transition">Delete Account</button>
        </div>

        <button onClick={handleSave} className="w-full bg-brand-600 hover:bg-brand-700 text-white py-3 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20">
          Save Settings
        </button>
      </div>
    </div>
  )
}
