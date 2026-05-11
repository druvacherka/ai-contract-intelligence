// Frontend API service — placeholder
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = {
  async healthCheck() {
    const res = await fetch(`${API_BASE_URL}/health`)
    return res.json()
  },

  async uploadContract(file) {
    // TODO: Implement contract upload
    throw new Error('Upload not yet implemented')
  },
}

export default api
