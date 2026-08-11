'use client'

import type { Collection, CoverLayout } from '@/lib/types'

type CoverPreviewProps = {
  layout: CoverLayout
  title: string
  imageSrc?: string
  focal?: { x: number; y: number }
  compact?: boolean
  className?: string
}

export function CoverPreview({
  layout,
  title,
  imageSrc,
  focal = { x: 50, y: 50 },
  compact,
  className,
}: CoverPreviewProps) {
  const pos = `${focal.x}% ${focal.y}%`
  const label = title || 'TITLE'

  return (
    <div
      className={`cover-preview layout-${layout} ${compact ? 'compact' : ''} ${className ?? ''}`}
    >
      {layout === 'novel' && (
        <>
          <div className="cover-novel-text">
            <span>{label}</span>
          </div>
          <div
            className="cover-novel-media"
            style={
              imageSrc
                ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
                : undefined
            }
          />
        </>
      )}

      {layout === 'stamp' && (
        <>
          <div
            className="cover-stamp-media"
            style={
              imageSrc
                ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
                : undefined
            }
          />
          <span className="cover-stamp-title">{label}</span>
        </>
      )}

      {layout === 'outline' && (
        <div
          className="cover-full"
          style={
            imageSrc
              ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
              : undefined
          }
        >
          <div className="cover-outline-box">
            <span>{label}</span>
          </div>
        </div>
      )}

      {layout === 'vintage' && (
        <div className="cover-vintage-frame">
          <div
            className="cover-full"
            style={
              imageSrc
                ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
                : undefined
            }
          >
            <span className="cover-center-title light">{label}</span>
          </div>
        </div>
      )}

      {layout === 'frame' && (
        <div
          className="cover-full"
          style={
            imageSrc
              ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
              : undefined
          }
        >
          <div className="cover-frame-caption">
            <i />
            <span>{label}</span>
          </div>
        </div>
      )}

      {layout === 'bottom-left' && (
        <div
          className="cover-full"
          style={
            imageSrc
              ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
              : undefined
          }
        >
          <span className="cover-bl-title">{label}</span>
        </div>
      )}

      {layout === 'center' && (
        <div
          className="cover-full"
          style={
            imageSrc
              ? { backgroundImage: `url(${imageSrc})`, backgroundPosition: pos }
              : undefined
          }
        >
          <span className="cover-center-title light">{label}</span>
        </div>
      )}
    </div>
  )
}

export function CoverLayoutPicker({
  collection,
  coverSrc,
  onSelect,
}: {
  collection: Collection
  coverSrc?: string
  onSelect: (layout: CoverLayout) => void
}) {
  const layouts: CoverLayout[] = [
    'center',
    'bottom-left',
    'novel',
    'stamp',
    'outline',
    'vintage',
    'frame',
  ]
  const labels: Record<CoverLayout, string> = {
    center: 'Center',
    'bottom-left': 'Bottom Left',
    novel: 'Novel',
    stamp: 'Stamp',
    outline: 'Outline',
    vintage: 'Vintage',
    frame: 'Frame',
  }

  return (
    <div className="cover-layout-list">
      {layouts.map((layout) => (
        <button
          key={layout}
          type="button"
          className={`cover-layout-option ${collection.coverLayout === layout ? 'selected' : ''}`}
          onClick={() => onSelect(layout)}
        >
          <CoverPreview
            layout={layout}
            title="TITLE"
            imageSrc={coverSrc}
            focal={collection.coverFocal}
            compact
          />
          <span className="cover-layout-label">{labels[layout]}</span>
        </button>
      ))}
    </div>
  )
}
