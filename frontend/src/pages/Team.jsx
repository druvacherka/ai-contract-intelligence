import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

const teamMembers = [
  { id: 1, name: 'Saniya', email: 'saniya@contractiq.dev', role: 'Admin', avatar: 'S', color: 'from-accent-rose to-pink-400', contracts: 34, lastActive: '2 min ago', status: 'online' },
  { id: 2, name: 'Prajwal', email: 'prajwal@contractiq.dev', role: 'Data Engineer', avatar: 'P', color: 'from-brand-500 to-brand-400', contracts: 28, lastActive: '1 hr ago', status: 'online' },
  { id: 3, name: 'Dhruva', email: 'dhruva@contractiq.dev', role: 'ML Engineer', avatar: 'D', color: 'from-accent-cyan to-blue-400', contracts: 19, lastActive: '3 hrs ago', status: 'away' },
  { id: 4, name: 'Vishwas', email: 'vishwas@contractiq.dev', role: 'Backend Dev', avatar: 'V', color: 'from-accent-amber to-orange-400', contracts: 22, lastActive: '30 min ago', status: 'online' },
]

const pendingInvites = [
  { email: 'reviewer@lawfirm.com', role: 'Viewer', sentAt: 'May 12' },
  { email: 'analyst@company.com', role: 'Analyst', sentAt: 'May 11' },
]

export default function Team() {
  const [showInvite, setShowInvite] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('Viewer')

  const handleInvite = (e) => {
    e.preventDefault()
    setShowInvite(false)
    setInviteEmail('')
  }

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/team" className="text-sm text-nav-active font-semibold">Team</Link>
          <Link to="/settings" className="text-sm text-nav hover:text-nav-active transition">Settings</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-heading">Team Management</h1>
            <p className="text-sm text-body mt-1">{teamMembers.length} members • {pendingInvites.length} pending invites</p>
          </div>
          <button onClick={() => setShowInvite(!showInvite)} className="bg-brand-600 hover:bg-brand-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition shadow-sm">
            + Invite Member
          </button>
        </div>

        {/* Invite Form */}
        {showInvite && (
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme mb-6 animate-fade-in">
            <h3 className="font-semibold text-heading mb-4">Invite New Member</h3>
            <form onSubmit={handleInvite} className="flex gap-3">
              <input type="email" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="colleague@company.com" className="flex-1 px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
              <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} className="px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 transition">
                <option>Viewer</option>
                <option>Analyst</option>
                <option>Manager</option>
                <option>Admin</option>
              </select>
              <button type="submit" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 rounded-xl font-semibold transition">Send Invite</button>
            </form>
          </div>
        )}

        {/* Team Grid */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {teamMembers.map(m => (
            <div key={m.id} className="bg-card border border-theme rounded-2xl p-5 shadow-theme hover:shadow-lg transition">
              <div className="flex items-start gap-4">
                <div className="relative">
                  <div className={`h-12 w-12 rounded-xl bg-gradient-to-br ${m.color} flex items-center justify-center text-white font-bold text-lg`}>{m.avatar}</div>
                  <span className={`absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-white ${m.status === 'online' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-heading">{m.name}</h3>
                    <span className="text-xs text-muted">{m.lastActive}</span>
                  </div>
                  <p className="text-xs text-muted truncate">{m.email}</p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-0.5 rounded-md border border-brand-200">{m.role}</span>
                    <span className="text-xs text-muted">{m.contracts} contracts</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Pending Invites */}
        <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
          <h2 className="font-semibold text-heading mb-4">Pending Invites</h2>
          {pendingInvites.length === 0 ? (
            <p className="text-sm text-muted">No pending invitations.</p>
          ) : (
            <div className="space-y-3">
              {pendingInvites.map((inv, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-subtle border border-theme">
                  <div>
                    <p className="text-sm font-medium text-heading">{inv.email}</p>
                    <p className="text-xs text-muted">Invited {inv.sentAt} • {inv.role}</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="text-xs font-medium text-brand-600 hover:text-brand-700 px-3 py-1.5 rounded-lg hover:bg-brand-50 transition">Resend</button>
                    <button className="text-xs font-medium text-red-500 hover:text-red-600 px-3 py-1.5 rounded-lg hover:bg-red-50 transition">Revoke</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
