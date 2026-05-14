import { useState, useEffect, useCallback, createContext, useContext } from 'react'

const ToastContext = createContext()

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type, duration }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[999] flex flex-col gap-3 max-w-sm">
        {toasts.map(toast => (
          <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)

function ToastItem({ toast, onClose }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    requestAnimationFrame(() => setIsVisible(true))
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(onClose, 300)
    }, toast.duration)
    return () => clearTimeout(timer)
  }, [toast.duration, onClose])

  const typeStyles = {
    success: 'border-l-4 border-l-accent-emerald bg-emerald-50 dark:bg-emerald-900/20',
    error: 'border-l-4 border-l-accent-rose bg-red-50 dark:bg-red-900/20',
    warning: 'border-l-4 border-l-accent-amber bg-amber-50 dark:bg-amber-900/20',
    info: 'border-l-4 border-l-brand-500 bg-brand-50 dark:bg-brand-900/20',
  }

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  }

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl shadow-lg border border-theme backdrop-blur-sm transition-all duration-300 ${typeStyles[toast.type]} ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <span className="text-lg flex-shrink-0 mt-0.5">{icons[toast.type]}</span>
      <p className="text-sm text-heading font-medium flex-1">{toast.message}</p>
      <button
        onClick={onClose}
        className="text-muted hover:text-heading transition text-lg leading-none flex-shrink-0"
      >
        ×
      </button>
    </div>
  )
}
