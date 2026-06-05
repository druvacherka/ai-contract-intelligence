import { useLocation, Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ThemeToggle from '../components/ThemeToggle'

const CLAUSE_ICONS = {
  'Termination': '⚖️',
  'Confidentiality': '🔒',
  'Liability': '⚠️',
  'Arbitration': '🏛️',
  'Governing Law': '📜',
  'Payment Terms': '💳',
  'Warranty': '🛡️',
  'Renewal': '🔄',
  'Indemnification': '🛡️',
  'Non-Compete': '🚫',
}

const CLAUSE_DESCRIPTIONS = {
  'Termination': 'Conditions and procedures for ending the contract agreement.',
  'Confidentiality': 'Protection of proprietary information and trade secrets.',
  'Liability': 'Allocation of legal responsibility and financial obligations.',
  'Arbitration': 'Dispute resolution through binding arbitration procedures.',
  'Governing Law': 'Jurisdiction and legal framework governing the agreement.',
  'Payment Terms': 'Payment schedules, amounts, and financial conditions.',
  'Warranty': 'Guarantees and representations about products or services.',
  'Renewal': 'Terms for contract extension, auto-renewal, and continuation.',
  'Indemnification': 'Protection against losses, damages, and third-party claims.',
  'Non-Compete': 'Restrictions on competitive activities after agreement.',
}

function CircularGauge({ value, size = 160, strokeWidth = 12 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  const color =
    value <= 30 ? '#10b981' :
    value <= 70 ? '#f59e0b' :
    '#f43f5e'

  const trackColor = 'rgba(139, 92, 246, 0.1)'

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={trackColor}
          strokeWidth={strokeWidth}
        />
        {/* Fill */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            animation: 'gauge-fill 1.8s ease-out forwards',
            filter: `drop-shadow(0 0 6px ${color}40)`,
          }}
        />
      </svg>
      {/* Center Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-heading animate-count-up">{value}</span>
        <span className="text-xs text-muted mt-0.5">/ 100</span>
      </div>
    </div>
  )
}

function ConfidenceBar({ value }) {
  const color =
    value >= 80 ? 'from-emerald-500 to-emerald-400' :
    value >= 50 ? 'from-amber-500 to-amber-400' :
    'from-red-500 to-red-400'

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-2">
        <span className="text-3xl font-bold text-heading animate-count-up">{value}%</span>
      </div>
      <div className="h-3 rounded-full progress-track overflow-hidden border border-theme">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color}`}
          style={{
            width: `${value}%`,
            animation: 'fill-bar 1.5s ease-out forwards',
            boxShadow: value >= 80
              ? '0 0 12px rgba(16,185,129,0.4)'
              : value >= 50
              ? '0 0 12px rgba(245,158,11,0.4)'
              : '0 0 12px rgba(244,63,94,0.4)',
          }}
        />
      </div>
    </div>
  )
}

export default function ContractResults() {
  const location = useLocation()
  const navigate = useNavigate()
  const [mounted, setMounted] = useState(false)

  const result = location.state?.result || null
  const fileName = location.state?.fileName || 'Unknown Document'

  useEffect(() => {
    setMounted(true)
    // Save to localStorage for Dashboard history
    if (result) {
      const history = JSON.parse(localStorage.getItem('contractiq_history') || '[]')
      const entry = {
        ...result,
        fileName,
        timestamp: new Date().toISOString(),
        id: Date.now().toString(),
      }
      history.unshift(entry)
      // Keep last 50
      if (history.length > 50) history.length = 50
      localStorage.setItem('contractiq_history', JSON.stringify(history))
    }
  }, [])

  if (!result) {
    return (
      <div className="min-h-screen bg-page">
        <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
          <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
          <div className="flex items-center gap-4">
            <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
            <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
            <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
            <ThemeToggle />
          </div>
        </nav>
        <div className="max-w-2xl mx-auto px-6 py-24 text-center">
          <div className="text-6xl mb-6">📄</div>
          <h2 className="text-2xl font-bold text-heading mb-3">No Analysis Results</h2>
          <p className="text-body mb-8">Upload a contract to see the AI analysis results here.</p>
          <Link to="/upload" className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-8 py-3.5 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20">
            📤 Upload Contract
          </Link>
        </div>
      </div>
    )
  }

  const { clause, confidence, risk_score, risk_level } = result
  const icon = CLAUSE_ICONS[clause] || '📋'
  const description = CLAUSE_DESCRIPTIONS[clause] || 'Legal clause detected in the contract.'

  const riskGlow =
    risk_level === 'High' ? 'glow-red animate-glow-pulse' :
    risk_level === 'Medium' ? 'glow-amber' :
    'glow-green'

  const riskBg =
    risk_level === 'High' ? 'bg-red-50 border-red-200 text-red-700' :
    risk_level === 'Medium' ? 'bg-amber-50 border-amber-200 text-amber-700' :
    'bg-emerald-50 border-emerald-200 text-emerald-700'

  const riskBgDark =
    risk_level === 'High' ? 'dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400' :
    risk_level === 'Medium' ? 'dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-400' :
    'dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400'

  return (
    <div className="min-h-screen bg-page">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Header */}
        <div className={`text-center mb-10 ${mounted ? 'animate-slide-up' : 'opacity-0'}`}>
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-emerald-50 border border-emerald-200 mb-4 animate-check-pop">
            <span className="text-3xl">✅</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-heading mb-2">Analysis Complete</h1>
          <div className="flex items-center justify-center gap-3 mt-3">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-subtle border border-theme text-body">
              📄 {fileName}
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-subtle border border-theme text-muted">
              🕐 {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>

        {/* Main Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Card 1: Predicted Clause — Full Width */}
          <div className={`md:col-span-2 glass-card rounded-2xl p-8 shadow-theme result-card-enter stagger-1`}>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Predicted Clause Type</span>
            </div>
            <div className="flex items-center gap-5">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center text-3xl shadow-lg shadow-brand-500/20 flex-shrink-0">
                {icon}
              </div>
              <div>
                <h2 className="text-3xl md:text-4xl font-bold text-heading">{clause}</h2>
                <p className="text-sm text-body mt-1 leading-relaxed max-w-lg">{description}</p>
              </div>
            </div>
          </div>

          {/* Card 2: Confidence Score */}
          <div className="glass-card rounded-2xl p-8 shadow-theme result-card-enter stagger-2">
            <div className="flex items-center gap-2 mb-6">
              <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Model Confidence</span>
            </div>
            <ConfidenceBar value={confidence} />
            <p className="text-xs text-muted mt-4">Prediction certainty based on NLP analysis</p>
          </div>

          {/* Card 3: Risk Score — Circular Gauge */}
          <div className="glass-card rounded-2xl p-8 shadow-theme result-card-enter stagger-3">
            <div className="flex items-center gap-2 mb-6">
              <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Risk Score</span>
            </div>
            <div className="flex flex-col items-center">
              <CircularGauge value={risk_score} />
              <p className="text-xs text-muted mt-4">Multi-factor risk assessment</p>
            </div>
          </div>

          {/* Card 4: Risk Level */}
          <div className={`md:col-span-2 glass-card rounded-2xl p-8 shadow-theme result-card-enter stagger-4`}>
            <div className="flex items-center gap-2 mb-6">
              <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Risk Assessment</span>
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className={`inline-flex items-center gap-3 px-8 py-4 rounded-2xl border-2 text-2xl font-bold ${riskBg} ${riskGlow}`}>
                {risk_level === 'High' ? '🔴' : risk_level === 'Medium' ? '🟡' : '🟢'}
                <span>{risk_level} Risk</span>
              </div>
              <div className="text-sm text-body leading-relaxed">
                {risk_level === 'High' && 'This contract contains significant risk factors. Legal review is strongly recommended before execution.'}
                {risk_level === 'Medium' && 'Moderate risk factors detected. Consider reviewing flagged clauses with your legal team.'}
                {risk_level === 'Low' && 'This contract appears to have favorable terms with minimal risk exposure.'}
              </div>
            </div>
          </div>

          {/* Summary Card */}
          <div className="md:col-span-2 bg-card border border-theme rounded-2xl p-6 shadow-theme result-card-enter stagger-4">
            <h3 className="font-semibold text-heading mb-4 text-sm uppercase tracking-wider">Analysis Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                <div className="text-2xl mb-1">{icon}</div>
                <div className="text-sm font-bold text-heading">{clause}</div>
                <div className="text-xs text-muted">Clause</div>
              </div>
              <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                <div className="text-2xl mb-1 font-bold text-heading">{confidence}%</div>
                <div className="text-xs text-muted">Confidence</div>
              </div>
              <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                <div className="text-2xl mb-1 font-bold text-heading">{risk_score}</div>
                <div className="text-xs text-muted">Risk Score</div>
              </div>
              <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                <div className={`text-sm font-bold px-3 py-1 rounded-full inline-block border ${riskBg}`}>{risk_level}</div>
                <div className="text-xs text-muted mt-1">Risk Level</div>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
          <button
            onClick={() => navigate('/upload')}
            className="w-full sm:w-auto bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white px-8 py-3.5 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2"
          >
            📤 Upload Another Contract
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full sm:w-auto bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme flex items-center justify-center gap-2"
          >
            📊 View Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
