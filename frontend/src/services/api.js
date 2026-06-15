// Frontend API service — connected to OCR Pipeline backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = {
  async healthCheck() {
    const res = await fetch(`${API_BASE_URL}/health`)
    return res.json()
  },

  async getPipelineStatus() {
    const res = await fetch(`${API_BASE_URL}/api/pipeline/status`)
    return res.json()
  },

  async uploadContract(file) {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || err.error || 'Upload failed')
    }

    return res.json()
  },

  async uploadMultiple(files) {
    const results = []
    for (const file of files) {
      try {
        const result = await this.uploadContract(file)
        results.push({ file: file.name, ...result })
      } catch (err) {
        results.push({ file: file.name, status: 'error', error: err.message })
      }
    }
    return results
  },

  async listDocuments() {
    const res = await fetch(`${API_BASE_URL}/api/documents`)
    return res.json()
  },

  async getDocument(docId) {
    const res = await fetch(`${API_BASE_URL}/api/documents/${docId}`)
    if (!res.ok) throw new Error('Document not found')
    return res.json()
  },

  async uploadForAnalysis(file) {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE_URL}/upload-contract`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload analysis failed' }))
      throw new Error(err.detail || err.error || 'Upload analysis failed')
    }

    return res.json()
  },

  async analyzeText(contractText) {
    const res = await fetch(`${API_BASE_URL}/analyze-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contract_text: contractText }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Text analysis failed' }))
      throw new Error(err.detail || err.error || 'Text analysis failed')
    }

    return res.json()
  },

  async analyzeFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE_URL}/analyze-file`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      throw new Error('Contract analysis failed')
    }

    return res.json()
  },
}

export default api