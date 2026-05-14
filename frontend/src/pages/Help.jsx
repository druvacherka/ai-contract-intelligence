import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

const faqs = [
  { q: 'What file formats does ContractIQ support?', a: 'ContractIQ supports PDF, DOCX, DOC, and TXT file formats. Scanned PDFs are processed through our OCR engine (Tesseract) to extract text before analysis.' },
  { q: 'How does the AI risk scoring work?', a: 'Our NLP engine uses fine-tuned transformer models to analyze contract clauses. Each clause is scored on a 1-10 risk scale based on factors like unfavorable terms, ambiguous language, missing protections, and compliance gaps. The overall contract score is a weighted average of individual clause risks.' },
  { q: 'Is my contract data secure?', a: 'Yes. All data is encrypted at rest (AES-256) and in transit (TLS 1.3). We process documents in isolated containers and never share your data with third parties. You can delete your data at any time from Settings.' },
  { q: 'What is semantic search?', a: 'Semantic search uses AI vector embeddings to understand the meaning behind your query, not just keyword matching. This allows you to search for concepts like "penalty for late delivery" and find relevant clauses even if they use different wording.' },
  { q: 'Can I invite team members?', a: 'Yes! Navigate to the Team page to invite colleagues. You can assign roles (Viewer, Analyst, Manager, Admin) to control access levels. Team members can collaborate on contract reviews in real-time.' },
  { q: 'How long does contract analysis take?', a: 'Most contracts are analyzed in 2-5 seconds. Large documents (100+ pages) or scanned PDFs requiring OCR may take up to 30 seconds. You can track progress in real-time on the Upload page.' },
  { q: 'What clause types can ContractIQ detect?', a: 'We detect 15+ clause types including: Confidentiality, Indemnification, Termination, Non-Compete, IP Assignment, Liability Cap, Force Majeure, Data Privacy, Auto-Renewal, Governing Law, Warranty, Payment Terms, and more.' },
  { q: 'Can I export analysis results?', a: 'Yes. You can export contract analysis as PDF reports, CSV data, or JSON format from the Dashboard. Team plans include bulk export and API access for integration with your existing tools.' },
]

const guides = [
  { icon: '🚀', title: 'Getting Started', desc: 'Learn how to upload your first contract and understand the analysis results.', link: '#' },
  { icon: '🔍', title: 'Search Guide', desc: 'Master semantic search to find exactly what you need across all contracts.', link: '/search' },
  { icon: '📊', title: 'Understanding Risk Scores', desc: 'Deep dive into how risk scoring works and what each level means.', link: '/analytics' },
  { icon: '👥', title: 'Team Collaboration', desc: 'Set up your team, assign roles, and collaborate on contract reviews.', link: '/team' },
  { icon: '🔌', title: 'API Documentation', desc: 'Integrate ContractIQ with your existing workflow using our REST API.', link: '#' },
  { icon: '🛡️', title: 'Security & Compliance', desc: 'Learn about our security measures, data handling, and compliance certifications.', link: '#' },
]

export default function Help() {
  const [openFaq, setOpenFaq] = useState(null)
  const [contactForm, setContactForm] = useState({ name: '', email: '', message: '' })
  const [sent, setSent] = useState(false)

  const handleContact = (e) => {
    e.preventDefault()
    setSent(true)
    setContactForm({ name: '', email: '', message: '' })
    setTimeout(() => setSent(false), 3000)
  }

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <Link to="/help" className="text-sm text-nav-active font-semibold">Help</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-heading mb-3">Help Center</h1>
          <p className="text-body max-w-lg mx-auto">Find answers, explore guides, or reach out to our support team.</p>
        </div>

        {/* Quick Guides */}
        <div className="mb-12">
          <h2 className="text-xl font-bold text-heading mb-6">Quick Guides</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {guides.map((g, i) => (
              <Link key={i} to={g.link} className="bg-card border border-theme rounded-2xl p-5 shadow-theme hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                <span className="text-2xl block mb-3 group-hover:scale-110 transition">{g.icon}</span>
                <h3 className="font-semibold text-heading mb-1">{g.title}</h3>
                <p className="text-xs text-body leading-relaxed">{g.desc}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div className="mb-12">
          <h2 className="text-xl font-bold text-heading mb-6">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-card border border-theme rounded-2xl shadow-theme overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-5 text-left hover:bg-card-hover transition"
                >
                  <span className="font-medium text-heading text-sm pr-4">{faq.q}</span>
                  <svg className={`h-5 w-5 text-muted flex-shrink-0 transition-transform duration-200 ${openFaq === i ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {openFaq === i && (
                  <div className="px-5 pb-5 border-t border-theme pt-4">
                    <p className="text-sm text-body leading-relaxed">{faq.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Contact */}
        <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
          <h2 className="text-xl font-bold text-heading mb-2">Contact Support</h2>
          <p className="text-sm text-body mb-6">Can't find what you're looking for? Send us a message.</p>
          {sent && (
            <div className="mb-4 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-medium">✅ Message sent! We'll get back to you within 24 hours.</div>
          )}
          <form onSubmit={handleContact} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <input type="text" value={contactForm.name} onChange={e => setContactForm({...contactForm, name: e.target.value})} placeholder="Your name" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
              <input type="email" value={contactForm.email} onChange={e => setContactForm({...contactForm, email: e.target.value})} placeholder="your@email.com" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
            </div>
            <textarea value={contactForm.message} onChange={e => setContactForm({...contactForm, message: e.target.value})} placeholder="How can we help?" rows={4} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition resize-none" required />
            <button type="submit" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20">Send Message</button>
          </form>
        </div>
      </div>
    </div>
  )
}
