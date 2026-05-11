import { Link } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'

/* ── Typing animation hook ─────────────────── */
function useTypewriter(words, speed = 100, pause = 2000) {
  const [text, setText] = useState('')
  const [wordIndex, setWordIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    const current = words[wordIndex]
    let timeout

    if (!isDeleting && text === current) {
      timeout = setTimeout(() => setIsDeleting(true), pause)
    } else if (isDeleting && text === '') {
      setIsDeleting(false)
      setWordIndex((prev) => (prev + 1) % words.length)
    } else {
      timeout = setTimeout(() => {
        setText(current.substring(0, isDeleting ? text.length - 1 : text.length + 1))
      }, isDeleting ? speed / 2 : speed)
    }
    return () => clearTimeout(timeout)
  }, [text, isDeleting, wordIndex, words, speed, pause])

  return text
}

/* ── Animated counter hook ─────────────────── */
function useCounter(end, duration = 2000) {
  const [count, setCount] = useState(0)
  const [started, setStarted] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setStarted(true) },
      { threshold: 0.5 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!started) return
    let start = 0
    const step = end / (duration / 16)
    const timer = setInterval(() => {
      start += step
      if (start >= end) { setCount(end); clearInterval(timer) }
      else setCount(Math.floor(start))
    }, 16)
    return () => clearInterval(timer)
  }, [started, end, duration])

  return [count, ref]
}

/* ── Floating particles ────────────────────── */
function Particles() {
  const particles = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 8,
    duration: 6 + Math.random() * 10,
    size: 2 + Math.random() * 4,
    opacity: 0.1 + Math.random() * 0.3,
  }))

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full bg-brand-400"
          style={{
            left: `${p.left}%`,
            bottom: '-10px',
            width: `${p.size}px`,
            height: `${p.size}px`,
            opacity: p.opacity,
            animation: `particleFloat ${p.duration}s ${p.delay}s ease-in infinite`,
          }}
        />
      ))}
    </div>
  )
}

/* ── Animated grid background ──────────────── */
function GridBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-[0.03]">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(99,102,241,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.3) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          animation: 'gridMove 20s linear infinite',
        }}
      />
    </div>
  )
}

export default function Home() {
  const typedText = useTypewriter(
    ['Contracts', 'Clauses', 'Risk Scores', 'Legal Terms', 'Compliance'],
    80,
    1800
  )

  const [modulesCount, modulesRef] = useCounter(7, 1500)
  const [techCount, techRef] = useCounter(15, 1500)
  const [teamCount, teamRef] = useCounter(4, 1000)

  const features = [
    { title: 'OCR Extraction', desc: 'Extract text from scanned contracts using Tesseract OCR and advanced image processing.', color: 'from-brand-500 to-brand-700', glow: 'shadow-brand-500/20', icon: '📄' },
    { title: 'NLP Analysis', desc: 'AI entity recognition and clause detection powered by transformer models.', color: 'from-accent-cyan to-blue-600', glow: 'shadow-accent-cyan/20', icon: '🧠' },
    { title: 'Risk Scoring', desc: 'Automated risk assessment of legal clauses with confidence scores.', color: 'from-accent-amber to-orange-600', glow: 'shadow-accent-amber/20', icon: '⚠️' },
    { title: 'Semantic Search', desc: 'Vector-based search with natural language queries across your library.', color: 'from-accent-emerald to-teal-600', glow: 'shadow-accent-emerald/20', icon: '🔍' },
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

  const [visibleSections, setVisibleSections] = useState(new Set())

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisibleSections((prev) => new Set([...prev, entry.target.id]))
          }
        })
      },
      { threshold: 0.15 }
    )
    document.querySelectorAll('[data-animate]').forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  const isVisible = (id) => visibleSections.has(id)

  return (
    <div className="relative overflow-hidden">
      <Particles />
      <GridBackground />

      {/* ── Background Orbs ────────────────────── */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-[-20%] left-[-10%] h-[600px] w-[600px] rounded-full bg-brand-600/10 blur-[120px] animate-pulse-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-accent-cyan/8 blur-[100px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-[50%] left-[60%] h-[300px] w-[300px] rounded-full bg-accent-rose/5 blur-[90px] animate-float" />
      </div>

      {/* ══════════════════════════════════════════
          HERO SECTION
          ══════════════════════════════════════════ */}
      <section className="relative pt-28 pb-20 px-4 sm:px-6 lg:px-8 min-h-screen flex items-center">
        <div className="mx-auto max-w-7xl w-full">
          <div className="grid lg:grid-cols-2 gap-12 items-center">

            {/* Left — Text */}
            <div className="animate-slide-up">
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5 hover:bg-brand-500/20 transition-colors cursor-default">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-400"></span>
                </span>
                <span className="text-xs font-medium text-brand-300">Day 1 — Foundation Ready</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-[1.1]">
                AI-Powered
                <br />
                <span className="gradient-text">Contract</span>
                <br />
                Intelligence
              </h1>

              <div className="mt-4 h-10 flex items-center">
                <span className="text-lg sm:text-xl text-slate-400">
                  Analyze{' '}
                  <span className="text-brand-400 font-semibold">{typedText}</span>
                  <span className="animate-pulse text-brand-400">|</span>
                </span>
              </div>

              <p className="mt-4 max-w-lg text-base text-slate-500 leading-relaxed">
                Enterprise-grade NLP + OCR + Semantic Search platform designed for legal and compliance teams. Extract, analyze, and score contracts with AI precision.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  to="/upload"
                  className="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/40 hover:scale-105 overflow-hidden"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                  Upload Contract
                </Link>
                <a
                  href="https://github.com/druvacherka/ai-contract-intelligence"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl border border-glass-border bg-glass-bg px-7 py-3.5 text-sm font-semibold text-slate-300 transition-all duration-300 hover:bg-glass-bg-hover hover:text-white hover:border-white/15 hover:scale-105"
                >
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                  View Repo
                </a>
              </div>
            </div>

            {/* Right — Animated visual */}
            <div className="hidden lg:flex justify-center animate-slide-up" style={{ animationDelay: '0.3s' }}>
              <div className="relative">
                {/* Orbiting rings */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-[350px] w-[350px] rounded-full border border-brand-500/10 animate-spin" style={{ animationDuration: '20s' }}>
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-brand-400 shadow-lg shadow-brand-400/50" />
                  </div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-[280px] w-[280px] rounded-full border border-accent-cyan/10 animate-spin" style={{ animationDuration: '15s', animationDirection: 'reverse' }}>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 h-2.5 w-2.5 rounded-full bg-accent-cyan shadow-lg shadow-accent-cyan/50" />
                  </div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-[210px] w-[210px] rounded-full border border-accent-emerald/10 animate-spin" style={{ animationDuration: '12s' }}>
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 h-2 w-2 rounded-full bg-accent-emerald shadow-lg shadow-accent-emerald/50" />
                  </div>
                </div>

                {/* Center icon */}
                <div className="relative h-[350px] w-[350px] flex items-center justify-center">
                  <div className="h-28 w-28 rounded-3xl bg-gradient-to-br from-brand-600 via-brand-500 to-accent-cyan flex items-center justify-center shadow-2xl shadow-brand-500/30 animate-float">
                    <svg className="h-14 w-14 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>

                {/* Floating badges */}
                <div className="absolute top-8 right-0 glass-card px-3 py-2 animate-float" style={{ animationDelay: '1s' }}>
                  <span className="text-xs font-semibold text-accent-emerald">✓ OCR Complete</span>
                </div>
                <div className="absolute bottom-12 left-0 glass-card px-3 py-2 animate-float" style={{ animationDelay: '2s' }}>
                  <span className="text-xs font-semibold text-accent-amber">⚡ Risk: Low</span>
                </div>
                <div className="absolute top-1/2 right-[-20px] glass-card px-3 py-2 animate-float" style={{ animationDelay: '0.5s' }}>
                  <span className="text-xs font-semibold text-brand-300">🔍 3 Matches</span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Stats Bar ───────────────────────── */}
          <div className="mt-20 animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <div className="glass-card mx-auto max-w-3xl px-6 py-5">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                <div className="text-center" ref={modulesRef}>
                  <div className="text-2xl font-bold text-white">{modulesCount}+</div>
                  <div className="mt-1 text-xs font-medium text-slate-500 uppercase tracking-wider">Modules</div>
                </div>
                <div className="text-center" ref={techRef}>
                  <div className="text-2xl font-bold text-white">{techCount}+</div>
                  <div className="mt-1 text-xs font-medium text-slate-500 uppercase tracking-wider">Tech Stack</div>
                </div>
                <div className="text-center" ref={teamRef}>
                  <div className="text-2xl font-bold text-white">{teamCount}</div>
                  <div className="mt-1 text-xs font-medium text-slate-500 uppercase tracking-wider">Team Members</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">Enterprise</div>
                  <div className="mt-1 text-xs font-medium text-slate-500 uppercase tracking-wider">Architecture</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          FEATURES SECTION
          ══════════════════════════════════════════ */}
      <section id="features" data-animate className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className={`text-center mb-16 transition-all duration-700 ${isVisible('features') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Core <span className="gradient-text">Capabilities</span></h2>
            <p className="mt-4 text-slate-400 max-w-xl mx-auto">Four powerful AI engines working together for comprehensive contract intelligence.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <div
                key={i}
                className={`glass-card p-6 group transition-all duration-700 ${isVisible('features') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
                style={{ transitionDelay: `${i * 100}ms` }}
              >
                <div className={`inline-flex items-center justify-center h-12 w-12 rounded-xl bg-gradient-to-br ${f.color} shadow-lg ${f.glow} text-white mb-4 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3`}>
                  <span className="text-xl">{f.icon}</span>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          ARCHITECTURE SECTION
          ══════════════════════════════════════════ */}
      <section id="arch" data-animate className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className={`text-center mb-16 transition-all duration-700 ${isVisible('arch') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">System <span className="gradient-text">Architecture</span></h2>
          </div>
          <div className={`glass-card p-8 sm:p-12 max-w-4xl mx-auto transition-all duration-700 ${isVisible('arch') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="grid gap-2 font-mono text-sm">
              {arch.map((item, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-4 rounded-lg px-4 py-2.5 hover:bg-white/5 transition-all duration-500 ${isVisible('arch') ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8'}`}
                  style={{ transitionDelay: `${i * 80}ms` }}
                >
                  <span className="text-slate-600">├──</span>
                  <span className={`font-semibold ${item.c}`}>{item.name}</span>
                  <span className="text-slate-600 text-xs hidden sm:inline">// {item.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          TEAM SECTION
          ══════════════════════════════════════════ */}
      <section id="team" data-animate className="relative py-24 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className={`text-center mb-16 transition-all duration-700 ${isVisible('team') ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Our <span className="gradient-text">Team</span></h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {team.map((m, i) => (
              <div
                key={i}
                className={`glass-card p-6 text-center group transition-all duration-700 ${isVisible('team') ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-10 scale-95'}`}
                style={{ transitionDelay: `${i * 100}ms` }}
              >
                <div className={`inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br ${m.color} text-white text-xl font-bold mb-4 shadow-lg transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 group-hover:shadow-xl`}>
                  {m.avatar}
                </div>
                <h3 className="text-base font-semibold text-white">{m.name}</h3>
                <p className="mt-1 text-xs text-slate-500">{m.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────── */}
      <footer className="border-t border-glass-border py-12 px-4">
        <div className="mx-auto max-w-7xl text-center">
          <p className="text-sm text-slate-600">© 2026 AI Contract Intelligence</p>
          <p className="mt-2 text-xs text-slate-700">React • FastAPI • PyTorch • Pinecone • Docker</p>
        </div>
      </footer>
    </div>
  )
}
