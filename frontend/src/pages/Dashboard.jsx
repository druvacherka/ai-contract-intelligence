import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

export default function Dashboard() {
  const stats = [
    { label:'Total Contracts', value:'24', change:'+3 this week', icon:'📄' },
    { label:'Analyzed', value:'18', change:'75% complete', icon:'✅' },
    { label:'High Risk', value:'5', change:'2 critical', icon:'⚠️' },
    { label:'Avg Risk Score', value:'6.2', change:'/10', icon:'📊' },
  ]
  const recent = [
    { name:'NDA_Acme_Corp_2026.pdf', risk:'Low', score:3.2, date:'May 11' },
    { name:'Service_Agreement_v4.docx', risk:'High', score:8.1, date:'May 10' },
    { name:'Lease_Contract_Q2.pdf', risk:'—', score:null, date:'May 10' },
    { name:'Employment_Offer_JD.pdf', risk:'Medium', score:5.7, date:'May 9' },
    { name:'Vendor_SLA_2026.docx', risk:'High', score:7.8, date:'May 8' },
  ]
  const rc = r => r==='High'?'risk-high':r==='Medium'?'risk-med':r==='Low'?'risk-low':'risk-none'
  const clauses = [
    { type:'Confidentiality', count:22, pct:92 },
    { type:'Termination', count:18, pct:75 },
    { type:'Indemnification', count:14, pct:58 },
    { type:'Non-Compete', count:11, pct:46 },
    { type:'Liability Cap', count:9, pct:38 },
  ]

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav-active font-semibold">Dashboard</Link>
          <ThemeToggle />
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white text-xs font-bold">S</div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div><h1 className="text-2xl font-bold text-heading">Dashboard</h1><p className="text-sm text-body mt-1">Contract analysis overview</p></div>
          <Link to="/upload" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition shadow-sm">+ Upload New</Link>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((s,i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-5 shadow-theme">
              <div className="flex items-center justify-between mb-3"><span className="text-2xl">{s.icon}</span><span className="text-xs text-muted">{s.change}</span></div>
              <div className="text-2xl font-bold text-heading">{s.value}</div>
              <div className="text-xs text-muted mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-4">Recent Contracts</h2>
            <div className="space-y-2">
              {recent.map((r,i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-card-hover transition">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="h-9 w-9 rounded-lg bg-subtle border border-theme flex items-center justify-center text-sm">📄</div>
                    <div className="min-w-0"><p className="text-sm font-medium text-heading truncate">{r.name}</p><p className="text-xs text-muted">{r.date}</p></div>
                  </div>
                  <div className="flex items-center gap-3">
                    {r.score!==null && <span className="text-sm font-semibold text-heading">{r.score}</span>}
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${rc(r.risk)}`}>{r.risk}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-4">Clause Detection</h2>
            <div className="space-y-4">
              {clauses.map((c,i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1"><span className="text-body">{c.type}</span><span className="text-muted">{c.count}</span></div>
                  <div className="h-2 progress-track rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full" style={{width:`${c.pct}%`}}></div></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mt-6">
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-4">Risk Distribution</h2>
            <div className="flex items-end gap-4 h-40">
              {[{l:'Low',h:45,c:'bg-emerald-400'},{l:'Medium',h:30,c:'bg-amber-400'},{l:'High',h:20,c:'bg-red-400'},{l:'Critical',h:5,c:'bg-red-600'}].map((b,i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <span className="text-xs font-semibold text-heading">{b.h}%</span>
                  <div className={`w-full rounded-lg ${b.c}`} style={{height:`${b.h*2}px`}}></div>
                  <span className="text-xs text-muted">{b.l}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-3">
              {[{icon:'📄',label:'Upload Contract',to:'/upload'},{icon:'🔍',label:'Search Contracts',to:'#'},{icon:'📊',label:'Risk Report',to:'#'},{icon:'⚙️',label:'Settings',to:'#'},{icon:'👥',label:'Team Access',to:'#'},{icon:'📥',label:'Export Data',to:'#'}].map((a,i) => (
                <Link key={i} to={a.to} className="flex items-center gap-3 p-3 rounded-xl bg-subtle border border-theme bg-card-hover transition">
                  <span className="text-lg">{a.icon}</span>
                  <span className="text-sm text-body font-medium">{a.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
