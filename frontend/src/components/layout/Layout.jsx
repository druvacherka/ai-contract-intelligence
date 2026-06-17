import { Outlet, Link, useLocation } from 'react-router-dom'
import ThemeToggle from '../ThemeToggle'
import Footer from './Footer'

export default function Layout() {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/upload', label: 'Upload' },
    { path: '/search', label: 'Search' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/dashboard', label: 'Dashboard' },
  ]

  return (
    <div className="min-h-screen bg-page flex flex-col">
      <nav className="flex items-center justify-between px-8 py-4 bg-nav backdrop-blur-md border-b border-theme sticky top-0 z-50">
        <Link to="/" className="text-xl font-bold text-heading">
          Intelli<span className="text-brand-500">Analyze</span>
        </Link>
        <div className="flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive(link.path)
                  ? 'text-brand-600 bg-brand-50'
                  : 'text-nav hover:text-nav-active hover:bg-subtle'
              }`}
            >
              {link.label}
            </Link>
          ))}
          <div className="ml-2 flex items-center gap-2">
            <ThemeToggle />
            <Link to="/settings" className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-400 flex items-center justify-center text-white text-xs font-bold hover:scale-110 transition">
              S
            </Link>
          </div>
        </div>
      </nav>

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  )
}
