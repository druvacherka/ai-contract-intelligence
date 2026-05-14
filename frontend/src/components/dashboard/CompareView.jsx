import { useState } from 'react'

const contractOptions = [
  { id: 1, name: 'NDA_Acme_Corp_2026.pdf', risk: 'Low', score: 3.2, clauses: 5, type: 'NDA' },
  { id: 2, name: 'Service_Agreement_v4.docx', risk: 'High', score: 8.1, clauses: 8, type: 'Service Agreement' },
  { id: 3, name: 'Lease_Contract_Q2.pdf', risk: 'Medium', score: 5.4, clauses: 6, type: 'Lease' },
  { id: 4, name: 'Employment_Offer_JD.pdf', risk: 'Medium', score: 5.7, clauses: 4, type: 'Employment' },
  { id: 5, name: 'Vendor_SLA_2026.docx', risk: 'High', score: 7.8, clauses: 7, type: 'SLA' },
]

const clauseComparison = {
  1: [
    { type: 'Confidentiality', text: 'Both parties maintain strict confidentiality for 5 years.', risk: 'Low' },
    { type: 'Termination', text: '30 days written notice required.', risk: 'Low' },
    { type: 'Liability', text: 'Capped at fees paid in preceding 12 months.', risk: 'Medium' },
  ],
  2: [
    { type: 'Indemnification', text: 'Client shall indemnify vendor against all claims and damages.', risk: 'High' },
    { type: 'Auto-Renewal', text: 'Automatically renews unless 90 days notice given.', risk: 'High' },
    { type: 'IP Assignment', text: 'All work products owned exclusively by vendor.', risk: 'High' },
  ],
  3: [
    { type: 'Sublease', text: 'Tenant cannot sublease without written consent.', risk: 'Medium' },
    { type: 'Maintenance', text: 'Tenant responsible for all interior maintenance.', risk: 'Medium' },
    { type: 'Termination', text: 'Early termination incurs 3-month penalty.', risk: 'High' },
  ],
  4: [
    { type: 'Non-Compete', text: '12-month restriction post-employment.', risk: 'Medium' },
    { type: 'IP Rights', text: 'All inventions during employment belong to employer.', risk: 'Medium' },
  ],
  5: [
    { type: 'Uptime SLA', text: '99.9% uptime guarantee with penalty clauses.', risk: 'Low' },
    { type: 'Liability', text: 'Limited to fees paid in last 3 months only.', risk: 'High' },
    { type: 'Data Processing', text: 'Vendor may store data in any jurisdiction.', risk: 'Critical' },
  ],
}

export default function CompareView() {
  const [leftId, setLeftId] = useState(1)
  const [rightId, setRightId] = useState(2)

  const left = contractOptions.find(c => c.id === leftId)
  const right = contractOptions.find(c => c.id === rightId)
  const leftClauses = clauseComparison[leftId] || []
  const rightClauses = clauseComparison[rightId] || []

  const riskColor = (r) => r === 'Critical' ? 'text-red-700 bg-red-50 border-red-200' : r === 'High' ? 'text-red-600 bg-red-50 border-red-200' : r === 'Medium' ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-emerald-600 bg-emerald-50 border-emerald-200'
  const scoreColor = (s) => s >= 7 ? 'text-red-600' : s >= 4 ? 'text-amber-600' : 'text-emerald-600'

  return (
    <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
      <h2 className="font-semibold text-heading mb-6 flex items-center gap-2">⚖️ Contract Comparison</h2>

      {/* Selectors */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <select value={leftId} onChange={e => setLeftId(Number(e.target.value))} className="px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 transition text-sm">
          {contractOptions.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={rightId} onChange={e => setRightId(Number(e.target.value))} className="px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 transition text-sm">
          {contractOptions.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {[left, right].map((c, idx) => (
          <div key={idx} className="bg-subtle border border-theme rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted font-medium">{c.type}</span>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${riskColor(c.risk)}`}>{c.risk}</span>
            </div>
            <div className="flex items-end gap-2">
              <span className={`text-3xl font-bold ${scoreColor(c.score)}`}>{c.score}</span>
              <span className="text-xs text-muted mb-1">/10 risk</span>
            </div>
            <span className="text-xs text-muted">{c.clauses} clauses analyzed</span>
          </div>
        ))}
      </div>

      {/* Clause Comparison */}
      <div className="grid grid-cols-2 gap-6">
        {[leftClauses, rightClauses].map((clauses, idx) => (
          <div key={idx} className="space-y-2">
            <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Key Clauses</h4>
            {clauses.map((c, i) => (
              <div key={i} className="p-3 rounded-xl bg-subtle border border-theme">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-heading">{c.type}</span>
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${riskColor(c.risk)}`}>{c.risk}</span>
                </div>
                <p className="text-xs text-body leading-relaxed">{c.text}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
