import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('30d')

  const monthlyData = [
    { month: 'Jan', contracts: 12, analyzed: 10, highRisk: 2 },
    { month: 'Feb', contracts: 18, analyzed: 15, highRisk: 4 },
    { month: 'Mar', contracts: 8, analyzed: 8, highRisk: 1 },
    { month: 'Apr', contracts: 24, analyzed: 20, highRisk: 5 },
    { month: 'May', contracts: 31, analyzed: 24, highRisk: 7 },
  ]
  const maxContracts = Math.max(...monthlyData.map(d => d.contracts))

  const riskBreakdown = [
    { level: 'Low Risk', count: 45, pct: 45, color: 'bg-emerald-400', textColor: 'text-emerald-600' },
    { level: 'Medium Risk', count: 30, pct: 30, color: 'bg-amber-400', textColor: 'text-amber-600' },
    { level: 'High Risk', count: 20, pct: 20, color: 'bg-red-400', textColor: 'text-red-600' },
    { level: 'Critical', count: 5, pct: 5, color: 'bg-red-600', textColor: 'text-red-700' },
  ]

  const clauseTypes = [
    { type: 'Confidentiality', total: 89, avgRisk: 2.1 },
    { type: 'Indemnification', total: 67, avgRisk: 6.8 },
    { type: 'Termination', total: 74, avgRisk: 4.2 },
    { type: 'Non-Compete', total: 42, avgRisk: 5.9 },
    { type: 'IP Assignment', total: 31, avgRisk: 7.4 },
    { type: 'Liability Cap', total: 56, avgRisk: 5.1 },
    { type: 'Force Majeure', total: 28, avgRisk: 3.3 },
    { type: 'Data Privacy', total: 39, avgRisk: 6.2 },
  ]

  const topMetrics = [
    { label: 'Total Contracts', value: '93', change: '+12%', icon: '📄', up: true },
    { label: 'Avg Risk Score', value: '4.8', change: '-0.3', icon: '📊', up: false },
    { label: 'Clauses Extracted', value: '1,247', change: '+18%', icon: '📑', up: true },
    { label: 'Processing Time', value: '2.3s', change: '-15%', icon: '⚡', up: false },
  ]

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/analytics" className="text-sm text-nav-active font-semibold">Analytics</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-heading">Analytics</h1>
            <p className="text-sm text-body mt-1">Contract intelligence insights and trends</p>
          </div>
          <div className="flex gap-1 bg-subtle rounded-xl p-1 border border-theme">
            {['7d', '30d', '90d', '1y'].map(r => (
              <button key={r} onClick={() => setTimeRange(r)} className={`px-4 py-2 rounded-lg text-xs font-medium transition ${timeRange === r ? 'bg-card shadow-sm text-heading' : 'text-body hover:text-heading'}`}>
                {r === '7d' ? '7 Days' : r === '30d' ? '30 Days' : r === '90d' ? '90 Days' : '1 Year'}
              </button>
            ))}
          </div>
        </div>

        {/* Top Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {topMetrics.map((m, i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-5 shadow-theme">
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl">{m.icon}</span>
                <span className={`text-xs font-medium px-2 py-1 rounded-lg ${m.up ? 'text-emerald-600 bg-emerald-50' : 'text-brand-600 bg-brand-50'}`}>{m.change}</span>
              </div>
              <div className="text-2xl font-bold text-heading">{m.value}</div>
              <div className="text-xs text-muted mt-1">{m.label}</div>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Bar Chart */}
          <div className="lg:col-span-2 bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-6">Contract Volume Trend</h2>
            <div className="flex items-end gap-6 h-48">
              {monthlyData.map((d, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <span className="text-xs font-semibold text-heading">{d.contracts}</span>
                  <div className="w-full flex flex-col gap-1">
                    <div className="w-full rounded-t-lg bg-gradient-to-t from-brand-600 to-brand-400 transition-all duration-500" style={{ height: `${(d.contracts / maxContracts) * 140}px` }} />
                    <div className="w-full rounded-b-lg bg-red-400/60" style={{ height: `${(d.highRisk / maxContracts) * 140}px` }} />
                  </div>
                  <span className="text-xs text-muted">{d.month}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-6 mt-4 pt-4 border-t border-theme">
              <div className="flex items-center gap-2"><div className="h-3 w-3 rounded bg-brand-500" /><span className="text-xs text-muted">Total</span></div>
              <div className="flex items-center gap-2"><div className="h-3 w-3 rounded bg-red-400" /><span className="text-xs text-muted">High Risk</span></div>
            </div>
          </div>

          {/* Risk Donut */}
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h2 className="font-semibold text-heading mb-6">Risk Distribution</h2>
            <div className="relative h-40 w-40 mx-auto mb-6">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                {(() => {
                  let offset = 0
                  return riskBreakdown.map((r, i) => {
                    const circ = 2 * Math.PI * 40
                    const dash = (r.pct / 100) * circ
                    const el = <circle key={i} cx="50" cy="50" r="40" fill="none" stroke={r.color.replace('bg-', 'var(--color-')} strokeWidth="12" strokeDasharray={`${dash} ${circ - dash}`} strokeDashoffset={-offset} className={r.color.replace('bg-', 'stroke-')} />
                    offset += dash
                    return el
                  })
                })()}
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold text-heading">100</span>
                <span className="text-xs text-muted">contracts</span>
              </div>
            </div>
            <div className="space-y-2">
              {riskBreakdown.map((r, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`h-2.5 w-2.5 rounded-full ${r.color}`} />
                    <span className="text-xs text-body">{r.level}</span>
                  </div>
                  <span className="text-xs font-semibold text-heading">{r.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Clause Heatmap */}
        <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
          <h2 className="font-semibold text-heading mb-6">Clause Analysis Heatmap</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {clauseTypes.map((c, i) => {
              const intensity = c.avgRisk >= 7 ? 'bg-red-100 border-red-200' : c.avgRisk >= 5 ? 'bg-amber-50 border-amber-200' : 'bg-emerald-50 border-emerald-200'
              const textC = c.avgRisk >= 7 ? 'text-red-600' : c.avgRisk >= 5 ? 'text-amber-600' : 'text-emerald-600'
              return (
                <div key={i} className={`rounded-xl p-4 border ${intensity} hover:shadow-md transition`}>
                  <h4 className="text-sm font-semibold text-heading mb-1">{c.type}</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted">{c.total} found</span>
                    <span className={`text-sm font-bold ${textC}`}>{c.avgRisk}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
