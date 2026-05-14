export default function LoadingSpinner({ size = 'md', label = 'Loading...' }) {
  const sizes = {
    sm: 'h-5 w-5 border-2',
    md: 'h-8 w-8 border-[3px]',
    lg: 'h-12 w-12 border-4',
    xl: 'h-16 w-16 border-4',
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizes[size]} rounded-full border-brand-200 border-t-brand-600 animate-spin`}
        role="status"
        aria-label={label}
      />
      {label && <p className="text-sm text-muted animate-pulse">{label}</p>}
    </div>
  )
}
