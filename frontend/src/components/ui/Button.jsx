import { Link } from 'react-router-dom'

const variants = {
  primary: 'bg-brand-600 hover:bg-brand-700 text-white shadow-lg shadow-brand-500/20',
  secondary: 'bg-card border border-theme text-heading hover:shadow-md',
  danger: 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20',
  ghost: 'text-body hover:text-heading hover:bg-subtle',
  outline: 'border border-brand-300 text-brand-600 hover:bg-brand-50',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs rounded-lg',
  md: 'px-5 py-2.5 text-sm rounded-xl',
  lg: 'px-8 py-3.5 text-base rounded-xl',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  to,
  href,
  disabled = false,
  loading = false,
  icon,
  className = '',
  ...props
}) {
  const baseClasses = `inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none ${variants[variant]} ${sizes[size]} ${className}`

  const content = (
    <>
      {loading ? (
        <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : icon ? (
        <span className="text-base">{icon}</span>
      ) : null}
      {children}
    </>
  )

  if (to) {
    return <Link to={to} className={baseClasses} {...props}>{content}</Link>
  }

  if (href) {
    return <a href={href} className={baseClasses} target="_blank" rel="noopener noreferrer" {...props}>{content}</a>
  }

  return (
    <button disabled={disabled || loading} className={baseClasses} {...props}>
      {content}
    </button>
  )
}
