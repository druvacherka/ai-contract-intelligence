import { useNotification } from '../context/NotificationContext'

const typeStyles = {
  success: { background: '#10b981', icon: '✓' },
  error: { background: '#ef4444', icon: '✕' },
  warning: { background: '#f59e0b', icon: '⚠' },
  info: { background: '#6366f1', icon: 'ℹ' },
}

export default function ToastContainer() {
  const { toasts, removeToast } = useNotification()

  if (!toasts.length) return null

  return (
    <div style={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem',
      maxWidth: '380px',
    }}>
      {toasts.map(toast => {
        const style = typeStyles[toast.type] || typeStyles.info
        return (
          <div
            key={toast.id}
            onClick={() => removeToast(toast.id)}
            style={{
              background: style.background,
              color: 'white',
              padding: '0.75rem 1rem',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.9rem',
              animation: 'slideIn 0.3s ease',
            }}
          >
            <span style={{ fontSize: '1.1rem' }}>{style.icon}</span>
            <span>{toast.message}</span>
          </div>
        )
      })}
    </div>
  )
}
