'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { Star } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { useGallery } from '@/lib/gallery-context'
import { formatDateLabel } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'

export function StarredScreen() {
  const { state, getCoverSrc, toggleCollectionStar, togglePhotoStar } = useGallery()
  const { notify } = useToast()
  const [tab, setTab] = useState<'collections' | 'photos'>('collections')

  const starredCollections = useMemo(
    () => state.collections.filter((c) => c.starred),
    [state.collections],
  )
  const starredPhotos = useMemo(() => state.photos.filter((p) => p.starred), [state.photos])

  return (
    <>
      <h1>Starred</h1>
      <div className="tabs">
        <button
          type="button"
          className={tab === 'collections' ? 'active' : undefined}
          onClick={() => setTab('collections')}
        >
          Collections
        </button>
        <button
          type="button"
          className={tab === 'photos' ? 'active' : undefined}
          onClick={() => setTab('photos')}
        >
          Photos
        </button>
      </div>

      {tab === 'collections' &&
        (starredCollections.length === 0 ? (
          <EmptyState kind="collections" />
        ) : (
          <div className="collections-grid">
            {starredCollections.map((collection) => {
              const cover = getCoverSrc(collection)
              const count = collection.sets.reduce((n, s) => n + s.photoIds.length, 0)
              return (
                <article key={collection.id} className="collection-card-wrap">
                  <Link href={`/editor/${collection.id}`} className="collection-card">
                    {cover ? (
                      <img src={cover} alt={collection.name} />
                    ) : (
                      <div className="collection-cover-empty">No cover</div>
                    )}
                    <h2>{collection.name}</h2>
                    <p>
                      <i className="live" />
                      {count} items <span>•</span> {formatDateLabel(collection.eventDate)}
                    </p>
                  </Link>
                  <button
                    type="button"
                    className="starred"
                    onClick={() => {
                      toggleCollectionStar(collection.id)
                      notify('Removed from starred')
                    }}
                  >
                    <Star size={16} fill="currentColor" />
                  </button>
                </article>
              )
            })}
          </div>
        ))}

      {tab === 'photos' &&
        (starredPhotos.length === 0 ? (
          <EmptyState kind="photos" />
        ) : (
          <div className="photo-grid library-grid">
            {starredPhotos.map((photo) => (
              <div key={photo.id} className="photo-card">
                <img src={photo.src} alt={photo.name} />
                <button
                  type="button"
                  className="photo-star on"
                  onClick={() => {
                    togglePhotoStar(photo.id)
                    notify('Removed from starred')
                  }}
                >
                  <Star size={14} fill="currentColor" />
                </button>
              </div>
            ))}
          </div>
        ))}
    </>
  )
}
