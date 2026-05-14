export default function Card({ children, className = '', hover = false, padding = 'p-6', onClick }) {
  return (
    <div
      className={`bg-card border border-theme rounded-2xl shadow-theme ${padding} ${
        hover ? 'hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return <div className={`mb-4 ${className}`}>{children}</div>
}

export function CardTitle({ children, className = '' }) {
  return <h3 className={`font-semibold text-heading ${className}`}>{children}</h3>
}

export function CardDescription({ children, className = '' }) {
  return <p className={`text-sm text-body mt-1 ${className}`}>{children}</p>
}

export function CardContent({ children, className = '' }) {
  return <div className={className}>{children}</div>
}

export function CardFooter({ children, className = '' }) {
  return <div className={`mt-4 pt-4 border-t border-theme flex items-center gap-3 ${className}`}>{children}</div>
}
