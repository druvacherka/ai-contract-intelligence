import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

const contractsDB = {
  1: {
    name: 'NDA_Acme_Corp_2026.pdf', type: 'Non-Disclosure Agreement', parties: ['Acme Corp', 'IntelliAnalyze AI Inc.'],
    date: 'May 11, 2026', expiry: 'May 11, 2027', risk: 'Low', score: 3.2, status: 'Active', pages: 8,
    clauses: [
      { id: 1, type: 'Confidentiality', text: 'Both parties agree to maintain strict confidentiality of all shared proprietary information for a period of 5 years.', risk: 'Low' },
      { id: 2, type: 'Non-Disclosure', text: 'Neither party shall disclose trade secrets, business plans, or technical specifications to any third party.', risk: 'Low' },
      { id: 3, type: 'Termination', text: 'This agreement may be terminated by either party with 30 days written notice.', risk: 'Low' },
      { id: 4, type: 'Liability', text: 'Total liability under this agreement shall not exceed the total fees paid in the preceding 12 months.', risk: 'Medium' },
      { id: 5, type: 'Jurisdiction', text: 'This agreement shall be governed by the laws of the State of Karnataka, India.', risk: 'Low' },
    ],
    entities: ['Acme Corp', 'IntelliAnalyze AI Inc.', 'Karnataka', 'India', '$500,000', '12 months', '5 years'],
    summary: 'Standard NDA between Acme Corp and IntelliAnalyze AI covering mutual confidentiality obligations with a 5-year term.',
  },
  2: {
    name: 'Service_Agreement_v4.docx', type: 'Service Agreement', parties: ['TechVendor Ltd', 'IntelliAnalyze AI Inc.'],
    date: 'May 10, 2026', expiry: 'Nov 10, 2026', risk: 'High', score: 8.1, status: 'Review', pages: 24,
    clauses: [
      { id: 1, type: 'Indemnification', text: 'Client shall indemnify vendor against all claims, damages, and expenses arising from use of the service.', risk: 'High' },
      { id: 2, type: 'Auto-Renewal', text: 'Agreement automatically renews for successive 1-year terms unless terminated with 90 days notice.', risk: 'High' },
      { id: 3, type: 'Limitation of Liability', text: 'Vendor liability is limited to direct damages not exceeding fees paid in the last 3 months.', risk: 'High' },
      { id: 4, type: 'Data Processing', text: 'Vendor may process and store client data in any jurisdiction deemed necessary.', risk: 'Critical' },
      { id: 5, type: 'IP Assignment', text: 'All work products created during the engagement shall be owned exclusively by the vendor.', risk: 'High' },
    ],
    entities: ['TechVendor Ltd', 'IntelliAnalyze AI Inc.', '$2,000,000', '90 days', '1 year'],
    summary: 'Service agreement with several high-risk clauses including broad indemnification and unfavorable IP assignment terms.',
  },
}

export default function ContractDetail() {
  const { id } = useParams()
  const contract = contractsDB[id] || contractsDB[1]
  const [activeTab, setActiveTab] = useState('clauses')

  useEffect(() => {
    async function loadContract() {
      setLoading(true)
      setError(null)
      try {
        const doc = await api.getDocument(id)
        const mapped = {
          name: doc.filename,
          type: doc.document_type || doc.clause || 'Contract',
          parties: doc.parties || ['Unknown Party', 'IntelliAnalyze AI Inc.'],
          date: doc.metadata?.processed_at ? new Date(doc.metadata.processed_at).toLocaleDateString() : new Date().toLocaleDateString(),
          expiry: 'N/A',
          risk: doc.risk_level || 'Low',
          score: doc.risk_score ? (doc.risk_score / 10).toFixed(1) : '0.0',
          status: 'Processed',
          pages: doc.pages || 1,
          clauses: (doc.clauses || []).map((c, i) => ({
            id: i + 1,
            type: c.type,
            text: c.text,
            risk: c.risk_level
          })),
          entities: [
            ...(doc.metadata?.word_count ? [`${doc.metadata.word_count} words`] : []),
            ...(doc.metadata?.text_length ? [`${doc.metadata.text_length} characters`] : []),
            ...(doc.processing_method ? [`Processed via ${doc.processing_method}`] : []),
            ...(doc.clause ? [`Primary Clause: ${doc.clause}`] : [])
          ],
          summary: doc.summary?.join(' ') || 'No summary available.'
        }
        setContract(mapped)
      } catch (err) {
        console.warn(`Could not fetch document ${id} from API, checking local DB:`, err)
        if (contractsDB[id]) {
          setContract(contractsDB[id])
        } else {
          setContract(contractsDB[1])
        }
      } finally {
        setLoading(false)
      }
    }
    loadContract()
  }, [id])

  const riskColor = (r) => r === 'Critical' ? 'text-red-700 bg-red-50 border-red-200' : r === 'High' ? 'risk-high' : r === 'Medium' ? 'risk-med' : 'risk-low'
  const scoreColor = contract.score >= 7 ? 'text-red-600' : contract.score >= 4 ? 'text-amber-600' : 'text-emerald-600'

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/search" className="text-sm text-nav hover:text-nav-active transition">Search</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <Link to="/dashboard" className="text-sm text-brand-600 hover:text-brand-700 font-medium mb-2 inline-block">← Back to Dashboard</Link>
            <h1 className="text-2xl font-bold text-heading mb-1">{contract.name}</h1>
            <p className="text-body">{contract.type} • {contract.pages} pages</p>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${riskColor(contract.risk)}`}>{contract.risk} Risk</span>
            <span className={`text-2xl font-bold ${scoreColor}`}>{contract.score}</span>
            <span className="text-xs text-muted">/10</span>
          </div>
        </div>

        {/* Meta Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Status', value: contract.status, icon: '📋' },
            { label: 'Parties', value: contract.parties.length, icon: '👥' },
            { label: 'Clauses', value: contract.clauses.length, icon: '📑' },
            { label: 'Expiry', value: contract.expiry, icon: '📅' },
          ].map((m, i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-4 shadow-theme">
              <span className="text-lg">{m.icon}</span>
              <div className="text-lg font-bold text-heading mt-1">{m.value}</div>
              <div className="text-xs text-muted">{m.label}</div>
            </div>
          ))}
        </div>

        {/* AI Summary */}
        <div className="bg-cta border border-theme rounded-2xl p-6 mb-8">
          <h2 className="font-semibold text-heading mb-2 flex items-center gap-2">🤖 AI Summary</h2>
          <p className="text-body leading-relaxed">{contract.summary}</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-subtle rounded-xl p-1 border border-theme">
          {['clauses', 'entities', 'parties'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === tab ? 'bg-card shadow-sm text-heading' : 'text-body hover:text-heading'}`}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Clauses Tab */}
        {activeTab === 'clauses' && (
          <div className="space-y-3">
            {contract.clauses.map(c => (
              <div key={c.id} className="bg-card border border-theme rounded-2xl p-5 shadow-theme hover:shadow-lg transition">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-heading">{c.type}</h3>
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${riskColor(c.risk)}`}>{c.risk}</span>
                </div>
                <p className="text-sm text-body leading-relaxed">{c.text}</p>
              </div>
            ))}
          </div>
        )}

        {/* Entities Tab */}
        {activeTab === 'entities' && (
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h3 className="font-semibold text-heading mb-4">Extracted Entities</h3>
            <div className="flex flex-wrap gap-2">
              {contract.entities.map((e, i) => (
                <span key={i} className="px-3 py-1.5 rounded-lg bg-brand-50 border border-brand-200 text-sm text-brand-700 font-medium">{e}</span>
              ))}
            </div>
          </div>
        )}

        {/* Parties Tab */}
        {activeTab === 'parties' && (
          <div className="grid md:grid-cols-2 gap-4">
            {contract.parties.map((p, i) => (
              <div key={i} className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white font-bold text-lg mb-3">{p[0]}</div>
                <h3 className="font-semibold text-heading">{p}</h3>
                <p className="text-xs text-muted mt-1">Contracting Party {i + 1}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
