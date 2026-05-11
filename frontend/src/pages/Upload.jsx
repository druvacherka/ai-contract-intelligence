import { useState, useRef } from 'react'

export default function Upload() {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files))
    }
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / 1048576).toFixed(1) + ' MB'
  }

  return (
    <div className="relative min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-[10%] right-[-5%] h-[400px] w-[400px] rounded-full bg-brand-600/8 blur-[100px] animate-pulse-glow" />
      </div>

      <div className="mx-auto max-w-3xl relative">
        <div className="text-center mb-10 animate-slide-up">
          <h1 className="text-3xl sm:text-4xl font-bold text-white">
            Upload <span className="gradient-text">Contract</span>
          </h1>
          <p className="mt-3 text-slate-400">
            Upload your legal contracts for AI-powered analysis and risk scoring.
          </p>
        </div>

        {/* Upload Zone */}
        <div
          className={`glass-card p-8 sm:p-12 text-center cursor-pointer transition-all duration-300 animate-slide-up ${
            dragActive
              ? 'border-brand-500 bg-brand-500/10 scale-[1.02]'
              : 'hover:border-white/15'
          }`}
          style={{ animationDelay: '0.1s' }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleChange}
            className="hidden"
          />

          <div className={`mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl transition-all duration-300 ${
            dragActive
              ? 'bg-brand-500/20 scale-110'
              : 'bg-white/5'
          }`}>
            <svg className={`h-10 w-10 transition-colors ${dragActive ? 'text-brand-400' : 'text-slate-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
          </div>

          <h3 className="text-lg font-semibold text-white mb-2">
            {dragActive ? 'Drop files here' : 'Drag & drop your contracts'}
          </h3>
          <p className="text-sm text-slate-500 mb-4">
            or click to browse files
          </p>
          <div className="inline-flex items-center gap-2 rounded-full border border-glass-border bg-white/5 px-4 py-1.5">
            <span className="text-xs text-slate-400">Supported: PDF, DOCX, DOC, TXT</span>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-6 space-y-3 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <h3 className="text-sm font-medium text-slate-400 mb-3">
              Selected Files ({files.length})
            </h3>
            {files.map((file, i) => (
              <div key={i} className="glass-card flex items-center justify-between p-4">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-500/10">
                    <svg className="h-5 w-5 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-white truncate">{file.name}</p>
                    <p className="text-xs text-slate-500">{formatSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); removeFile(i) }}
                  className="ml-3 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 hover:text-accent-rose hover:bg-accent-rose/10 transition-colors"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

            {/* Process Button */}
            <button className="w-full mt-4 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 transition-all duration-300 hover:shadow-xl hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed" disabled>
              Process Contracts — Coming Soon
            </button>
          </div>
        )}

        {/* Info Cards */}
        <div className="mt-10 grid sm:grid-cols-3 gap-4 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          {[
            { title: 'OCR Extract', desc: 'Text extraction from scans', icon: '📄' },
            { title: 'AI Analyze', desc: 'Entity & clause detection', icon: '🤖' },
            { title: 'Risk Score', desc: 'Automated risk assessment', icon: '⚡' },
          ].map((card, i) => (
            <div key={i} className="glass-card p-4 text-center">
              <div className="text-2xl mb-2">{card.icon}</div>
              <h4 className="text-sm font-semibold text-white">{card.title}</h4>
              <p className="mt-1 text-xs text-slate-500">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
