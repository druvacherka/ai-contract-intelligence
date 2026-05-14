import { useEffect } from 'react'

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      const handleEsc = (e) => { if (e.key === 'Escape') onClose() }
      window.addEventListener('keydown', handleEsc)
      return () => { window.removeEventListener('keydown', handleEsc); document.body.style.overflow = '' }
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizes = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl', full: 'max-w-[90vw]' }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fade-in" onClick={onClose} />
      <div className={`relative ${sizes[size]} w-full bg-card border border-theme rounded-2xl shadow-2xl transform transition-all duration-300 animate-scale-in`}>
        {title && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-theme">
            <h2 className="text-lg font-semibold text-heading">{title}</h2>
            <button onClick={onClose} className="h-8 w-8 rounded-lg flex items-center justify-center text-muted hover:text-heading hover:bg-subtle transition">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}
