import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-page flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        {/* Animated 404 */}
        <div className="relative mb-8">
          <h1 className="text-[120px] font-bold text-brand-100 leading-none select-none">404</h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-6xl animate-bounce">📄</div>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-heading mb-3">Page Not Found</h2>
        <p className="text-body mb-8 leading-relaxed">
          The contract you're looking for seems to have expired or doesn't exist. Let's get you back on track.
        </p>

        <div className="flex justify-center gap-4 flex-wrap">
          <Link to="/" className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-3 rounded-xl font-semibold transition hover:scale-[1.02] shadow-lg shadow-brand-500/20">
            Go Home
          </Link>
          <Link to="/dashboard" className="bg-card border border-theme text-heading px-6 py-3 rounded-xl font-semibold transition hover:shadow-md">
            Dashboard
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-3 gap-4">
          {[
            { icon: '📤', label: 'Upload', to: '/upload' },
            { icon: '🔍', label: 'Search', to: '/search' },
            { icon: '❓', label: 'Help', to: '/help' },
          ].map((link, i) => (
            <Link key={i} to={link.to} className="bg-subtle border border-theme rounded-xl p-3 text-center hover:bg-card-hover transition group">
              <span className="text-xl block mb-1 group-hover:scale-110 transition">{link.icon}</span>
              <span className="text-xs text-body font-medium">{link.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
