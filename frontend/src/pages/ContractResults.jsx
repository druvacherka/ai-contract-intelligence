import { useLocation, Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ThemeToggle from '../components/ThemeToggle'
import { useAuth } from '../context/AuthContext'

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
  const { user, logout } = useAuth()
  const [mounted, setMounted] = useState(false)
  const [selectedClause, setSelectedClause] = useState(null)
  const [showSummaryView, setShowSummaryView] = useState(false)
  const [fullscreenPanel, setFullscreenPanel] = useState(null) // 'viewer' | 'analytics' | null

  const result = location.state?.result || null
  const activeResult = result
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

  useEffect(() => {
    if (activeResult) {
      const history = JSON.parse(localStorage.getItem('IntelliAnalyze AI_history') || '[]')
      const docId = activeResult.document_id || activeResult.id
      const exists = history.some(h => h.document_id === docId || (h.fileName === fileName && h.timestamp && (Date.now() - new Date(h.timestamp).getTime() < 5000)))
      if (!exists) {
        const entry = {
          ...activeResult,
          fileName,
          timestamp: new Date().toISOString(),
          id: docId || Date.now().toString(),
        }
        history.unshift(entry)
        if (history.length > 50) history.length = 50
        localStorage.setItem('IntelliAnalyze AI_history', JSON.stringify(history))
      }
    }
  }, [activeResult, fileName])

  if (!activeResult) {
    return (
      <div className="min-h-screen bg-page">
        <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
          <Link to="/" className="text-xl font-bold text-heading">Intelli<span className="text-brand-500">Analyze</span></Link>
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

  // Normalize field names — handle both pipeline (new) and inline (old) field names
  const clause = activeResult.primary_clause || activeResult.clause || 'Unknown'
  const confidence = activeResult.primary_confidence || activeResult.confidence || 0
  const risk_score = activeResult.overall_risk_score || activeResult.risk_score || 0
  const risk_level = activeResult.overall_risk_level || activeResult.risk_level || 'Low'
  const contract_text = activeResult.contract_text || activeResult.clean_text || activeResult.text_preview || ''
  const rawSummary = activeResult.summary
  const summary = Array.isArray(rawSummary) ? rawSummary : []
  const rawRiskFactors = activeResult.risk_factors
  const risk_factors = Array.isArray(rawRiskFactors) ? rawRiskFactors : []
  const rawClauses = activeResult.clauses
  const clauses = Array.isArray(rawClauses) ? rawClauses : (rawClauses?.detected ? rawClauses.detected : [])
  const ai_summary = activeResult.ai_summary || ''
  const rawFindings = activeResult.key_findings
  const key_findings = Array.isArray(rawFindings) ? rawFindings : []
  const rawRecs = activeResult.recommendations
  const recommendations = Array.isArray(rawRecs) ? rawRecs : []
  const rawMissing = activeResult.missing_clauses
  const missing_clauses = Array.isArray(rawMissing) ? rawMissing : []
  const completeness_score = activeResult.completeness_score ?? null
  const entities = activeResult.entities || {}
  const clause_risks = activeResult.clause_risks || []
  const pages = activeResult.pages || 0
  const ocr_method = activeResult.ocr_method || activeResult.processing_method || 'native'
  const ocr_confidence = activeResult.ocr_confidence || 0
  const word_count = contract_text ? contract_text.split(/\s+/).filter(Boolean).length : 0

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

  const renderSummaryView = () => {
    const sections = []

    // Contract Overview
    sections.push(
      <div key="overview" className="p-4 rounded-xl bg-brand-50/50 border border-brand-200 dark:bg-brand-500/5 dark:border-brand-500/15 mb-4">
        <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">📄 Contract Overview</h4>
        <div className="grid grid-cols-2 gap-2 text-xs text-body">
          <p><strong>Type:</strong> {clause}</p>
          <p><strong>Pages:</strong> {pages || 'N/A'}</p>
          <p><strong>Words:</strong> {word_count.toLocaleString()}</p>
          <p><strong>Risk:</strong> <span className={risk_level === 'High' ? 'text-red-600 font-bold' : risk_level === 'Medium' ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold'}>{risk_level} ({risk_score}/100)</span></p>
        </div>
      </div>
    )

    // AI Summary
    if (ai_summary) {
      sections.push(
        <div key="ai-sum" className="p-4 rounded-xl bg-purple-50/50 border border-purple-200 dark:bg-purple-500/5 dark:border-purple-500/15 mb-4">
          <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">🧠 AI Intelligence Summary</h4>
          <p className="text-sm text-body leading-relaxed">{ai_summary}</p>
        </div>
      )
    }

    // Key Findings
    if (key_findings && key_findings.length > 0) {
      sections.push(
        <div key="findings" className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 dark:bg-emerald-500/5 dark:border-emerald-500/15 mb-4">
          <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">🔑 Key Findings</h4>
          <ul className="space-y-1.5">
            {key_findings.map((f, i) => <li key={i} className="text-sm text-body flex items-start gap-2"><span className="text-emerald-500 mt-0.5">✓</span><span>{f}</span></li>)}
          </ul>
        </div>
      )
    }

    // Clause Summary
    if (clauses && clauses.length > 0) {
      sections.push(
        <div key="clauses" className="p-4 rounded-xl bg-blue-50/50 border border-blue-200 dark:bg-blue-500/5 dark:border-blue-500/15 mb-4">
          <h4 className="text-sm font-bold text-heading mb-3 flex items-center gap-2">📋 Detected Clauses ({clauses.length})</h4>
          <div className="space-y-2">
            {clauses.map((c, i) => {
              const cRisk = c.risk_level || (c.risk_score > 60 ? 'High' : c.risk_score > 30 ? 'Medium' : 'Low')
              return (
                <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-card border border-theme">
                  <span className="text-base mt-0.5">{CLAUSE_ICONS[c.type] || '📋'}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-heading">{c.type}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-muted font-semibold">{c.confidence || 0}%</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${cRisk === 'High' ? 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400' : cRisk === 'Medium' ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400'}`}>{cRisk}</span>
                      </div>
                    </div>
                    <p className="text-xs text-body mt-1 line-clamp-2 leading-relaxed">{c.text}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )
    }

    // Recommendations
    if (recommendations && recommendations.length > 0) {
      sections.push(
        <div key="recs" className="p-4 rounded-xl bg-amber-50/50 border border-amber-200 dark:bg-amber-500/5 dark:border-amber-500/15 mb-4">
          <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">💡 Recommendations</h4>
          <ul className="space-y-1.5">
            {recommendations.map((r, i) => <li key={i} className="text-sm text-body flex items-start gap-2"><span className="text-amber-500 mt-0.5">→</span><span>{r}</span></li>)}
          </ul>
        </div>
      )
    }

    // Entities
    if (entities && Object.keys(entities).length > 0) {
      const entityItems = []
      if (entities.organizations?.length) entityItems.push(<p key="o" className="text-xs text-body"><strong>Organizations:</strong> {entities.organizations.join(', ')}</p>)
      if (entities.persons?.length) entityItems.push(<p key="p" className="text-xs text-body"><strong>Persons:</strong> {entities.persons.join(', ')}</p>)
      if (entities.dates?.length) entityItems.push(<p key="d" className="text-xs text-body"><strong>Dates:</strong> {entities.dates.join(', ')}</p>)
      if (entities.money_values?.length) entityItems.push(<p key="m" className="text-xs text-body"><strong>Money Values:</strong> {entities.money_values.join(', ')}</p>)
      if (entities.jurisdictions?.length) entityItems.push(<p key="j" className="text-xs text-body"><strong>Jurisdictions:</strong> {entities.jurisdictions.join(', ')}</p>)
      if (entityItems.length > 0) {
        sections.push(
          <div key="entities" className="p-4 rounded-xl bg-teal-50/50 border border-teal-200 dark:bg-teal-500/5 dark:border-teal-500/15 mb-4">
            <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">🏷️ Extracted Entities</h4>
            <div className="space-y-1.5">{entityItems}</div>
          </div>
        )
      }
    }

    // Missing Clauses
    if (missing_clauses && missing_clauses.length > 0) {
      sections.push(
        <div key="missing" className="p-4 rounded-xl bg-red-50/50 border border-red-200 dark:bg-red-500/5 dark:border-red-500/15 mb-4">
          <h4 className="text-sm font-bold text-heading mb-2 flex items-center gap-2">⚠️ Missing Clauses</h4>
          <div className="flex flex-wrap gap-2">
            {missing_clauses.map((mc, i) => <span key={i} className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-red-100 border border-red-200 text-red-700 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400">{mc}</span>)}
          </div>
        </div>
      )
    }

    return sections
  }

  const renderParagraphs = () => {
    if (!contract_text) return <p className="text-sm text-muted">No contract text available.</p>
    return contract_text.split('\n').map((para, idx) => {
      if (!para.trim()) return null
      return (
        <p key={idx} className="text-sm text-body leading-relaxed mb-4">
          {para}
        </p>
      )
    })
  }

  return (
    <div className="min-h-screen bg-page">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50 no-print">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <ThemeToggle />
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white text-xs font-bold uppercase cursor-pointer" title={user?.name || 'User'}>
              {user?.name?.[0] || 'U'}
            </div>
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

      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Header */}
        <div className={`text-center mb-10 ${mounted ? 'animate-slide-up' : 'opacity-0'}`}>
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-emerald-50 border border-emerald-200 mb-4 animate-check-pop">
            <span className="text-3xl">✅</span>
          </div>
          <h1 className="text-3xl font-bold text-heading mb-1">Analysis Complete</h1>
          <div className="flex items-center justify-center gap-3 mt-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-subtle border border-theme text-body">
              📄 {fileName}
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-subtle border border-theme text-muted">
              🕐 {new Date().toLocaleTimeString()}
            </span>
            {pages > 0 && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-subtle border border-theme text-muted">
                📖 {pages} pages
              </span>
            )}
            {word_count > 0 && (
              <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-subtle border border-theme text-muted">
                📝 {word_count.toLocaleString()} words
              </span>
            )}
          </div>
        </div>

        {/* Contract Overview Card */}
        <div className={`grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-8 ${mounted ? 'animate-slide-up stagger-1' : 'opacity-0'}`}>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">📄</span>
            <p className="text-lg font-extrabold text-heading">{clause}</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Contract Type</p>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">📖</span>
            <p className="text-lg font-extrabold text-heading">{pages || '—'}</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Pages</p>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">📝</span>
            <p className="text-lg font-extrabold text-heading">{word_count > 0 ? word_count.toLocaleString() : '—'}</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Words</p>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">🔍</span>
            <p className="text-lg font-extrabold text-heading">{ocr_method === 'native' || ocr_method === 'pdf_native' ? 'Digital' : 'OCR'}</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Extraction</p>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">📋</span>
            <p className="text-lg font-extrabold text-heading">{clauses.length}</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Clauses Found</p>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-4 shadow-theme text-center">
            <span className="text-2xl block mb-1">{risk_level === 'High' ? '🔴' : risk_level === 'Medium' ? '🟡' : '🟢'}</span>
            <p className="text-lg font-extrabold text-heading">{risk_score}/100</p>
            <p className="text-[10px] text-muted uppercase font-bold tracking-wider">Risk Score</p>
          </div>
        </div>

        {/* Main Grid — Left contract viewer + Right sticky analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* ── LEFT PANEL: Interactive Contract Viewer ── */}
          <div className={`lg:col-span-7 bg-card border border-theme rounded-2xl p-6 shadow-theme ${mounted ? 'animate-slide-up' : 'opacity-0'}`}>
            <div className="flex items-center justify-between pb-3 border-b border-theme mb-4">
              <h3 className="font-bold text-heading flex items-center gap-2">📄 {showSummaryView ? 'Contract Summary' : 'Interactive Contract Viewer'}</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowSummaryView(!showSummaryView)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all duration-300 ${
                    showSummaryView
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                      : 'bg-brand-50 border border-brand-200 text-brand-600 hover:bg-brand-100 dark:bg-brand-500/10 dark:border-brand-500/20 dark:text-brand-400 dark:hover:bg-brand-500/20'
                  }`}
                >
                  {showSummaryView ? '📄 Full Contract' : '⚡ Summarize in Short'}
                </button>
                <button onClick={() => setFullscreenPanel('viewer')} className="h-7 w-7 rounded-lg bg-subtle border border-theme flex items-center justify-center text-muted hover:text-heading hover:bg-card transition" title="Expand fullscreen">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                </button>
              </div>
            </div>
            <div className="pr-2 custom-scrollbar" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
              {showSummaryView ? renderSummaryView() : renderParagraphs()}
            </div>
          </div>

          {/* ── RIGHT PANEL: Analytics Summary (STICKY) ── */}
          <div className={`lg:col-span-5 space-y-5 custom-scrollbar ${mounted ? 'animate-slide-up' : 'opacity-0'}`} style={{ position: 'sticky', top: '1.5rem', alignSelf: 'start', maxHeight: 'calc(100vh - 3rem)', overflowY: 'auto' }}>

            {/* Expand fullscreen button */}
            <div className="flex justify-end">
              <button onClick={() => setFullscreenPanel('analytics')} className="h-7 w-7 rounded-lg bg-subtle border border-theme flex items-center justify-center text-muted hover:text-heading hover:bg-card transition" title="Expand analytics fullscreen">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
              </button>
            </div>
            
            {/* Predicted Clause */}
            <div className="glass-card rounded-2xl p-5 shadow-theme">
              <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2">Primary Clause Identified</span>
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center text-2xl shadow-lg shadow-brand-500/20 flex-shrink-0">
                  {icon}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-heading">{clause}</h2>
                  <p className="text-xs text-body mt-0.5 leading-relaxed">{description}</p>
                </div>
              </div>
            </div>

            {/* Metrics row */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card rounded-2xl p-5 shadow-theme flex flex-col justify-between">
                <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-3">Confidence</span>
                <ConfidenceBar value={confidence} />
              </div>
              <div className="glass-card rounded-2xl p-5 shadow-theme flex flex-col items-center justify-center text-center">
                <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2 self-start">Risk Score</span>
                <CircularGauge value={risk_score} size={110} strokeWidth={8} />
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="glass-card rounded-2xl p-5 shadow-theme">
              <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-3">Risk Assessment</span>
              <div className="flex items-center gap-4">
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl border-2 text-sm font-bold ${riskBg} ${riskGlow}`}>
                  {risk_level === 'High' ? '🔴' : risk_level === 'Medium' ? '🟡' : '🟢'}
                  <span>{risk_level} Risk</span>
                </div>
                <div className="text-xs text-body leading-relaxed flex-1">
                  {risk_level === 'High' && 'Significant risk indicators detected. Mandatory legal review recommended before execution.'}
                  {risk_level === 'Medium' && 'Moderate liability or vague terms flagged. Review suggested.'}
                  {risk_level === 'Low' && 'Favorable contract terms matching compliant baseline standards.'}
                </div>
              </div>
            </div>

            {/* AI Summary */}
            {summary && summary.length > 0 && (
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🤖 AI Summary</h3>
                <ul className="space-y-2">
                  {summary.map((sumItem, index) => (
                    <li key={index} className="text-xs text-body leading-relaxed flex items-start gap-2">
                      <span className="text-brand-500 mt-0.5">•</span>
                      <span>{sumItem}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* AI Intelligence Summary */}
            {ai_summary && (
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🧠 AI Intelligence Summary</h3>
                <p className="text-sm text-body leading-relaxed bg-subtle/50 p-4 rounded-xl border border-theme">{ai_summary}</p>
              </div>
            )}

            {/* Key Findings */}
            {key_findings && key_findings.length > 0 && (
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🔑 Key Findings</h3>
                <ul className="space-y-2">
                  {key_findings.map((finding, index) => (
                    <li key={index} className="text-xs text-body leading-relaxed flex items-start gap-2">
                      <span className="text-emerald-500 mt-0.5">✓</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {recommendations && recommendations.length > 0 && (
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">💡 Recommendations</h3>
                <ul className="space-y-2">
                  {recommendations.map((rec, index) => (
                    <li key={index} className="text-xs text-body leading-relaxed flex items-start gap-2">
                      <span className="text-amber-500 mt-0.5">→</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Completeness + Missing */}
            <div className="grid grid-cols-1 gap-4">
              {completeness_score != null && (
                <div className="glass-card rounded-2xl p-5 shadow-theme flex items-center gap-5">
                  <CircularGauge value={completeness_score} size={90} strokeWidth={7} />
                  <div>
                    <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-1">Completeness Score</span>
                    <p className="text-xs text-body">How complete the contract is relative to standard legal templates.</p>
                  </div>
                </div>
              )}
              {missing_clauses && missing_clauses.length > 0 && (
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">⚠️ Missing Clauses</h3>
                  <div className="flex flex-wrap gap-2">
                    {missing_clauses.map((mc, index) => (
                      <span key={index} className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-400">
                        {mc}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Entities */}
            {entities && Object.keys(entities).length > 0 && (
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🏷️ Extracted Entities</h3>
                <div className="space-y-3">
                  {entities.organizations && entities.organizations.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wider">Organizations</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {entities.organizations.map((org, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 dark:bg-blue-500/10 dark:border-blue-500/20 dark:text-blue-400 font-medium">{org}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {entities.persons && entities.persons.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wider">Persons</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {entities.persons.map((p, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-700 dark:bg-purple-500/10 dark:border-purple-500/20 dark:text-purple-400 font-medium">{p}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {entities.dates && entities.dates.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wider">Dates</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {entities.dates.map((d, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-teal-50 border border-teal-200 text-teal-700 dark:bg-teal-500/10 dark:border-teal-500/20 dark:text-teal-400 font-medium">{d}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {entities.money_values && entities.money_values.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wider">Money Values</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {entities.money_values.map((m, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400 font-medium">{m}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {entities.jurisdictions && entities.jurisdictions.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wider">Jurisdictions</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {entities.jurisdictions.map((j, i) => (
                          <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-400 font-medium">{j}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>

        </div>

        {/* ── Full-width sections below the grid ── */}

        {/* Clause-by-Clause Breakdown */}
        {clauses && clauses.length > 0 && (
          <div className={`mt-8 bg-card border border-theme rounded-2xl p-6 shadow-theme ${mounted ? 'animate-slide-up stagger-3' : 'opacity-0'}`}>
            <h3 className="text-xs font-bold text-heading mb-5 uppercase tracking-wider">📋 Clause-by-Clause Analysis ({clauses.length} detected)</h3>
            <div className="space-y-3">
              {clauses.map((c, idx) => {
                const cRisk = c.risk_level || (c.risk_score > 60 ? 'High' : c.risk_score > 30 ? 'Medium' : 'Low')
                const cBg = cRisk === 'High' 
                  ? 'border-l-red-500 bg-red-50/50 dark:bg-red-500/5' 
                  : cRisk === 'Medium' 
                  ? 'border-l-amber-500 bg-amber-50/50 dark:bg-amber-500/5' 
                  : 'border-l-emerald-500 bg-emerald-50/50 dark:bg-emerald-500/5'
                return (
                  <div key={idx} className={`border-l-4 rounded-xl p-4 border border-theme cursor-pointer hover:shadow-md transition ${cBg}`} onClick={() => setSelectedClause(c)}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{CLAUSE_ICONS[c.type] || '📋'}</span>
                        <h4 className="font-bold text-heading text-sm">{c.type}</h4>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] font-bold text-muted uppercase">{c.confidence || 0}% conf</span>
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-lg border ${cRisk === 'High' ? 'risk-high' : cRisk === 'Medium' ? 'risk-med' : 'risk-low'}`}>
                          {cRisk} • {c.risk_score || 0}/100
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-body leading-relaxed line-clamp-2">{c.text}</p>
                    {c.risk_factors && c.risk_factors.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {c.risk_factors.map((f, fi) => (
                          <span key={fi} className="text-[10px] px-2 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 font-medium">⚠ {f}</span>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Compliance Check */}
        <div className={`mt-8 bg-card border border-theme rounded-2xl p-6 shadow-theme ${mounted ? 'animate-slide-up stagger-4' : 'opacity-0'}`}>
          <h3 className="text-xs font-bold text-heading mb-4 uppercase tracking-wider">✅ Compliance Check</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            {['Termination', 'Confidentiality', 'Liability', 'Indemnification', 'Arbitration', 'Governing Law', 'Payment Terms', 'Warranty', 'Renewal', 'Non-Compete'].map((ct) => {
              const found = clauses.some(c => c.type === ct)
              return (
                <div key={ct} className={`flex items-center gap-2 p-3 rounded-xl border text-xs font-semibold ${found ? 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400' : 'bg-red-50 border-red-200 text-red-600 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400'}`}>
                  <span>{found ? '✓' : '✗'}</span>
                  <span>{ct}</span>
                </div>
              )
            })}
          </div>
          {missing_clauses && missing_clauses.length > 0 && (
            <p className="text-xs text-amber-600 dark:text-amber-400 mt-3 font-semibold">⚠️ {missing_clauses.length} standard clause(s) not detected — review recommended before execution.</p>
          )}
        </div>

        {/* Extracted Entities Card */}
        {result.entities && result.entities.length > 0 && (
          <div className="md:col-span-2 glass-card rounded-2xl p-8 shadow-theme result-card-enter stagger-5 mt-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">🏷️ Extracted Legal Entities</span>
            </div>
            <div className="flex flex-wrap gap-2.5">
              {result.entities.map((entity, index) => (
                <div
                  key={index}
                  className="text-sm px-3.5 py-2 rounded-xl bg-subtle border border-theme text-body flex items-center gap-2"
                >
                  <span className="font-semibold text-brand-600 dark:text-brand-400">{entity.text}</span>
                  <span className="text-[10px] font-bold text-muted bg-card px-2 py-0.5 rounded border border-theme uppercase tracking-wider">{entity.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
          <button
            onClick={() => navigate('/upload')}
            className="w-full sm:w-auto bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white px-8 py-3.5 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2"
          >
            📤 Analyze Another Contract
          </button>
          <button
            onClick={async () => {
              const contractId = activeResult?.document_id || activeResult?.id
              if (!contractId) { window.print(); return }
              try {
                const blob = await api.downloadReport(contractId)
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `${fileName.replace(/\.[^/.]+$/, '')}_report.pdf`
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                window.URL.revokeObjectURL(url)
              } catch {
                window.print()
              }
            }}
            className="w-full sm:w-auto bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme flex items-center justify-center gap-2"
          >
            📥 Download PDF Report
          </button>
          <button
            onClick={() => window.print()}
            className="w-full sm:w-auto bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme flex items-center justify-center gap-2"
          >
            🖨️ Print Report
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full sm:w-auto bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme flex items-center justify-center gap-2"
          >
            📊 View Dashboard
          </button>
        </div>
      </div>

      {/* Hidden PDF Printable Report Layout (Visible during print only) */}
      <div className="hidden print-block p-10 font-sans bg-white text-black min-h-screen">
        <div className="flex justify-between items-center border-b-2 border-gray-300 pb-4 mb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">IntelliAnalyze AI</h1>
            <p className="text-xs text-gray-500 font-semibold uppercase mt-0.5">Contract Intelligence & Risk Assessment Report</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-red-600">Risk Assessment: {risk_level}</p>
            <p className="text-xs text-gray-400">Date Generated: {new Date().toLocaleString()}</p>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-sm font-extrabold uppercase text-gray-400 tracking-wider mb-2">Metadata Summary</h2>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div><span className="font-semibold text-gray-600">File Name:</span> {fileName}</div>
            <div><span className="font-semibold text-gray-600">Primary Clause Type:</span> {clause}</div>
            <div><span className="font-semibold text-gray-600">Composite Risk Score:</span> {risk_score} / 100</div>
            <div><span className="font-semibold text-gray-600">Model Confidence:</span> {confidence}%</div>
          </div>
        </div>

        {summary && summary.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-extrabold uppercase text-gray-400 tracking-wider mb-2 border-b pb-1">Executive Summary</h2>
            <ul className="list-disc pl-5 space-y-1 text-xs text-gray-700">
              {summary.map((sumItem, idx) => (
                <li key={idx}>{sumItem}</li>
              ))}
            </ul>
          </div>
        )}

        {risk_factors && risk_factors.length > 0 && (
          <div className="mb-6" style={{ pageBreakInside: 'avoid' }}>
            <h2 className="text-sm font-extrabold uppercase text-gray-400 tracking-wider mb-2 border-b pb-1">Key Risk Factors</h2>
            <ul className="list-disc pl-5 space-y-1 text-xs text-red-600 font-medium">
              {risk_factors.map((factor, idx) => (
                <li key={idx}>{factor}</li>
              ))}
            </ul>
          </div>
        )}

        {clauses && clauses.length > 0 && (
          <div className="mb-6" style={{ pageBreakInside: 'avoid' }}>
            <h2 className="text-sm font-extrabold uppercase text-gray-400 tracking-wider mb-2 border-b pb-1">Identified Clauses & Risk Breakdown</h2>
            <table className="min-w-full text-left text-xs text-gray-700 border mt-2">
              <thead className="bg-gray-100 uppercase text-[10px] text-gray-600 font-bold border-b">
                <tr>
                  <th className="p-2 border">Clause Type</th>
                  <th className="p-2 border">Risk Score</th>
                  <th className="p-2 border">Risk Level</th>
                  <th className="p-2 border">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {clauses.map((c, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="p-2 border font-semibold">{c.type}</td>
                    <td className="p-2 border">{c.risk_score} / 100</td>
                    <td className={`p-2 border font-bold ${c.risk_level === 'High' ? 'text-red-600' : c.risk_level === 'Medium' ? 'text-yellow-600' : 'text-green-600'}`}>{c.risk_level}</td>
                    <td className="p-2 border">{c.confidence}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="border-t border-gray-200 pt-6 mt-10 text-center text-[10px] text-gray-400">
          This report was generated using IntelliAnalyze AI automated AI legal analysis engine. Independent legal counsel review is advised before final signature.
        </div>
      </div>

      {/* ══════ FULLSCREEN MODAL: Contract Viewer ══════ */}
      {fullscreenPanel === 'viewer' && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in" onClick={() => setFullscreenPanel(null)}>
          <div className="bg-card border border-theme rounded-2xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-theme flex-shrink-0">
              <h3 className="font-bold text-heading flex items-center gap-2 text-lg">📄 {showSummaryView ? 'Contract Summary' : 'Full Contract Viewer'}</h3>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowSummaryView(!showSummaryView)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${
                    showSummaryView ? 'bg-brand-600 text-white' : 'bg-brand-50 border border-brand-200 text-brand-600 dark:bg-brand-500/10 dark:border-brand-500/20 dark:text-brand-400'
                  }`}
                >
                  {showSummaryView ? '📄 Full Text' : '⚡ Summary'}
                </button>
                <button onClick={() => setFullscreenPanel(null)} className="h-9 w-9 rounded-xl bg-subtle border border-theme flex items-center justify-center text-heading hover:bg-red-50 hover:text-red-500 hover:border-red-200 dark:hover:bg-red-500/10 transition text-lg font-bold">×</button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
              {showSummaryView ? renderSummaryView() : renderParagraphs()}
            </div>
          </div>
        </div>
      )}

      {/* ══════ FULLSCREEN MODAL: Analytics ══════ */}
      {fullscreenPanel === 'analytics' && (
        <div className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in" onClick={() => setFullscreenPanel(null)}>
          <div className="bg-card border border-theme rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-theme flex-shrink-0">
              <h3 className="font-bold text-heading flex items-center gap-2 text-lg">📊 Full Analytics & Intelligence Report</h3>
              <button onClick={() => setFullscreenPanel(null)} className="h-9 w-9 rounded-xl bg-subtle border border-theme flex items-center justify-center text-heading hover:bg-red-50 hover:text-red-500 hover:border-red-200 dark:hover:bg-red-500/10 transition text-lg font-bold">×</button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar space-y-5">
              {/* Clause + Metrics */}
              <div className="glass-card rounded-2xl p-5 shadow-theme">
                <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2">Primary Clause</span>
                <div className="flex items-center gap-4">
                  <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-400 flex items-center justify-center text-2xl shadow-lg shadow-brand-500/20 flex-shrink-0">{icon}</div>
                  <div>
                    <h2 className="text-2xl font-bold text-heading">{clause}</h2>
                    <p className="text-xs text-body mt-0.5">{description}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="glass-card rounded-2xl p-5 shadow-theme text-center">
                  <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2">Confidence</span>
                  <ConfidenceBar value={confidence} />
                </div>
                <div className="glass-card rounded-2xl p-5 shadow-theme flex flex-col items-center">
                  <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2 self-start">Risk Score</span>
                  <CircularGauge value={risk_score} size={100} strokeWidth={7} />
                </div>
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest block mb-2">Risk Level</span>
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border-2 text-sm font-bold mt-2 ${riskBg}`}>
                    {risk_level === 'High' ? '🔴' : risk_level === 'Medium' ? '🟡' : '🟢'} {risk_level}
                  </div>
                </div>
              </div>

              {ai_summary && (
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🧠 AI Summary</h3>
                  <p className="text-sm text-body leading-relaxed">{ai_summary}</p>
                </div>
              )}

              {key_findings && key_findings.length > 0 && (
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🔑 Key Findings</h3>
                  <ul className="space-y-2">{key_findings.map((f, i) => <li key={i} className="text-sm text-body flex items-start gap-2"><span className="text-emerald-500">✓</span><span>{f}</span></li>)}</ul>
                </div>
              )}

              {recommendations && recommendations.length > 0 && (
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">💡 Recommendations</h3>
                  <ul className="space-y-2">{recommendations.map((r, i) => <li key={i} className="text-sm text-body flex items-start gap-2"><span className="text-amber-500">→</span><span>{r}</span></li>)}</ul>
                </div>
              )}

              {entities && Object.keys(entities).length > 0 && (
                <div className="glass-card rounded-2xl p-5 shadow-theme">
                  <h3 className="text-xs font-bold text-heading mb-3 uppercase tracking-wider">🏷️ All Entities</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {entities.organizations?.length > 0 && <div><span className="text-[10px] font-bold text-muted uppercase">Organizations</span><div className="flex flex-wrap gap-1.5 mt-1">{entities.organizations.map((o,i) => <span key={i} className="text-xs px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-700 dark:bg-blue-500/10 dark:border-blue-500/20 dark:text-blue-400">{o}</span>)}</div></div>}
                    {entities.persons?.length > 0 && <div><span className="text-[10px] font-bold text-muted uppercase">Persons</span><div className="flex flex-wrap gap-1.5 mt-1">{entities.persons.map((p,i) => <span key={i} className="text-xs px-2 py-0.5 rounded bg-purple-50 border border-purple-200 text-purple-700 dark:bg-purple-500/10 dark:border-purple-500/20 dark:text-purple-400">{p}</span>)}</div></div>}
                    {entities.dates?.length > 0 && <div><span className="text-[10px] font-bold text-muted uppercase">Dates</span><div className="flex flex-wrap gap-1.5 mt-1">{entities.dates.map((d,i) => <span key={i} className="text-xs px-2 py-0.5 rounded bg-teal-50 border border-teal-200 text-teal-700 dark:bg-teal-500/10 dark:border-teal-500/20 dark:text-teal-400">{d}</span>)}</div></div>}
                    {entities.money_values?.length > 0 && <div><span className="text-[10px] font-bold text-muted uppercase">Money</span><div className="flex flex-wrap gap-1.5 mt-1">{entities.money_values.map((m,i) => <span key={i} className="text-xs px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-700 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400">{m}</span>)}</div></div>}
                    {entities.jurisdictions?.length > 0 && <div><span className="text-[10px] font-bold text-muted uppercase">Jurisdictions</span><div className="flex flex-wrap gap-1.5 mt-1">{entities.jurisdictions.map((j,i) => <span key={i} className="text-xs px-2 py-0.5 rounded bg-rose-50 border border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/20 dark:text-rose-400">{j}</span>)}</div></div>}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
