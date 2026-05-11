import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'

export default function Upload() {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const inputRef = useRef(null)

  const handleDrag = (e) => { e.preventDefault(); setDragActive(e.type==='dragenter'||e.type==='dragover') }
  const handleDrop = (e) => { e.preventDefault(); setDragActive(false); if(e.dataTransfer.files?.length) setFiles(Array.from(e.dataTransfer.files)) }
  const handleChange = (e) => { if(e.target.files?.length) setFiles(Array.from(e.target.files)) }
  const removeFile = (i) => setFiles(files.filter((_,idx)=>idx!==i))
  const fmt = (b) => b<1024?b+' B':b<1048576?(b/1024).toFixed(1)+' KB':(b/1048576).toFixed(1)+' MB'

  return (
    <div className="min-h-screen bg-page">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">Contract<span className="text-brand-500">IQ</span></Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm text-nav hover:text-nav-active transition">Home</Link>
          <Link to="/upload" className="text-sm text-nav-active font-semibold">Upload</Link>
          <Link to="/dashboard" className="text-sm text-nav hover:text-nav-active transition">Dashboard</Link>
          <ThemeToggle />
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-12">
        <h1 className="text-2xl font-bold text-heading mb-2">Upload Contract</h1>
        <p className="text-body mb-8">Upload your legal contracts for AI-powered analysis.</p>

        <div className={`upload-zone border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all shadow-theme ${dragActive?'upload-zone-active':''}`} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} onClick={()=>inputRef.current?.click()}>
          <input ref={inputRef} type="file" multiple accept=".pdf,.docx,.doc,.txt" onChange={handleChange} className="hidden" />
          <div className="text-4xl mb-4">{dragActive?'📥':'📄'}</div>
          <h3 className="font-semibold text-heading mb-2">{dragActive?'Drop files here':'Drag & drop contracts'}</h3>
          <p className="text-sm text-muted mb-4">or click to browse</p>
          <span className="text-xs text-body bg-subtle px-3 py-1 rounded-full border border-theme">PDF, DOCX, DOC, TXT</span>
        </div>

        {files.length > 0 && (
          <div className="mt-6 space-y-2">
            {files.map((f,i) => (
              <div key={i} className="flex items-center justify-between bg-card border border-theme rounded-xl p-4 shadow-theme">
                <div className="flex items-center gap-3 min-w-0">
                  <span>📄</span>
                  <div className="min-w-0"><p className="text-sm font-medium text-heading truncate">{f.name}</p><p className="text-xs text-muted">{fmt(f.size)}</p></div>
                </div>
                <button onClick={e=>{e.stopPropagation();removeFile(i)}} className="text-muted hover:text-accent-rose transition text-lg">×</button>
              </div>
            ))}
            <button className="w-full mt-4 bg-brand-600 hover:bg-brand-700 text-white py-3 rounded-xl font-semibold transition shadow-sm disabled:opacity-50" disabled>Analyze Contracts — Coming Soon</button>
          </div>
        )}
      </div>
    </div>
  )
}
