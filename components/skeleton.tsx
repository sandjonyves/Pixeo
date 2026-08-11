export function Skeleton({ className }: { className?: string }) {
  return <div className={`skeleton ${className ?? ''}`} aria-hidden />
}

export function PageSkeleton() {
  return (
    <div className="page-skeleton">
      <Skeleton className="sk-title" />
      <div className="sk-row">
        <Skeleton className="sk-pill" />
        <Skeleton className="sk-pill" />
        <Skeleton className="sk-pill" />
      </div>
      <div className="sk-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="sk-card" />
        ))}
      </div>
    </div>
  )
}
