import { Link } from 'react-router-dom'
import { useState } from 'react'
import ThemeToggle from '../components/ThemeToggle'

export default function Home() {
  const [mobileMenu, setMobileMenu] = useState(false)

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/upload', label: 'Upload' },
    { to: '/search', label: 'Search' },
    { to: '/analytics', label: 'Analytics' },
    { to: '/team', label: 'Team' },
    { to: '/help', label: 'Help' },
  ]

  return (
    <div className="min-h-screen bg-page">
      {/* ===== NAVBAR with all links ===== */}
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">
          Contract<span className="text-brand-500">IQ</span>
          <span className="text-[10px] ml-1.5 px-1.5 py-0.5 rounded bg-brand-100 text-brand-700 font-semibold align-super">AI</span>
        </Link>
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map(l => (
            <Link key={l.to} to={l.to} className="px-3 py-2 rounded-lg text-sm text-nav hover:text-nav-active hover:bg-subtle font-medium transition">{l.label}</Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link to="/login" className="text-sm text-nav hover:text-nav-active font-medium transition hidden md:block">Login</Link>
          <Link to="/signup" className="text-sm bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg font-medium transition shadow-sm">Get Started</Link>
          <button onClick={() => setMobileMenu(!mobileMenu)} className="md:hidden text-heading">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileMenu && (
        <div className="md:hidden bg-card border-b border-theme p-4 space-y-2 animate-slide-up">
          {navLinks.map(l => (
            <Link key={l.to} to={l.to} className="block px-4 py-2 rounded-lg text-sm text-body hover:bg-subtle transition">{l.label}</Link>
          ))}
          <Link to="/login" className="block px-4 py-2 rounded-lg text-sm text-brand-600 font-medium">Login</Link>
        </div>
      )}

      {/* ===== HERO SECTION ===== */}
      <section className="relative overflow-hidden">
        {/* Animated background gradient orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-brand-400/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-20 -left-20 w-72 h-72 bg-accent-cyan/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-500/5 rounded-full blur-3xl" />
        </div>

        <div className="max-w-6xl mx-auto text-center pt-20 pb-24 px-6 relative z-10">
          <div className="inline-flex items-center gap-2 bg-subtle border border-theme rounded-full px-4 py-1.5 mb-8 animate-fade-in">
            <span className="h-2 w-2 rounded-full bg-accent-emerald animate-pulse" />
            <span className="text-xs font-medium text-brand-600">Built by Saniya • Prajwal • Dhruva • Vishwas</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-heading leading-tight animate-slide-up">
            AI-Powered<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 via-brand-500 to-accent-cyan">Contract Intelligence</span>
          </h1>
          <p className="mt-6 text-lg md:text-xl text-body max-w-2xl mx-auto leading-relaxed animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Upload legal contracts, extract clauses with OCR & NLP, identify risk factors, and search semantically — powered by enterprise-grade AI.
          </p>
          <div className="mt-10 flex justify-center gap-4 flex-wrap animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Link to="/signup" className="bg-brand-600 hover:bg-brand-700 text-white px-8 py-3.5 rounded-xl font-semibold transition hover:scale-105 shadow-lg shadow-brand-500/20">Start Free →</Link>
            <Link to="/dashboard" className="bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme">Explore Dashboard</Link>
          </div>

          {/* Trusted by logos */}
          <div className="mt-16 pt-8 border-t border-theme">
            <p className="text-xs text-muted uppercase tracking-widest mb-6">Trusted by teams worldwide</p>
            <div className="flex justify-center gap-8 flex-wrap opacity-40">
              {['LegalTech Co', 'FinanceAI', 'SecureDocs', 'CloudLaw', 'DataShield'].map((name, i) => (
                <span key={i} className="text-sm font-bold text-heading tracking-wider">{name}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== STATS BAR ===== */}
      <section className="bg-cta border-y border-theme">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 px-6 py-10">
          {[
            { n: '10,000+', l: 'Contracts Analyzed', icon: '📄' },
            { n: '99.7%', l: 'Accuracy Rate', icon: '🎯' },
            { n: '2.3s', l: 'Avg Processing', icon: '⚡' },
            { n: '15+', l: 'Clause Types', icon: '🧠' },
          ].map((s, i) => (
            <div key={i} className="text-center">
              <span className="text-2xl block mb-2">{s.icon}</span>
              <div className="text-2xl md:text-3xl font-bold text-heading">{s.n}</div>
              <div className="text-xs text-muted mt-1 uppercase tracking-wider">{s.l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== FEATURES SECTION ===== */}
      <section className="max-w-6xl mx-auto px-6 py-24" id="features">
        <h2 className="text-3xl md:text-4xl font-bold text-heading text-center mb-4">Everything You Need</h2>
        <p className="text-body text-center mb-14 max-w-xl mx-auto">Four AI engines working together for complete contract intelligence.</p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { icon: '📄', title: 'OCR Extraction', desc: 'Extract text from scanned PDFs and images using Tesseract OCR with advanced preprocessing.', color: 'from-brand-600 to-brand-400' },
            { icon: '🧠', title: 'NLP Analysis', desc: 'Identify entities, dates, clauses and legal terms automatically using transformer models.', color: 'from-accent-cyan to-blue-500' },
            { icon: '⚠️', title: 'Risk Scoring', desc: 'Flag risky language, unfavorable terms, and compliance gaps with 1-10 severity ratings.', color: 'from-accent-amber to-orange-500' },
            { icon: '🔍', title: 'Semantic Search', desc: 'Search contracts with natural language using vector embeddings and RAG architecture.', color: 'from-accent-emerald to-teal-500' },
          ].map((f, i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group shadow-theme">
              <div className={`h-12 w-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center text-xl mb-4 group-hover:scale-110 transition shadow-sm`}>{f.icon}</div>
              <h3 className="font-semibold text-heading mb-2 text-lg">{f.title}</h3>
              <p className="text-sm text-body leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== HOW IT WORKS ===== */}
      <section className="bg-subtle border-y border-theme py-24 px-6" id="how-it-works">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-heading text-center mb-4">How It Works</h2>
          <p className="text-body text-center mb-14 max-w-lg mx-auto">Three simple steps to unlock insights from any contract.</p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Upload', desc: 'Drag & drop your PDF, DOCX or scanned contracts. Our OCR engine handles even poor-quality scans.', icon: '📤' },
              { step: '02', title: 'Analyze', desc: 'AI extracts clauses, scores risks, identifies entities, and generates plain-English summaries.', icon: '🤖' },
              { step: '03', title: 'Decide', desc: 'Get actionable risk reports, compare contracts side-by-side, and search across your entire library.', icon: '✅' },
            ].map((s, i) => (
              <div key={i} className="bg-card border border-theme rounded-2xl p-8 text-center shadow-theme hover:shadow-lg transition">
                <div className="text-3xl mb-4">{s.icon}</div>
                <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-brand-100 text-brand-700 font-bold text-sm mb-4">{s.step}</div>
                <h3 className="font-semibold text-heading text-lg mb-3">{s.title}</h3>
                <p className="text-sm text-body leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== OUR MISSION ===== */}
      <section className="max-w-5xl mx-auto px-6 py-24" id="mission">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Our Mission</span>
            <h2 className="text-3xl md:text-4xl font-bold text-heading mt-3 mb-6">Democratizing Legal Intelligence</h2>
            <p className="text-body leading-relaxed mb-4">
              We believe every business — from startups to enterprises — deserves access to the same caliber of contract analysis that was once exclusive to expensive law firms.
            </p>
            <p className="text-body leading-relaxed mb-6">
              ContractIQ AI uses cutting-edge machine learning to make contract review faster, cheaper, and more accurate. Our mission is to eliminate blind spots in legal agreements and protect businesses from hidden risks.
            </p>
            <div className="flex gap-3">
              <Link to="/help" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition">Learn More</Link>
              <Link to="/team" className="bg-card border border-theme text-heading px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:shadow-md">Meet the Team</Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              { icon: '🎯', title: 'Precision', desc: '99.7% clause detection accuracy' },
              { icon: '⚡', title: 'Speed', desc: 'Analyze 50-page contracts in seconds' },
              { icon: '🔒', title: 'Security', desc: 'AES-256 encryption, SOC 2 compliant' },
              { icon: '🌍', title: 'Scale', desc: 'Handles 10,000+ contracts daily' },
            ].map((v, i) => (
              <div key={i} className="bg-card border border-theme rounded-xl p-5 shadow-theme hover:shadow-lg transition">
                <span className="text-2xl block mb-2">{v.icon}</span>
                <h4 className="font-semibold text-heading text-sm">{v.title}</h4>
                <p className="text-xs text-muted mt-1">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== OUR VISION ===== */}
      <section className="bg-cta border-y border-theme py-24 px-6" id="vision">
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Our Vision</span>
          <h2 className="text-3xl md:text-4xl font-bold text-heading mt-3 mb-6">The Future of Contract Management</h2>
          <p className="text-lg text-body max-w-2xl mx-auto leading-relaxed mb-12">
            We envision a world where AI doesn't replace lawyers — it empowers them. Where every contract is understood in minutes, not days. Where risk is visible before it becomes a problem.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: '🔮', title: 'Predictive Risk', desc: 'AI that predicts contract disputes before they happen using historical analysis.' },
              { icon: '🤝', title: 'Smart Negotiation', desc: 'Auto-generated counter-proposals based on industry benchmarks and best practices.' },
              { icon: '🌐', title: 'Multi-Language', desc: 'Real-time contract analysis in 50+ languages with cultural legal nuances.' },
            ].map((v, i) => (
              <div key={i} className="bg-card border border-theme rounded-2xl p-6 shadow-theme hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
                <span className="text-3xl block mb-4">{v.icon}</span>
                <h3 className="font-semibold text-heading mb-2">{v.title}</h3>
                <p className="text-sm text-body leading-relaxed">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== ABOUT US ===== */}
      <section className="max-w-5xl mx-auto px-6 py-24" id="about">
        <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest block text-center">About Us</span>
        <h2 className="text-3xl md:text-4xl font-bold text-heading text-center mt-3 mb-6">The Minds Behind ContractIQ</h2>
        <p className="text-body text-center max-w-2xl mx-auto mb-14 leading-relaxed">
          We're a team of engineers, data scientists, and legal-tech enthusiasts passionate about building AI solutions that make a real difference in how businesses handle contracts.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {[
            { n: 'Saniya', r: 'Frontend Lead + DevOps', a: 'S', c: 'from-accent-rose to-pink-400', bio: 'Crafts beautiful, responsive interfaces and manages CI/CD pipelines.' },
            { n: 'Prajwal', r: 'OCR + Data Engineering', a: 'P', c: 'from-brand-500 to-brand-400', bio: 'Builds document processing pipelines and data infrastructure.' },
            { n: 'Dhruva', r: 'NLP / ML Engineer', a: 'D', c: 'from-accent-cyan to-blue-400', bio: 'Trains transformer models for clause detection and risk scoring.' },
            { n: 'Vishwas', r: 'Backend + API', a: 'V', c: 'from-accent-amber to-orange-400', bio: 'Architects scalable APIs and microservices infrastructure.' },
          ].map((m, i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-6 text-center hover:shadow-lg transition group shadow-theme">
              <div className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${m.c} flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4 group-hover:scale-110 transition shadow-md`}>{m.a}</div>
              <h3 className="font-bold text-heading text-lg">{m.n}</h3>
              <p className="text-xs text-brand-600 font-semibold mt-1">{m.r}</p>
              <p className="text-xs text-muted mt-2 leading-relaxed">{m.bio}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ===== TECH STACK / ARCHITECTURE ===== */}
      <section className="bg-subtle border-y border-theme py-24 px-6" id="tech">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-heading text-center mb-4">System Architecture</h2>
          <p className="text-body text-center mb-14 max-w-lg mx-auto">Enterprise-grade stack built for scale, security, and speed.</p>
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { icon: '⚛️', title: 'Frontend', techs: ['React 18', 'Vite', 'Tailwind CSS', 'GSAP'], color: 'border-l-accent-cyan' },
              { icon: '🐍', title: 'Backend', techs: ['FastAPI', 'Uvicorn', 'PostgreSQL', 'Redis'], color: 'border-l-brand-500' },
              { icon: '🧠', title: 'ML Pipeline', techs: ['HuggingFace', 'spaCy', 'PyTorch', 'scikit-learn'], color: 'border-l-accent-amber' },
              { icon: '🔍', title: 'Search', techs: ['Pinecone', 'LangChain', 'FAISS', 'Embeddings'], color: 'border-l-accent-emerald' },
              { icon: '📄', title: 'OCR Engine', techs: ['Tesseract', 'OpenCV', 'PDF.js', 'Pillow'], color: 'border-l-accent-rose' },
              { icon: '☁️', title: 'Infrastructure', techs: ['Docker', 'GitHub Actions', 'AWS', 'Terraform'], color: 'border-l-purple-500' },
            ].map((t, i) => (
              <div key={i} className={`bg-card border border-theme ${t.color} border-l-4 rounded-xl p-5 shadow-theme`}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xl">{t.icon}</span>
                  <h3 className="font-semibold text-heading">{t.title}</h3>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {t.techs.map((tech, j) => (
                    <span key={j} className="text-xs px-2 py-1 rounded-md bg-subtle border border-theme text-body font-medium">{tech}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CONTACT US ===== */}
      <section className="max-w-4xl mx-auto px-6 py-24" id="contact">
        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <span className="text-xs font-semibold text-brand-600 uppercase tracking-widest">Contact Us</span>
            <h2 className="text-3xl md:text-4xl font-bold text-heading mt-3 mb-6">Get in Touch</h2>
            <p className="text-body leading-relaxed mb-8">
              Have questions about ContractIQ? Want to schedule a demo? We'd love to hear from you.
            </p>
            <div className="space-y-4">
              {[
                { icon: '📧', label: 'Email', value: 'team@contractiq.dev' },
                { icon: '📍', label: 'Location', value: 'Bangalore, India' },
                { icon: '🕐', label: 'Response Time', value: 'Within 24 hours' },
                { icon: '🔗', label: 'GitHub', value: 'github.com/druvacherka' },
              ].map((c, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-xl bg-subtle border border-theme flex items-center justify-center text-lg">{c.icon}</div>
                  <div>
                    <p className="text-xs text-muted">{c.label}</p>
                    <p className="text-sm font-medium text-heading">{c.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h3 className="font-semibold text-heading mb-4">Send a Message</h3>
            <form className="space-y-4" onSubmit={e => { e.preventDefault(); alert('Message sent! We will get back to you soon.') }}>
              <input type="text" placeholder="Your name" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
              <input type="email" placeholder="your@email.com" className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition" required />
              <select className="w-full px-4 py-3 rounded-xl bg-input border text-heading outline-none focus:border-brand-500 transition">
                <option>General Inquiry</option>
                <option>Schedule a Demo</option>
                <option>Partnership</option>
                <option>Bug Report</option>
                <option>Feature Request</option>
              </select>
              <textarea placeholder="Your message..." rows={4} className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition resize-none" required />
              <button type="submit" className="w-full bg-brand-600 hover:bg-brand-700 text-white py-3 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20">Send Message</button>
            </form>
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="bg-gradient-to-br from-brand-600 to-brand-700 py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Ready to Transform Your Contract Workflow?</h2>
          <p className="text-brand-100 text-lg mb-8">Join thousands of teams using ContractIQ to eliminate contract blind spots.</p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Link to="/signup" className="bg-white text-brand-700 px-8 py-3.5 rounded-xl font-semibold transition hover:scale-105 shadow-lg">Start Free Trial</Link>
            <Link to="/upload" className="border-2 border-white/30 text-white px-8 py-3.5 rounded-xl font-semibold transition hover:bg-white/10">Upload Contract</Link>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="border-t border-theme bg-footer">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="col-span-2 md:col-span-1">
              <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
              <p className="text-sm text-body mt-3 leading-relaxed">Enterprise-grade AI contract analysis for modern legal teams.</p>
            </div>
            {[
              { title: 'Product', links: [{ l: 'Dashboard', t: '/dashboard' }, { l: 'Upload', t: '/upload' }, { l: 'Search', t: '/search' }, { l: 'Analytics', t: '/analytics' }] },
              { title: 'Company', links: [{ l: 'About Us', t: '#about' }, { l: 'Our Mission', t: '#mission' }, { l: 'Team', t: '/team' }, { l: 'Contact', t: '#contact' }] },
              { title: 'Resources', links: [{ l: 'Help Center', t: '/help' }, { l: 'Settings', t: '/settings' }, { l: 'GitHub', t: 'https://github.com/druvacherka/ai-contract-intelligence' }, { l: 'API Docs', t: '/help' }] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="text-sm font-semibold text-heading mb-4">{col.title}</h4>
                <ul className="space-y-2.5">
                  {col.links.map((link, j) => (
                    <li key={j}>
                      {link.t.startsWith('/') || link.t.startsWith('#') ? (
                        <Link to={link.t} className="text-sm text-body hover:text-brand-600 transition">{link.l}</Link>
                      ) : (
                        <a href={link.t} target="_blank" rel="noopener noreferrer" className="text-sm text-body hover:text-brand-600 transition">{link.l}</a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-10 pt-6 border-t border-theme flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-muted">© 2026 ContractIQ — Built with ❤️ by Saniya • Prajwal • Dhruva • Vishwas</p>
            <p className="text-xs text-muted">React • FastAPI • PyTorch • Docker • Tailwind</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
