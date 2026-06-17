import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

const mockResults = [
  { id: 1, name: 'NDA_Acme_Corp_2026.pdf', relevance: 96, snippet: 'This Non-Disclosure Agreement contains confidentiality clauses binding both parties...', risk: 'Low', date: 'May 11', clauses: 12 },
  { id: 2, name: 'Service_Agreement_v4.docx', relevance: 89, snippet: 'Service provider agrees to indemnify and hold harmless the client from any damages...', risk: 'High', date: 'May 10', clauses: 24 },
  { id: 3, name: 'Lease_Contract_Q2.pdf', relevance: 74, snippet: 'Tenant shall not sublease the premises without prior written consent of the landlord...', risk: 'Medium', date: 'May 10', clauses: 18 },
  { id: 4, name: 'Employment_Offer_JD.pdf', relevance: 68, snippet: 'Non-compete period shall extend for twelve months following termination of employment...', risk: 'Medium', date: 'May 9', clauses: 8 },
  { id: 5, name: 'Vendor_SLA_2026.docx', relevance: 55, snippet: 'Service level commitments include 99.9% uptime guarantee with penalty clauses...', risk: 'High', date: 'May 8', clauses: 15 },
]

export default function Search() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('semantic')
  const [riskFilter, setRiskFilter] = useState('all')
  const [dateFilter, setDateFilter] = useState('all')
  const [results, setResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setIsSearching(true)
    setHasSearched(true)

    // Try vector search first
    try {
      const searchData = await api.searchContracts(query)
      const vectorResults = (searchData.results || searchData || []).map(r => ({
        id: r.document_id || r.id,
        name: r.filename || r.fileName || 'Unknown',
        relevance: r.similarity_score != null ? Math.round(r.similarity_score * 100) : (r.relevance || 80),
        snippet: r.text_preview || r.snippet || r.contract_text?.slice(0, 150) || 'No preview available.',
        risk: r.risk_level || 'Low',
        date: r.processed_at ? (() => {
          const d = new Date(r.processed_at)
          const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
          return `${months[d.getMonth()]} ${d.getDate()}`
        })() : 'N/A',
        clauses: r.num_clauses || r.num_sentences || 0,
      }))

      let filtered = vectorResults
      if (riskFilter !== 'all') {
        filtered = filtered.filter(r => r.risk === riskFilter)
      }
      setResults(filtered)
      setIsSearching(false)
      return
    } catch (err) {
      console.warn('Vector search failed, falling back to client-side:', err)
    }

    // Fallback: client-side filtering
    setTimeout(() => {
      let filtered = allDocs.map(doc => {
        const filename = doc.filename || ''
        const docType = doc.document_type || ''
        const clause = doc.clause || ''
        const preview = doc.text_preview || ''
        
        const q = query.toLowerCase()

        let relevance = 0
        if (filename.toLowerCase().includes(q)) relevance += 50
        if (preview.toLowerCase().includes(q)) relevance += 30
        if (clause.toLowerCase().includes(q)) relevance += 20

        if (relevance === 0) return null

        let snippet = preview
        if (snippet) {
          const idx = snippet.toLowerCase().indexOf(q)
          if (idx !== -1) {
            const start = Math.max(0, idx - 40)
            const end = Math.min(snippet.length, idx + q.length + 60)
            snippet = snippet.slice(start, end)
            if (start > 0) snippet = '...' + snippet
            if (end < preview.length) snippet = snippet + '...'
          } else {
            snippet = snippet.slice(0, 120) + '...'
          }
        } else {
          snippet = 'No preview text available.'
        }

        const dateObj = doc.processed_at ? new Date(doc.processed_at) : new Date()
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        const formattedDate = `${monthNames[dateObj.getMonth()]} ${dateObj.getDate()}`

        return {
          id: doc.document_id,
          name: filename,
          relevance: Math.min(99, 60 + relevance),
          snippet: snippet,
          risk: doc.risk_level || 'Low',
          date: formattedDate,
          clauses: doc.num_sentences || 10,
        }
      }).filter(Boolean)

      if (filtered.length === 0) {
        filtered = mockResults.filter(r =>
          r.name.toLowerCase().includes(query.toLowerCase()) ||
          r.snippet.toLowerCase().includes(query.toLowerCase())
        )
        if (filtered.length === 0) {
          filtered = mockResults.slice(0, 3)
        }
      }

      if (riskFilter !== 'all') {
        filtered = filtered.filter(r => r.risk === riskFilter)
      }

      if (dateFilter !== 'all') {
        const now = new Date()
        const days = dateFilter === '7d' ? 7 : dateFilter === '30d' ? 30 : 90
        const cutoff = new Date(now.setDate(now.getDate() - days))
        
        filtered = filtered.filter(r => {
          if (r.id.toString().length < 5) return true // Mock results
          try {
            const itemDate = new Date(r.date)
            return itemDate >= cutoff
          } catch {
            return true
          }
        })
      }

      setResults(filtered)
      setIsSearching(false)
    }, 600)
  }

  const rc = r => r === 'High' ? 'risk-high' : r === 'Medium' ? 'risk-med' : r === 'Low' ? 'risk-low' : 'risk-none'

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/search" className="text-sm text-nav-active font-semibold">Search</Link>
          <Link to="/upload" className="text-sm text-nav hover:text-nav-active transition">Upload</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-heading mb-2">Semantic Search</h1>
        <p className="text-body mb-8">Search contracts using natural language powered by AI vector embeddings.</p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <svg className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search contracts... e.g., 'non-compete clauses with 12-month restriction'"
                className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition"
              />
            </div>
            <button type="submit" disabled={isSearching} className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3.5 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20 disabled:opacity-50">
              {isSearching ? '...' : 'Search'}
            </button>
          </div>
        </form>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-8">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted font-medium">Type:</span>
            {['semantic', 'keyword', 'clause'].map(t => (
              <button key={t} onClick={() => setSearchType(t)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${searchType === t ? 'bg-brand-600 text-white' : 'bg-subtle border border-theme text-body hover:bg-card-hover'}`}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted font-medium">Risk:</span>
            {['all', 'Low', 'Medium', 'High'].map(r => (
              <button key={r} onClick={() => setRiskFilter(r)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${riskFilter === r ? 'bg-brand-600 text-white' : 'bg-subtle border border-theme text-body hover:bg-card-hover'}`}>
                {r === 'all' ? 'All' : r}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted font-medium">Date:</span>
            {['all', '7d', '30d', '90d'].map(d => (
              <button key={d} onClick={() => setDateFilter(d)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${dateFilter === d ? 'bg-brand-600 text-white' : 'bg-subtle border border-theme text-body hover:bg-card-hover'}`}>
                {d === 'all' ? 'All Time' : d === '7d' ? 'Week' : d === '30d' ? 'Month' : '3 Months'}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        {isSearching && (
          <div className="text-center py-12">
            <div className="h-8 w-8 border-[3px] rounded-full border-brand-200 border-t-brand-600 animate-spin mx-auto mb-3" />
            <p className="text-sm text-muted">Searching with AI embeddings...</p>
          </div>
        )}

        {!isSearching && hasSearched && results.length === 0 && (
          <div className="text-center py-12 bg-card border border-theme rounded-2xl">
            <p className="text-4xl mb-3">🔍</p>
            <p className="text-heading font-semibold mb-1">No results found</p>
            <p className="text-sm text-muted">Try different keywords or broaden your filters.</p>
          </div>
        )}

        {!isSearching && results.length > 0 && (
          <div className="space-y-3">
            <p className="text-sm text-muted mb-4">{results.length} results found</p>
            {results.map(r => (
              <Link key={r.id} to={`/contract/${r.id}`} className="block bg-card border border-theme rounded-2xl p-5 shadow-theme hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-subtle border border-theme flex items-center justify-center text-lg">📄</div>
                    <div>
                      <h3 className="font-semibold text-heading">{r.name}</h3>
                      <p className="text-xs text-muted">{r.date} • {r.clauses} clauses</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-brand-600 bg-brand-50 px-2 py-1 rounded-lg border border-brand-200">{r.relevance}% match</span>
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${rc(r.risk)}`}>{r.risk}</span>
                  </div>
                </div>
                <p className="text-sm text-body leading-relaxed mt-2 pl-[52px]">...{r.snippet}</p>
              </Link>
            ))}
          </div>
        )}

        {!hasSearched && (
          <div className="text-center py-16">
            <p className="text-5xl mb-4">🔍</p>
            <h3 className="text-lg font-semibold text-heading mb-2">Search your contracts</h3>
            <p className="text-sm text-body max-w-md mx-auto">Use natural language to find specific clauses, terms, or patterns across all your uploaded contracts.</p>
          </div>
        )}
      </div>
    </div>
  )
}
