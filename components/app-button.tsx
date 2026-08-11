type AppButtonProps = {
  children: React.ReactNode
  onClick?: () => void
  secondary?: boolean
  danger?: boolean
  type?: 'button' | 'submit'
  disabled?: boolean
  loading?: boolean
  className?: string
}

export function AppButton({
  children,
  onClick,
  secondary = false,
  danger = false,
  type = 'button',
  disabled,
  loading,
  className,
}: AppButtonProps) {
  const variant = danger ? 'danger-button' : secondary ? 'outline-button' : 'primary-button'
  return (
    <button
      type={type}
      className={`${variant} ${className ?? ''} ${loading ? 'is-loading' : ''}`.trim()}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? 'Loading…' : children}
    </button>
  )
}
