import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

export default function Home() {
  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-5 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active font-medium transition">Dashboard</Link>
          <Link to="/login" className="text-sm text-nav hover:text-nav-active transition">Login</Link>
          <ThemeToggle />
          <Link to="/signup" className="text-sm bg-brand-600 hover:bg-brand-700 text-white px-5 py-2 rounded-lg font-medium transition shadow-sm">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto text-center pt-24 pb-20 px-6">
        <div className="inline-flex items-center gap-2 bg-subtle border border-theme rounded-full px-4 py-1.5 mb-8">
          <span className="h-2 w-2 rounded-full bg-accent-emerald animate-pulse"></span>
          <span className="text-xs font-medium text-brand-600">Built by Saniya • Prajwal • Dhruva • Vishwas</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-bold text-heading leading-tight">
          AI Contract<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-brand-400">Intelligence</span>
        </h1>
        <p className="mt-6 text-lg text-body max-w-2xl mx-auto leading-relaxed">
          Upload legal contracts, extract clauses with OCR & NLP, identify risk factors, and search semantically — powered by enterprise-grade AI.
        </p>
        <div className="mt-10 flex justify-center gap-4 flex-wrap">
          <Link to="/signup" className="bg-brand-600 hover:bg-brand-700 text-white px-8 py-3.5 rounded-xl font-semibold transition hover:scale-105 shadow-lg shadow-brand-500/20">Start Free →</Link>
          <Link to="/dashboard" className="bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md shadow-theme">Explore Dashboard</Link>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 px-6 pb-20">
        {[{ n:'7+', l:'Modules' },{ n:'15+', l:'Tech Stack' },{ n:'4', l:'Team Members' },{ n:'99.9%', l:'Accuracy' }].map((s,i) => (
          <div key={i} className="bg-card border border-theme rounded-2xl p-6 text-center shadow-theme">
            <div className="text-2xl font-bold text-heading">{s.n}</div>
            <div className="text-xs text-muted mt-1 uppercase tracking-wider">{s.l}</div>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <h2 className="text-3xl font-bold text-heading text-center mb-4">Everything You Need</h2>
        <p className="text-body text-center mb-14 max-w-xl mx-auto">Four AI engines working together for complete contract intelligence.</p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { icon:'📄', title:'OCR Extraction', desc:'Extract text from scanned PDFs and images using Tesseract OCR.', color:'from-brand-600 to-brand-400' },
            { icon:'🧠', title:'NLP Analysis', desc:'Identify entities, dates, clauses and legal terms automatically.', color:'from-accent-cyan to-blue-500' },
            { icon:'⚠️', title:'Risk Scoring', desc:'Flag risky language, unfavorable terms, and compliance gaps.', color:'from-accent-amber to-orange-500' },
            { icon:'🔍', title:'Semantic Search', desc:'Search contracts with natural language using vector embeddings.', color:'from-accent-emerald to-teal-500' },
          ].map((f,i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-6 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group shadow-theme bg-card-hover">
              <div className={`h-11 w-11 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center text-lg mb-4 group-hover:scale-110 transition shadow-sm`}>{f.icon}</div>
              <h3 className="font-semibold text-heading mb-2">{f.title}</h3>
              <p className="text-sm text-body leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        <h2 className="text-3xl font-bold text-heading text-center mb-14">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step:'01', title:'Upload', desc:'Drag & drop your PDF, DOCX or scanned contracts.' },
            { step:'02', title:'Analyze', desc:'AI extracts clauses, scores risks, identifies entities.' },
            { step:'03', title:'Decide', desc:'Get actionable insights and risk reports instantly.' },
          ].map((s,i) => (
            <div key={i} className="text-center">
              <div className="h-14 w-14 rounded-2xl bg-subtle border border-theme flex items-center justify-center text-brand-600 font-bold text-lg mx-auto mb-4">{s.step}</div>
              <h3 className="font-semibold text-heading text-lg mb-2">{s.title}</h3>
              <p className="text-sm text-body leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Architecture */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        <h2 className="text-3xl font-bold text-heading text-center mb-14">System Architecture</h2>
        <div className="bg-card border border-theme rounded-2xl p-8 font-mono text-sm space-y-2 shadow-theme">
          {[
            { n:'frontend/', d:'React + Vite + Tailwind', c:'text-accent-cyan' },
            { n:'backend/', d:'FastAPI + Uvicorn', c:'text-brand-600' },
            { n:'ocr_engine/', d:'Tesseract + OpenCV', c:'text-accent-emerald' },
            { n:'nlp_engine/', d:'HuggingFace + spaCy', c:'text-accent-amber' },
            { n:'vector_search/', d:'Pinecone + LangChain', c:'text-accent-rose' },
            { n:'infra/', d:'Docker + AWS + Terraform', c:'text-purple-500' },
          ].map((a,i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-2 rounded-lg bg-card-hover transition">
              <span className="text-muted">├──</span>
              <span className={`font-semibold ${a.c}`}>{a.n}</span>
              <span className="text-muted text-xs">// {a.d}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        <h2 className="text-3xl font-bold text-heading text-center mb-14">Our Team</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {[
            { n:'Saniya', r:'Frontend + DevOps', a:'S', c:'from-accent-rose to-pink-400' },
            { n:'Prajwal', r:'OCR + Data', a:'P', c:'from-brand-500 to-brand-400' },
            { n:'Dhruva', r:'NLP / ML', a:'D', c:'from-accent-cyan to-blue-400' },
            { n:'Vishwas', r:'Backend / API', a:'V', c:'from-accent-amber to-orange-400' },
          ].map((m,i) => (
            <div key={i} className="bg-card border border-theme rounded-2xl p-6 text-center hover:shadow-lg transition group shadow-theme">
              <div className={`h-14 w-14 rounded-2xl bg-gradient-to-br ${m.c} flex items-center justify-center text-white font-bold text-lg mx-auto mb-3 group-hover:scale-110 transition`}>{m.a}</div>
              <h3 className="font-semibold text-heading">{m.n}</h3>
              <p className="text-xs text-muted mt-1">{m.r}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-3xl mx-auto px-6 pb-24 text-center">
        <div className="bg-cta border border-theme rounded-3xl p-12">
          <h2 className="text-3xl font-bold text-heading mb-4">Ready to Get Started?</h2>
          <p className="text-body mb-8">Upload your first contract and experience AI-powered legal intelligence.</p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Link to="/upload" className="bg-brand-600 hover:bg-brand-700 text-white px-8 py-3.5 rounded-xl font-semibold transition hover:scale-105 shadow-lg shadow-brand-500/20">Upload Contract</Link>
            <a href="https://github.com/druvacherka/ai-contract-intelligence" target="_blank" rel="noopener noreferrer" className="bg-card border border-theme text-heading px-8 py-3.5 rounded-xl font-semibold transition hover:shadow-md">GitHub →</a>
          </div>
        </div>
      </section>

      <footer className="border-t border-theme py-8 text-center bg-footer">
        <p className="text-sm text-muted">© 2026 AI Contract Intelligence — React • FastAPI • PyTorch • Docker</p>
      </footer>
    </div>
  )
}
