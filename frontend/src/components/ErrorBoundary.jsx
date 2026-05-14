import { Component } from 'react'
import { Link } from 'react-router-dom'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-page flex items-center justify-center px-6">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-6">⚠️</div>
            <h1 className="text-2xl font-bold text-heading mb-3">Something Went Wrong</h1>
            <p className="text-body mb-6 leading-relaxed">
              An unexpected error occurred. Our team has been notified and is working on a fix.
            </p>
            <div className="bg-card border border-theme rounded-xl p-4 mb-6 text-left">
              <p className="text-xs text-muted font-mono break-all">
                {this.state.error?.message || 'Unknown error'}
              </p>
            </div>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload() }}
                className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 rounded-xl font-semibold transition"
              >
                Try Again
              </button>
              <Link to="/" className="bg-card border border-theme text-heading px-6 py-3 rounded-xl font-semibold transition hover:shadow-md">
                Go Home
              </Link>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
