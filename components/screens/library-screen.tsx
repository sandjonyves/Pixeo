'use client'

import { useMemo, useState } from 'react'
import { CalendarDays, Search, Star, Trash2 } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { ConfirmDialog } from '@/components/modal'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function LibraryScreen() {
  const { state, togglePhotoStar, deletePhotos } = useGallery()
  const { notify } = useToast()
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<string[]>([])
  const [confirmDelete, setConfirmDelete] = useState(false)

  const photos = useMemo(() => {
    const q = query.trim().toLowerCase()
    return state.photos.filter((p) => !q || p.name.toLowerCase().includes(q))
  }, [state.photos, query])

  return (
    <>
      <div className="page-heading">
        <h1>Photo Library</h1>
        <label className="library-search">
          <Search size={22} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search 'black and white portraits'"
            aria-label="Search photos"
          />
          <CalendarDays size={20} />
        </label>
      </div>

      {selected.length > 0 && (
        <div className="bulk-bar">
          <span>{selected.length} selected</span>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              selected.forEach((id) => togglePhotoStar(id))
              notify('Star status updated')
              setSelected([])
            }}
          >
            Toggle star
          </button>
          <button type="button" className="text-button" onClick={() => setConfirmDelete(true)}>
            <Trash2 size={16} /> Delete
          </button>
        </div>
      )}

      {photos.length === 0 ? (
        <EmptyState kind={query ? 'search' : 'library'} />
      ) : (
        <div className="photo-grid library-grid">
          {photos.map((photo) => {
            const isSelected = selected.includes(photo.id)
            return (
              <button
                key={photo.id}
                type="button"
                className={isSelected ? 'photo-card selected' : 'photo-card'}
                onClick={() =>
                  setSelected((current) =>
                    current.includes(photo.id)
                      ? current.filter((id) => id !== photo.id)
                      : [...current, photo.id],
                  )
                }
              >
                <img src={photo.src} alt={photo.name} />
                <span className="photo-meta">{photo.name}</span>
                <button
                  type="button"
                  className={`photo-star ${photo.starred ? 'on' : ''}`}
                  aria-label="Star photo"
                  onClick={(e) => {
                    e.stopPropagation()
                    togglePhotoStar(photo.id)
                  }}
                >
                  <Star size={14} fill={photo.starred ? 'currentColor' : 'none'} />
                </button>
              </button>
            )
          })}
        </div>
      )}

      <ConfirmDialog
        open={confirmDelete}
        title="Delete photos"
        message={`Delete ${selected.length} photo(s) from your library?`}
        confirmLabel="Delete"
        danger
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() => {
          deletePhotos(selected)
          notify('Photos deleted')
          setSelected([])
          setConfirmDelete(false)
        }}
      />
    </>
  )
}
