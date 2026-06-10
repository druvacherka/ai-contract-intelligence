import { useState, useRef } from 'react'
import api from '../services/api'

export default function Upload() {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const inputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
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

  const processContract = async () => {
    if (files.length === 0) return

    try {
      setLoading(true)

      const response = await api.uploadContract(files[0])

      setResult(response)
    } catch (error) {
      console.error(error)
      alert('Contract analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / 1048576).toFixed(1) + ' MB'
  }

  return (
    <div className="relative min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl relative">

        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-white">
            Upload Contract
          </h1>

          <p className="mt-3 text-slate-400">
            Upload your legal contracts for AI-powered analysis.
          </p>
        </div>

        <div
          className="glass-card p-8 sm:p-12 text-center cursor-pointer"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleChange}
            className="hidden"
          />

          <h3 className="text-lg font-semibold text-white mb-2">
            {dragActive
              ? 'Drop files here'
              : 'Drag & drop your contracts'}
          </h3>

          <p className="text-sm text-slate-500 mb-4">
            or click to browse files
          </p>

          <p className="text-xs text-slate-400">
            Supported: PDF, DOCX, DOC, TXT
          </p>
        </div>

        {files.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-slate-400 mb-3">
              Selected Files ({files.length})
            </h3>

            {files.map((file, i) => (
              <div
                key={i}
                className="glass-card flex items-center justify-between p-4 mb-3"
              >
                <div>
                  <p className="text-sm font-medium text-white">
                    {file.name}
                  </p>

                  <p className="text-xs text-slate-500">
                    {formatSize(file.size)}
                  </p>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile(i)
                  }}
                  className="text-red-400"
                >
                  X
                </button>
              </div>
            ))}

            <button
              onClick={processContract}
              disabled={loading}
              className="w-full mt-4 rounded-xl bg-purple-600 px-6 py-3 text-white"
            >
              {loading
                ? 'Analyzing...'
                : 'Process Contract'}
            </button>
          </div>
        )}

        {result && (
          <div className="mt-6 glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Analysis Result
            </h3>

            <div className="space-y-3">

              <p className="text-slate-300">
                <strong>Clause:</strong> {result.clause}
              </p>

              <p className="text-slate-300">
                <strong>Confidence:</strong> {result.confidence}%
              </p>

              <p className="text-slate-300">
                <strong>Risk Score:</strong> {result.risk_score}
              </p>

              <p className="text-slate-300">
                <strong>Risk Level:</strong> {result.risk_level}
              </p>

              <div className="pt-4">
                <h4 className="text-white font-semibold mb-2">
                  Extracted Entities
                </h4>

                {result.entities &&
                result.entities.length > 0 ? (
                  <div className="space-y-2">
                    {result.entities.map(
                      (entity, index) => (
                        <div
                          key={index}
                          className="rounded-lg bg-white/5 p-2"
                        >
                          <span className="text-blue-400">
                            {entity.text}
                          </span>

                          {' '}

                          <span className="text-slate-400">
                            ({entity.label})
                          </span>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500">
                    No entities found.
                  </p>
                )}
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  )
}