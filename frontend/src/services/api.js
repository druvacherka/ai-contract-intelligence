// Frontend API service — connected to OCR Pipeline backend
import supabase from './supabase'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://intellianalyze-api.onrender.com'

async function getAuthHeaders() {
  try {
    const userStr = localStorage.getItem('IntelliAnalyze AI_user')
    if (userStr) {
      const user = JSON.parse(userStr)
      if (user?.id === 'demo-user-id') {
        return { Authorization: 'Bearer demo-token' }
      }
    }
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      return { Authorization: 'Bearer ' + session.access_token }
    }
  } catch (e) {
    console.warn('Failed to get auth session for headers:', e)
  }
  return {}
}

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

    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      headers: { ...authHeaders },
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
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/documents`, {
      headers: { ...authHeaders },
    })
    return res.json()
  },

  async getDocument(docId) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/documents/${docId}`, {
      headers: { ...authHeaders },
    })
    if (!res.ok) throw new Error('Document not found')
    return res.json()
  },

  async uploadForAnalysis(file) {
    const formData = new FormData()
    formData.append('file', file)

    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/upload-contract`, {
      method: 'POST',
      headers: { ...authHeaders },
      body: formData,
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload analysis failed' }))
      throw new Error(err.detail || err.error || 'Upload analysis failed')
    }

    return res.json()
  },

  async analyzeText(contractText) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/analyze-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
      body: JSON.stringify({ contract_text: contractText }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Text analysis failed' }))
      throw new Error(err.detail || err.error || 'Text analysis failed')
    }

    return res.json()
  },

  async getContracts() {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/contracts`, {
      headers: { ...authHeaders },
    })
    if (!res.ok) throw new Error('Failed to fetch contracts')
    return res.json()
  },

  async getContractById(id) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/contracts/${id}`, {
      headers: { ...authHeaders },
    })
    if (!res.ok) throw new Error('Contract not found')
    return res.json()
  },

  async deleteContract(id) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/contracts/${id}`, {
      method: 'DELETE',
      headers: { ...authHeaders },
    })
    if (!res.ok) throw new Error('Failed to delete contract')
    return res.json()
  },

  async searchContracts(query) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders },
      body: JSON.stringify({ query }),
    })
    if (!res.ok) throw new Error('Search failed')
    return res.json()
  },

  async downloadReport(contractId) {
    const authHeaders = await getAuthHeaders()
    const res = await fetch(`${API_BASE_URL}/api/report/${contractId}/pdf`, {
      headers: { ...authHeaders },
    })
    if (!res.ok) throw new Error('Failed to download report')
    return res.blob()
  },
}

export default api