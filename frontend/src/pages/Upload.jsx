import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'
import api from '../services/api'

const STAGES = [
  { key: 'uploading', label: 'Uploading Document', icon: '📤' },
  { key: 'ocr', label: 'Agent 1: OCR Extraction', icon: '🔍' },
  { key: 'cleaning', label: 'Agent 2: Text Cleaning', icon: '🧹' },
  { key: 'ner', label: 'Agent 3: Entity Recognition', icon: '🏷️' },
  { key: 'clause', label: 'Agent 4: Clause Detection', icon: '📋' },
  { key: 'risk', label: 'Agent 5: Risk Analysis', icon: '⚠️' },
  { key: 'summary', label: 'Agent 6: AI Summary', icon: '🤖' },
  { key: 'compile', label: 'Agent 7: Final Compilation', icon: '✅' },
]

export default function Upload() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('upload') // 'upload' or 'paste'
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const [processing, setProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState('')
  const [results, setResults] = useState([])
  const [nlpResult, setNlpResult] = useState(null)
  const [currentFile, setCurrentFile] = useState('')
  const [progress, setProgress] = useState(0)
  const [pipelineStatus, setPipelineStatus] = useState(null)
  const [backendOnline, setBackendOnline] = useState(null)
  const [pasteText, setPasteText] = useState('')
  const [pasteProcessing, setPasteProcessing] = useState(false)
  const [pasteError, setPasteError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      const health = await api.healthCheck()
      setBackendOnline(health.status === 'healthy')
      const status = await api.getPipelineStatus()
      setPipelineStatus(status)
    } catch {
      setBackendOnline(false)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.length) {
      setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files)])
    }
  }

  const handleChange = (e) => {
    if (e.target.files?.length) {
      setFiles(prev => [...prev, ...Array.from(e.target.files)])
    }
  }

  const removeFile = (i) => setFiles(files.filter((_, idx) => idx !== i))
  const previewFile = (file) => {
    const url = URL.createObjectURL(file)
    window.open(url, '_blank')
  }
  const fmt = (b) => b < 1024 ? b + ' B' : b < 1048576 ? (b / 1024).toFixed(1) + ' KB' : (b / 1048576).toFixed(1) + ' MB'
  const ext = (name) => name.split('.').pop().toUpperCase()

  const simulateStages = async (stageKeys) => {
    for (const key of stageKeys) {
      setProcessingStage(key)
      if (key === 'uploading') addToast(`Uploading: ${file.name}`, 'info')
      if (key === 'ocr') addToast(`Agent 1: Extracting text from: ${file.name}`, 'info')
      if (key === 'clause') addToast(`Agent 4: Detecting clauses...`, 'info')
      if (key !== 'compile') {
        await new Promise(r => setTimeout(r, 650))
      }
    }
  }

  const processFiles = async () => {
    if (!files.length || processing) return
    setProcessing(true)
    setResults([])
    setNlpResult(null)
    setProgress(0)

    const allResults = []
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      setCurrentFile(file.name)
      setProgress(Math.round(((i) / files.length) * 100))

      const stagePromise = simulateStages(['uploading', 'ocr', 'cleaning', 'ner', 'clause', 'risk', 'summary'], file)

      try {
        const result = await api.uploadForAnalysis(file)
        await stagePromise
        setProcessingStage('compile')
        addToast(`Successfully analyzed: ${file.name}!`, 'success')
        allResults.push({ file: file.name, status: 'success', ...result })
        setNlpResult(result)

        // Save to localStorage for dashboard
        const history = JSON.parse(localStorage.getItem('IntelliAnalyze AI_history') || '[]')
        history.unshift({
          ...result,
          fileName: file.name,
          timestamp: new Date().toISOString(),
          id: Date.now().toString(),
        })
        if (history.length > 50) history.length = 50
        localStorage.setItem('IntelliAnalyze AI_history', JSON.stringify(history))
      } catch (err) {
        await stagePromise
        setProcessingStage('compile')
        addToast(`Failed to parse ${file.name}: ${err.message}`, 'error')
        allResults.push({ file: file.name, status: 'error', error: err.message })
      }
      setResults([...allResults])
    }

    setProgress(100)
    setCurrentFile('')
    setProcessing(false)

    // Auto-navigate to results if we have a result
    const successResults = allResults.filter(r => r.status === 'success')
    if (successResults.length > 0) {
      const lastResult = successResults[successResults.length - 1]
      const lastFileName = lastResult.file || files[files.length - 1]?.name || 'Contract'
      setFiles([])
      navigate('/results', { state: { result: lastResult, fileName: lastFileName } })
      return
    }
    setFiles([])
  }

  const handlePasteAnalysis = async () => {
    if (!pasteText.trim() || pasteProcessing) return
    setPasteProcessing(true)
    setPasteError('')

    try {
      const result = await api.analyzeText(pasteText)
      setNlpResult(result)

      const history = JSON.parse(localStorage.getItem('IntelliAnalyze AI_history') || '[]')
      history.unshift({
        ...result,
        fileName: 'Pasted Text',
        timestamp: new Date().toISOString(),
        id: Date.now().toString(),
      })
      if (history.length > 50) history.length = 50
      localStorage.setItem('IntelliAnalyze AI_history', JSON.stringify(history))

      // Navigate to results
      navigate('/results', { state: { result, fileName: 'Pasted Text' } })
    } catch (err) {
      setPasteError(err.message)
    } finally {
      setPasteProcessing(false)
    }
  }

  const getStageIndex = () => STAGES.findIndex(s => s.key === processingStage)

  const riskColor = (level) =>
    level === 'High' ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400' :
    level === 'Medium' ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-400' :
    'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400'

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading group flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-brand-600 flex items-center justify-center text-white text-sm font-black shadow-md shadow-brand-500/20">IA</div>
          <span>Intelli<span className="text-brand-500">Analyze</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav-active font-semibold">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-heading">Upload & Analyze Contracts</h1>
            <p className="text-body mt-1">Upload documents for AI-powered OCR extraction and NLP analysis.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border ${backendOnline === true ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-400' : backendOnline === false ? 'bg-red-50 text-red-600 border-red-200 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>
              <span className={`h-2 w-2 rounded-full ${backendOnline === true ? 'bg-emerald-500' : backendOnline === false ? 'bg-red-500' : 'bg-gray-400'}`}></span>
              {backendOnline === true ? 'Pipeline Online' : backendOnline === false ? 'Pipeline Offline' : 'Checking...'}
            </span>
          </div>
        </div>

        {/* Pipeline Status Bar */}
        {pipelineStatus && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            {[
              { label: 'Processed', value: pipelineStatus.processed_count, icon: '📊' },
              { label: 'OCR DPI', value: pipelineStatus.ocr_dpi, icon: '🔍' },
              { label: 'Max Size', value: pipelineStatus.max_file_size_mb + 'MB', icon: '📦' },
              { label: 'Formats', value: pipelineStatus.supported_formats?.length || 4, icon: '📄' },
            ].map((s, i) => (
              <div key={i} className="bg-card border border-theme rounded-xl p-3 shadow-theme text-center">
                <div className="text-lg mb-1">{s.icon}</div>
                <div className="text-lg font-bold text-heading">{s.value}</div>
                <div className="text-xs text-muted">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Tab Switcher */}
        <div className="flex gap-2 mb-6 p-1 bg-subtle rounded-xl border border-theme">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition ${activeTab === 'upload' ? 'tab-active' : 'tab-inactive'}`}
          >
            📄 Upload File
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition ${activeTab === 'paste' ? 'tab-active' : 'tab-inactive'}`}
          >
            📝 Paste Text
          </button>
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <>
            {/* Upload Zone */}
            <div
              className={`upload-zone border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all shadow-theme ${dragActive ? 'upload-zone-active border-brand-400 bg-brand-50/30' : 'border-theme'}`}
              onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
            >
              <input ref={inputRef} type="file" multiple accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png,.tiff,.tif,.bmp" onChange={handleChange} className="hidden" />
              <div className="text-5xl mb-4">{dragActive ? '📥' : processing ? '⚙️' : '📄'}</div>
              <h3 className="font-semibold text-heading mb-2 text-lg">{dragActive ? 'Drop files here' : processing ? `Processing: ${currentFile}` : 'Drag & drop contracts'}</h3>
              <p className="text-sm text-muted mb-4">or click to browse • PDF, DOCX, TXT, JPG, PNG supported • Handwritten documents welcome</p>
              <div className="flex items-center justify-center gap-2 flex-wrap">
                {['PDF', 'DOCX', 'TXT', 'JPG', 'PNG', 'TIFF'].map(f => (
                  <span key={f} className="text-xs px-2.5 py-1 rounded-full bg-subtle border border-theme text-body">{f}</span>
                ))}
              </div>
            </div>

            {/* Processing Stages */}
            {processing && processingStage && (
              <div className="mt-6 bg-card border border-theme rounded-2xl p-6 shadow-theme">
                <h3 className="text-sm font-semibold text-heading mb-4">Processing Pipeline</h3>
                <div className="space-y-3">
                  {STAGES.map((stage, i) => {
                    const currentIdx = getStageIndex()
                    const isDone = i < currentIdx || processingStage === 'complete'
                    const isActive = i === currentIdx && processingStage !== 'complete'

                    return (
                      <div key={stage.key} className="flex items-center gap-3">
                        <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                          isDone ? 'bg-emerald-500 text-white' :
                          isActive ? 'bg-brand-500 text-white step-active' :
                          'bg-subtle border border-theme text-muted'
                        }`}>
                          {isDone ? '✓' : isActive ? '●' : '○'}
                        </div>
                        <span className={`text-sm font-medium ${
                          isDone ? 'text-emerald-600' :
                          isActive ? 'text-brand-600 font-semibold' :
                          'text-muted'
                        }`}>
                          {stage.icon} {stage.label}{isActive ? '...' : ''}
                        </span>
                      </div>
                    )
                  })}
                </div>
                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-body font-medium">Overall Progress</span>
                    <span className="text-muted">{progress}%</span>
                  </div>
                  <div className="h-2.5 bg-subtle rounded-full overflow-hidden border border-theme">
                    <div className="h-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-full transition-all duration-500 ease-out" style={{ width: `${progress}%` }}></div>
                  </div>
                </div>

                {/* Preview while processing */}
                {files.length > 0 && (
                  <div className="flex items-center justify-between p-3 rounded-xl bg-subtle/35 border border-theme">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">📄</span>
                      <div>
                        <p className="text-xs font-bold text-heading">{currentFile}</p>
                        <p className="text-[10px] text-muted">Analysis in progress — you can preview the document while it processes</p>
                      </div>
                    </div>
                    <button
                      onClick={() => previewFile(files.find(f => f.name === currentFile) || files[0])}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white transition text-[10px] font-bold uppercase tracking-wider shadow-md shadow-brand-500/15"
                    >
                      👁️ Preview Document
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Queued Files */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-heading mb-3">Queued Files ({files.length})</h3>
                <div className="space-y-2">
                  {files.map((f, i) => (
                    <div key={i} className="flex items-center justify-between bg-card border border-theme rounded-xl p-3.5 shadow-theme">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="h-9 w-9 rounded-lg bg-subtle border border-theme flex items-center justify-center text-xs font-bold text-brand-600">{ext(f.name)}</div>
                        <div className="min-w-0"><p className="text-sm font-medium text-heading truncate">{f.name}</p><p className="text-xs text-muted">{fmt(f.size)}</p></div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={(e) => { e.stopPropagation(); previewFile(f) }}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-brand-50 border border-brand-200 text-brand-600 hover:bg-brand-100 dark:bg-brand-500/10 dark:border-brand-500/20 dark:text-brand-400 dark:hover:bg-brand-500/20 transition text-[10px] font-bold uppercase tracking-wider"
                          title="Open document in new tab"
                        >
                          👁️ Preview
                        </button>
                        <button onClick={() => removeFile(i)} className="text-muted hover:text-red-500 transition text-lg leading-none px-1">×</button>
                      </div>
                    </div>
                  ))}
                  <button
                    onClick={processFiles}
                    disabled={processing || !backendOnline}
                    className="w-full mt-3 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white py-3.5 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {processing ? (
                      <><span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Processing...</>
                    ) : (
                      <>{backendOnline ? '🚀 Analyze with AI (OCR + NLP + Risk)' : '⚠️ Backend Offline — Start server first'}</>
                    )}
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {/* Paste Text Tab */}
        {activeTab === 'paste' && (
          <div className="bg-card border border-theme rounded-2xl p-6 shadow-theme">
            <h3 className="text-sm font-semibold text-heading mb-3">Paste Contract Text</h3>
            <p className="text-xs text-muted mb-4">Paste the full contract text below for direct NLP analysis and risk scoring.</p>
            <textarea
              value={pasteText}
              onChange={e => setPasteText(e.target.value)}
              placeholder="Paste your contract text here...&#10;&#10;Example: This Agreement may be terminated by either party upon thirty (30) days written notice to the other party..."
              rows={10}
              className="w-full px-4 py-3 rounded-xl bg-input border text-heading placeholder-muted outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 transition resize-none font-mono text-sm leading-relaxed"
            />
            <div className="flex items-center justify-between mt-4">
              <span className="text-xs text-muted">{pasteText.length.toLocaleString()} characters</span>
              <button
                onClick={handlePasteAnalysis}
                disabled={!pasteText.trim() || pasteProcessing || !backendOnline}
                className="bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white px-6 py-3 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {pasteProcessing ? (
                  <><span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> Analyzing...</>
                ) : (
                  <>🧠 Analyze Text</>
                )}
              </button>
            </div>
            {pasteError && (
              <div className="mt-3 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
                ❌ {pasteError}
              </div>
            )}
          </div>
        )}

        {/* NLP Results Preview */}
        {nlpResult && !processing && (
          <div className="mt-8 animate-slide-up">
            <div className="glass-card rounded-2xl p-6 shadow-theme border border-emerald-200">
              <div className="flex items-center gap-3 mb-5">
                <div className="h-10 w-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-lg animate-check-pop">✅</div>
                <div>
                  <h3 className="font-bold text-heading">AI Analysis Complete</h3>
                  <p className="text-xs text-muted">Contract processed through OCR + NLP + Risk pipeline</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
                <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                  <div className="text-xs text-muted mb-1">Clause</div>
                  <div className="text-sm font-bold text-heading">{nlpResult.clause}</div>
                </div>
                <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                  <div className="text-xs text-muted mb-1">Confidence</div>
                  <div className="text-sm font-bold text-heading">{nlpResult.confidence}%</div>
                </div>
                <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                  <div className="text-xs text-muted mb-1">Risk Score</div>
                  <div className="text-sm font-bold text-heading">{nlpResult.risk_score}/100</div>
                </div>
                <div className="bg-subtle rounded-xl p-4 border border-theme text-center">
                  <div className="text-xs text-muted mb-1">Risk Level</div>
                  <div className={`text-xs font-bold px-2.5 py-1 rounded-full inline-block border ${riskColor(nlpResult.risk_level)}`}>{nlpResult.risk_level}</div>
                </div>
              </div>

              {/* Extracted Entities */}
              {nlpResult.entities && nlpResult.entities.length > 0 && (
                <div className="mt-6 pt-5 border-t border-theme mb-5 animate-slide-up">
                  <h4 className="font-semibold text-heading mb-3 text-xs uppercase tracking-wider flex items-center gap-1.5">
                    🏷️ Extracted Entities
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {nlpResult.entities.map((entity, index) => (
                      <div
                        key={index}
                        className="text-xs px-3 py-1.5 rounded-xl bg-subtle border border-theme text-body flex items-center gap-1.5"
                      >
                        <span className="font-semibold text-brand-600 dark:text-brand-400">
                          {entity.text}
                        </span>
                        <span className="text-[9px] font-bold text-muted bg-card px-1.5 py-0.5 rounded border border-theme uppercase">
                          {entity.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={() => navigate('/results', { state: { result: nlpResult, fileName: results[0]?.file || 'Contract' } })}
                className="w-full bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white py-3 rounded-xl font-semibold transition shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2"
              >
                🔎 View Full Analysis Results →
              </button>
            </div>
          </div>
        )}

        {/* Error Results */}
        {results.length > 0 && results.some(r => r.status === 'error') && !processing && (
          <div className="mt-6 space-y-3">
            {results.filter(r => r.status === 'error').map((r, i) => (
              <div key={i} className="flex items-center gap-3 bg-card border border-red-200 rounded-xl p-4 shadow-theme">
                <div className="h-10 w-10 rounded-xl bg-red-50 border border-red-200 flex items-center justify-center text-lg">❌</div>
                <div>
                  <p className="font-semibold text-heading">{r.file}</p>
                  <p className="text-sm text-red-500">{r.error}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}