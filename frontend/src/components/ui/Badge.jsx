const badgeVariants = {
  low: 'text-emerald-700 bg-emerald-50 border-emerald-200 dark:text-emerald-400 dark:bg-emerald-900/20 dark:border-emerald-800',
  medium: 'text-amber-700 bg-amber-50 border-amber-200 dark:text-amber-400 dark:bg-amber-900/20 dark:border-amber-800',
  high: 'text-red-700 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800',
  critical: 'text-red-900 bg-red-100 border-red-300 dark:text-red-300 dark:bg-red-900/30 dark:border-red-700',
  info: 'text-brand-700 bg-brand-50 border-brand-200 dark:text-brand-400 dark:bg-brand-900/20 dark:border-brand-800',
  success: 'text-emerald-700 bg-emerald-50 border-emerald-200 dark:text-emerald-400 dark:bg-emerald-900/20 dark:border-emerald-800',
  neutral: 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-900/20 dark:border-gray-700',
}

const badgeSizes = {
  sm: 'px-2 py-0.5 text-[10px]',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1.5 text-sm',
}

export default function Badge({ children, variant = 'info', size = 'md', dot = false, className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1.5 font-medium border rounded-full ${badgeVariants[variant]} ${badgeSizes[size]} ${className}`}>
      {dot && (
        <span className={`h-1.5 w-1.5 rounded-full ${
          variant === 'low' || variant === 'success' ? 'bg-emerald-500' :
          variant === 'medium' ? 'bg-amber-500' :
          variant === 'high' || variant === 'critical' ? 'bg-red-500' :
          variant === 'info' ? 'bg-brand-500' : 'bg-gray-400'
        }`} />
      )}
      {children}
    </span>
  )
}
