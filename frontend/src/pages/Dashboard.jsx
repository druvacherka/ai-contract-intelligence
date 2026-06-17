import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import ThemeToggle from '../components/ThemeToggle'

export default function Dashboard() {
  const [history, setHistory] = useState([])

  useEffect(() => {
    // ── Migrate old localStorage keys from before the rename ──
    const OLD_KEYS = ['ContractIQ_history', 'contractiq_history', 'contractIQ_history']
    const NEW_KEY = 'IntelliAnalyze AI_history'
    OLD_KEYS.forEach(oldKey => {
      const oldData = localStorage.getItem(oldKey)
      if (oldData) {
        try {
          const oldItems = JSON.parse(oldData)
          const existing = JSON.parse(localStorage.getItem(NEW_KEY) || '[]')
          const ids = new Set(existing.map(e => e.document_id || e.id))
          oldItems.forEach(item => {
            const k = item.document_id || item.id
            if (k && !ids.has(k)) { existing.push(item); ids.add(k) }
          })
          localStorage.setItem(NEW_KEY, JSON.stringify(existing))
          localStorage.removeItem(oldKey)
          console.log(`[Migration] Merged ${oldItems.length} items from ${oldKey}`)
        } catch { /* ignore parse errors */ }
      }
    })
  }, [])

  useEffect(() => {
    async function loadData() {
      try {
        let apiHistory = []

        // Try MongoDB-backed contracts endpoint first
        try {
          const contractsData = await api.getContracts()
          const contracts = contractsData.contracts || contractsData || []
          apiHistory = (Array.isArray(contracts) ? contracts : []).map(doc => ({
            document_id: doc.contract_id || doc.document_id || doc.id,
            contract_id: doc.contract_id || doc.document_id || doc.id,
            id: doc.contract_id || doc.document_id || doc.id,
            fileName: doc.filename || doc.fileName,
            clause: doc.primary_clause || doc.clause || 'Unknown',
            confidence: doc.primary_confidence || doc.confidence || 0,
            risk_score: doc.overall_risk_score || doc.risk_score || 0,
            risk_level: doc.overall_risk_level || doc.risk_level || 'Low',
            completeness_score: doc.completeness_score || null,
            ai_summary: doc.ai_summary || '',
            entities: doc.entities || {},
            timestamp: doc.created_at || doc.processed_at || new Date().toISOString(),
          }))
        } catch {
          // Fall back to in-memory endpoint
          try {
            const data = await api.listDocuments()
            apiHistory = (data.documents || []).map(doc => ({
              document_id: doc.contract_id || doc.document_id,
              contract_id: doc.contract_id || doc.document_id,
              id: doc.contract_id || doc.document_id,
              fileName: doc.filename,
              clause: doc.primary_clause || doc.clause || 'Unknown',
              confidence: doc.primary_confidence || doc.confidence || 0,
              risk_score: doc.overall_risk_score || doc.risk_score || 0,
              risk_level: doc.overall_risk_level || doc.risk_level || 'Low',
              completeness_score: doc.completeness_score || null,
              ai_summary: doc.ai_summary || '',
              timestamp: doc.created_at || doc.processed_at || new Date().toISOString(),
            }))
          } catch { /* both endpoints failed */ }
        }

        const localHistory = JSON.parse(localStorage.getItem('IntelliAnalyze AI_history') || '[]')
        const seen = new Set()
        const merged = []

        apiHistory.forEach(item => {
          if (item.document_id && !seen.has(item.document_id)) {
            seen.add(item.document_id)
            merged.push(item)
          }
        })

        localHistory.forEach(item => {
          const key = item.document_id || item.id
          if (key && !seen.has(key)) {
            seen.add(key)
            merged.push(item)
          }
        })

        merged.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        setHistory(merged)
        
        // Save stats to user in LocalStorage if needed
        if (user) {
          user.contractsUploaded = merged.length
          user.contractsProcessed = merged.filter(m => m.clause && m.clause !== 'Unknown').length
          localStorage.setItem('IntelliAnalyze AI_user', JSON.stringify(user))
        }
      } catch (err) {
        console.error("Failed to load documents from API, falling back to localStorage:", err)
        const stored = JSON.parse(localStorage.getItem('IntelliAnalyze AI_history') || '[]')
        setHistory(stored)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // Compute dynamic stats
  const totalContracts = history.length
  const analyzed = history.filter(h => h.clause && h.clause !== 'Unknown').length
  const highRisk = history.filter(h => h.risk_level === 'High').length
  const avgRisk = history.length > 0
    ? (history.reduce((sum, h) => sum + (h.risk_score || 0), 0) / history.length).toFixed(1)
    : '0.0'
  const avgCompleteness = history.filter(h => h.completeness_score != null).length > 0
    ? Math.round(history.filter(h => h.completeness_score != null).reduce((sum, h) => sum + h.completeness_score, 0) / history.filter(h => h.completeness_score != null).length)
    : null

  const stats = [
    { label: 'Total Contracts', value: totalContracts || '0', change: totalContracts > 0 ? `${totalContracts} analyzed` : 'None yet', icon: '📄' },
    { label: 'Classified Clauses', value: analyzed || '0', change: totalContracts > 0 ? `${Math.round((analyzed / totalContracts) * 100)}% classified` : '—', icon: '✅' },
    { label: 'High Risk Flagged', value: highRisk || '0', change: highRisk > 0 ? `${highRisk} flagged` : 'None', icon: '⚠️' },
    { label: avgCompleteness != null ? 'Completeness' : 'Average Risk Score', value: avgCompleteness != null ? `${avgCompleteness}%` : avgRisk, change: avgCompleteness != null ? 'avg score' : '/ 100', icon: avgCompleteness != null ? '📋' : '📊' },
  ]

  // Recent contracts
  const recent = history.slice(0, 6)

  // Clause counts
  const clauseCounts = {}
  history.forEach(h => {
    if (h.clause && h.clause !== 'Unknown') {
      clauseCounts[h.clause] = (clauseCounts[h.clause] || 0) + 1
    }
  })
  const sortedClauses = Object.entries(clauseCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([type, count]) => ({
      type,
      count,
      pct: totalContracts > 0 ? Math.round((count / totalContracts) * 100) : 0,
    }))

  // Risk distribution
  const lowCount = history.filter(h => h.risk_level === 'Low').length
  const medCount = history.filter(h => h.risk_level === 'Medium').length
  const highCount = history.filter(h => h.risk_level === 'High').length
  const riskDistribution = [
    { l: 'Low', h: totalContracts > 0 ? Math.round((lowCount / totalContracts) * 100) : 0, c: 'bg-emerald-400' },
    { l: 'Medium', h: totalContracts > 0 ? Math.round((medCount / totalContracts) * 100) : 0, c: 'bg-amber-400' },
    { l: 'High', h: totalContracts > 0 ? Math.round((highCount / totalContracts) * 100) : 0, c: 'bg-red-400' },
  ]

  const rc = r => r === 'High' ? 'risk-high' : r === 'Medium' ? 'risk-med' : r === 'Low' ? 'risk-low' : 'risk-none'

  const clauseIcon = (clause) => {
    const map = {
      'Termination': '⚖️', 'Confidentiality': '🔒', 'Liability': '⚠️',
      'Arbitration': '🏛️', 'Governing Law': '📜', 'Payment Terms': '💳',
      'Warranty': '🛡️', 'Renewal': '🔄', 'Indemnification': '🛡️', 'Non-Compete': '🚫',
    }
    return map[clause] || '📋'
  }

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav-active font-semibold">Dashboard</Link>
          <ThemeToggle />
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white text-xs font-bold">P</div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div><h1 className="text-2xl font-bold text-heading">Dashboard</h1><p className="text-sm text-body mt-1">Contract analysis overview</p></div>
          <Link to="/upload" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition shadow-sm">+ Upload New</Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((s, i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-5 shadow-theme">
              <div className="flex items-center justify-between mb-3"><span className="text-2xl">{s.icon}</span><span className="text-xs text-muted">{s.change}</span></div>
              <div className="text-2xl font-bold text-heading">{s.value}</div>
              <div className="text-xs text-muted mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {history.length === 0 && (
          <div className="bg-card border border-theme rounded-2xl p-12 shadow-theme text-center mb-8">
            <div className="text-5xl mb-4">📄</div>
            <h3 className="text-xl font-bold text-heading mb-2">No Contracts Analyzed Yet</h3>
            <p className="text-body mb-6 max-w-md mx-auto">Upload your first contract to see AI-powered clause classification, confidence scores, and risk analysis.</p>
            <Link to="/upload" className="inline-flex items-center gap-2 bg-gradient-to-r from-brand-600 to-brand-500 text-white px-8 py-3.5 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 hover:from-brand-700 hover:to-brand-600">
              📤 Upload Your First Contract
            </Link>
          </div>
        )}

        {history.length > 0 && (
          <>
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Recent Contracts */}
              <div className="lg:col-span-2 bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <h2 className="font-semibold text-heading mb-4">Recent Analysis</h2>
                <div className="space-y-2">
                  {recent.map((r, i) => (
                    <Link
                      key={i}
                      to="/results"
                      state={{ result: { clause: r.clause, confidence: r.confidence, risk_score: r.risk_score, risk_level: r.risk_level }, fileName: r.fileName }}
                      className="flex items-center justify-between p-3 rounded-xl bg-card-hover transition group"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="h-9 w-9 rounded-lg bg-subtle border border-theme flex items-center justify-center text-sm">
                          {clauseIcon(r.clause)}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-heading truncate">{r.fileName || 'Contract'}</p>
                          <p className="text-xs text-muted">{r.clause} • {r.confidence}% confidence</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-semibold text-heading">{r.risk_score}</span>
                        <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${rc(r.risk_level)}`}>{r.risk_level}</span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>

              {/* Clause Detection */}
              <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <h2 className="font-semibold text-heading mb-4">Clause Detection</h2>
                {sortedClauses.length > 0 ? (
                  <div className="space-y-4">
                    {sortedClauses.map((c, i) => (
                      <div key={i}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-body flex items-center gap-1.5">{clauseIcon(c.type)} {c.type}</span>
                          <span className="text-muted">{c.count}</span>
                        </div>
                        <div className="h-2 progress-track rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full transition-all" style={{ width: `${c.pct}%` }}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted">No clauses detected yet.</p>
                )}
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6 mt-6">
              {/* Risk Distribution */}
              <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <h2 className="font-semibold text-heading mb-4">Risk Distribution</h2>
                <div className="flex items-end gap-4 h-40">
                  {riskDistribution.map((b, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2">
                      <span className="text-xs font-semibold text-heading">{b.h}%</span>
                      <div className={`w-full rounded-lg ${b.c} transition-all`} style={{ height: `${Math.max(b.h * 1.5, 4)}px` }}></div>
                      <span className="text-xs text-muted">{b.l}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-theme grid grid-cols-3 gap-2 text-center">
                  <div><span className="text-lg font-bold text-emerald-500">{lowCount}</span><p className="text-xs text-muted">Low</p></div>
                  <div><span className="text-lg font-bold text-amber-500">{medCount}</span><p className="text-xs text-muted">Medium</p></div>
                  <div><span className="text-lg font-bold text-red-500">{highCount}</span><p className="text-xs text-muted">High</p></div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <h2 className="font-semibold text-heading mb-4">Quick Actions</h2>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { icon: '📄', label: 'Upload Contract', to: '/upload' },
                    { icon: '🔍', label: 'Search Contracts', to: '/search' },
                    { icon: '📊', label: 'Analytics', to: '/analytics' },
                    { icon: '⚙️', label: 'Settings', to: '/settings' },
                    { icon: '👥', label: 'Team Access', to: '/team' },
                    { icon: '❓', label: 'Help Center', to: '/help' },
                  ].map((a, i) => (
                    <Link key={i} to={a.to} className="flex items-center gap-3 p-3 rounded-xl bg-subtle border border-theme bg-card-hover transition">
                      <span className="text-lg">{a.icon}</span>
                      <span className="text-sm text-body font-medium">{a.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
