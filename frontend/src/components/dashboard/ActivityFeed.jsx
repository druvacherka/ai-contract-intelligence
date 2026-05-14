export default function ActivityFeed() {
  const activities = [
    { id: 1, type: 'upload', user: 'Saniya', action: 'uploaded', target: 'NDA_Acme_Corp_2026.pdf', time: '2 min ago', icon: '📤', color: 'bg-brand-100 text-brand-600' },
    { id: 2, type: 'analysis', user: 'System', action: 'completed analysis of', target: 'Service_Agreement_v4.docx', time: '15 min ago', icon: '🤖', color: 'bg-cyan-100 text-cyan-600' },
    { id: 3, type: 'risk', user: 'System', action: 'flagged high-risk clause in', target: 'Vendor_SLA_2026.docx', time: '1 hr ago', icon: '⚠️', color: 'bg-red-100 text-red-600' },
    { id: 4, type: 'comment', user: 'Prajwal', action: 'commented on', target: 'Lease_Contract_Q2.pdf', time: '2 hrs ago', icon: '💬', color: 'bg-emerald-100 text-emerald-600' },
    { id: 5, type: 'invite', user: 'Saniya', action: 'invited', target: 'reviewer@lawfirm.com', time: '3 hrs ago', icon: '👥', color: 'bg-amber-100 text-amber-600' },
    { id: 6, type: 'export', user: 'Dhruva', action: 'exported risk report for', target: 'Employment_Offer_JD.pdf', time: '5 hrs ago', icon: '📥', color: 'bg-purple-100 text-purple-600' },
    { id: 7, type: 'upload', user: 'Vishwas', action: 'uploaded', target: 'Partnership_Agreement_2026.pdf', time: '1 day ago', icon: '📤', color: 'bg-brand-100 text-brand-600' },
    { id: 8, type: 'analysis', user: 'System', action: 'detected 3 critical clauses in', target: 'IP_License_Draft.docx', time: '1 day ago', icon: '🔍', color: 'bg-red-100 text-red-600' },
  ]

  return (
    <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
      <div className="flex items-center justify-between mb-5">
        <h2 className="font-semibold text-heading">Activity Feed</h2>
        <span className="text-xs text-muted">Live</span>
      </div>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-[18px] top-2 bottom-2 w-px bg-gradient-to-b from-brand-200 via-brand-100 to-transparent" />
        
        <div className="space-y-4">
          {activities.map(a => (
            <div key={a.id} className="flex items-start gap-4 relative">
              <div className={`h-9 w-9 rounded-lg ${a.color} flex items-center justify-center text-sm flex-shrink-0 z-10 shadow-sm`}>
                {a.icon}
              </div>
              <div className="flex-1 min-w-0 pt-1">
                <p className="text-sm text-body leading-relaxed">
                  <span className="font-semibold text-heading">{a.user}</span>
                  {' '}{a.action}{' '}
                  <span className="font-medium text-brand-600">{a.target}</span>
                </p>
                <p className="text-xs text-muted mt-0.5">{a.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
