import { Link } from 'react-router-dom'

export default function Home() {
  const features = [
    { title: 'OCR Extraction', desc: 'Extract text from scanned contracts using Tesseract OCR.', color: 'from-brand-500 to-brand-700', glow: 'shadow-brand-500/20' },
    { title: 'NLP Analysis', desc: 'AI entity recognition and clause detection with transformers.', color: 'from-accent-cyan to-blue-600', glow: 'shadow-accent-cyan/20' },
    { title: 'Risk Scoring', desc: 'Automated risk assessment of legal clauses and terms.', color: 'from-accent-amber to-orange-600', glow: 'shadow-accent-amber/20' },
    { title: 'Semantic Search', desc: 'Vector-based search with natural language queries.', color: 'from-accent-emerald to-teal-600', glow: 'shadow-accent-emerald/20' },
  ]

  const team = [
    { name: 'Saniya', role: 'Frontend + DevOps', avatar: 'S', color: 'from-accent-rose to-pink-600' },
    { name: 'Prajwal', role: 'OCR + Data', avatar: 'P', color: 'from-brand-500 to-brand-700' },
    { name: 'Dhruva', role: 'NLP / ML', avatar: 'D', color: 'from-accent-cyan to-blue-600' },
    { name: 'Vishwas Chandra', role: 'Backend / API', avatar: 'V', color: 'from-accent-amber to-orange-600' },
  ]

  const arch = [
    { name: 'frontend/', desc: 'React + Vite + Tailwind', c: 'text-accent-cyan' },
    { name: 'backend/', desc: 'FastAPI + Uvicorn + Celery', c: 'text-brand-400' },
    { name: 'ocr_engine/', desc: 'Tesseract + OpenCV', c: 'text-accent-emerald' },
    { name: 'nlp_engine/', desc: 'HuggingFace + spaCy', c: 'text-accent-amber' },
    { name: 'vector_search/', desc: 'Pinecone + LangChain', c: 'text-accent-rose' },
    { name: 'infra/', desc: 'Docker + AWS + Terraform', c: 'text-purple-400' },
  ]

  return (
    <div className="relative overflow-hidden">
      {/* Background Effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-[-20%] left-[-10%] h-[600px] w-[600px] rounded-full bg-brand-600/10 blur-[120px] animate-pulse-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-accent-cyan/8 blur-[100px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
      </div>

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl text-center animate-slide-up">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-400"></span>
            </span>
            <span className="text-xs font-medium text-brand-300">Day 1 — Foundation Ready</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight text-white leading-tight">
            AI Contract<br /><span className="gradient-text">Intelligence</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400 leading-relaxed">
            Enterprise-grade NLP + OCR + Semantic Search platform for legal and compliance teams.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/upload" className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 transition-all duration-300 hover:shadow-xl hover:scale-105">
              Upload Contract
            </Link>
            <a href="https://github.com/druvacherka/ai-contract-intelligence" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-xl border border-glass-border bg-glass-bg px-8 py-3.5 text-sm font-semibold text-slate-300 transition-all duration-300 hover:bg-glass-bg-hover hover:text-white">
              View Repository
            </a>
          </div>

          {/* Stats */}
          <div className="mt-20 glass-card mx-auto max-w-3xl px-6 py-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              {[['7+', 'Modules'], ['15+', 'Tech Stack'], ['4', 'Team Members'], ['Enterprise', 'Architecture']].map(([v, l], i) => (
                <div key={i} className="text-center">
                  <div className="text-2xl font-bold text-white">{v}</div>
                  <div className="mt-1 text-xs font-medium text-slate-500 uppercase tracking-wider">{l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Core <span className="gradient-text">Capabilities</span></h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <div key={i} className="glass-card p-6 group animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className={`inline-flex items-center justify-center h-12 w-12 rounded-xl bg-gradient-to-br ${f.color} shadow-lg ${f.glow} text-white mb-4 transition-transform duration-300 group-hover:scale-110`}>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white">System <span className="gradient-text">Architecture</span></h2>
          </div>
          <div className="glass-card p-8 sm:p-12 max-w-4xl mx-auto">
            <div className="grid gap-3 font-mono text-sm">
              {arch.map((item, i) => (
                <div key={i} className="flex items-center gap-4 rounded-lg px-4 py-2.5 hover:bg-white/5 transition-colors">
                  <span className="text-slate-600">├──</span>
                  <span className={`font-semibold ${item.c}`}>{item.name}</span>
                  <span className="text-slate-600 text-xs hidden sm:inline">// {item.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Our <span className="gradient-text">Team</span></h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {team.map((m, i) => (
              <div key={i} className="glass-card p-6 text-center group">
                <div className={`inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br ${m.color} text-white text-xl font-bold mb-4 shadow-lg transition-transform duration-300 group-hover:scale-110`}>
                  {m.avatar}
                </div>
                <h3 className="text-base font-semibold text-white">{m.name}</h3>
                <p className="mt-1 text-xs text-slate-500">{m.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-glass-border py-12 px-4">
        <div className="mx-auto max-w-7xl text-center">
          <p className="text-sm text-slate-600">© 2026 AI Contract Intelligence</p>
          <p className="mt-2 text-xs text-slate-700">React • FastAPI • PyTorch • Pinecone • Docker</p>
        </div>
      </footer>
    </div>
  )
}
