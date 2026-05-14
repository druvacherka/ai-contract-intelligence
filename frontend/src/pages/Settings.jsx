import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

export default function Settings() {
  const [profile, setProfile] = useState({
    name: 'Saniya',
    email: 'saniya@contractiq.dev',
    company: 'ContractIQ Inc.',
    role: 'Admin',
    timezone: 'Asia/Kolkata',
    language: 'English',
  })
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    riskAlerts: true,
    weeklyDigest: false,
    contractExpiry: true,
    teamUpdates: false,
  })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/settings" className="text-sm text-nav-active font-semibold">Settings</Link>
          <ThemeToggle />
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
              <input type="text" value={profile.name} onChange={e => setProfile({...profile, name: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Email</label>
              <input type="email" value={profile.email} onChange={e => setProfile({...profile, email: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Company</label>
              <input type="text" value={profile.company} onChange={e => setProfile({...profile, company: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Role</label>
              <select value={profile.role} onChange={e => setProfile({...profile, role: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
                <option>Admin</option>
                <option>Manager</option>
                <option>Analyst</option>
                <option>Viewer</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Timezone</label>
              <select value={profile.timezone} onChange={e => setProfile({...profile, timezone: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
                <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                <option value="America/New_York">America/New_York (EST)</option>
                <option value="Europe/London">Europe/London (GMT)</option>
                <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-body mb-2">Language</label>
              <select value={profile.language} onChange={e => setProfile({...profile, language: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition">
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
