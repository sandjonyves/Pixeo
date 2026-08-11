'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ChevronDown, Search, Star } from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { ConfirmDialog, Modal } from '@/components/modal'
import { EmptyState } from '@/components/empty-state'
import { useGallery } from '@/lib/gallery-context'
import { formatDateLabel } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'
import type { CollectionStatus } from '@/lib/types'

const STATUS_OPTIONS: CollectionStatus[] = ['published', 'pre-release', 'hidden', 'draft']

export function CollectionsScreen() {
  const router = useRouter()
  const { notify } = useToast()
  const { state, createCollection, getCoverSrc, deleteCollection, toggleCollectionStar } =
    useGallery()
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<CollectionStatus | null>(null)
  const [starredOnly, setStarredOnly] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [name, setName] = useState('')
  const [eventDate, setEventDate] = useState('')
  const [creating, setCreating] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const collections = useMemo(() => {
    return state.collections.filter((c) => {
      if (query && !c.name.toLowerCase().includes(query.toLowerCase())) return false
      if (statusFilter && c.status !== statusFilter) return false
      if (starredOnly && !c.starred) return false
      return true
    })
  }, [state.collections, query, statusFilter, starredOnly])

  const submitCreate = async () => {
    if (!name.trim()) {
      notify('Collection name is required.', 'error')
      return
    }
    setCreating(true)
    await new Promise((r) => setTimeout(r, 350))
    const collection = createCollection({ name, eventDate: eventDate || undefined })
    setCreating(false)
    setCreateOpen(false)
    setName('')
    setEventDate('')
    notify('Collection created')
    router.push(`/editor/${collection.id}`)
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Collections</h1>
          <label className="inline-search">
            <Search size={22} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search"
              aria-label="Search collections"
            />
          </label>
        </div>
        <div>
          <button
            type="button"
            className="text-button"
            onClick={() => notify('Presets let you reuse design styles on new collections.', 'info')}
          >
            View Presets
          </button>
          <AppButton onClick={() => setCreateOpen(true)}>
            New Collection <ChevronDown size={16} />
          </AppButton>
        </div>
      </div>

      <div className="filter-row">
        {[
          { key: 'Status', action: () => setFilter(filter === 'Status' ? null : 'Status') },
          {
            key: 'Category Tag',
            action: () => notify('Create category tags in Settings → Preferences.', 'info'),
          },
          {
            key: 'Event Date',
            action: () => notify('Sort by event date is available in collection settings.', 'info'),
          },
          {
            key: 'Expiry Date',
            action: () => notify('Set expiry dates inside each collection settings.', 'info'),
          },
          {
            key: 'Starred',
            action: () => {
              setStarredOnly((v) => !v)
              setFilter(null)
            },
          },
        ].map(({ key, action }) => (
          <button
            key={key}
            type="button"
            className={`filter-pill ${(key === 'Starred' && starredOnly) || filter === key ? 'active' : ''}`}
            onClick={action}
          >
            {key}
            <ChevronDown size={14} />
          </button>
        ))}
      </div>

      {filter === 'Status' && (
        <div className="filter-menu">
          <button
            type="button"
            onClick={() => {
              setStatusFilter(null)
              setFilter(null)
            }}
          >
            All statuses
          </button>
          {STATUS_OPTIONS.map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => {
                setStatusFilter(status)
                setFilter(null)
              }}
            >
              {status}
            </button>
          ))}
        </div>
      )}

      {collections.length === 0 ? (
        query || statusFilter || starredOnly ? (
          <EmptyState kind="search" />
        ) : (
          <div className="empty-state">
            <div className="empty-art">
              <Search size={58} strokeWidth={1} />
            </div>
            <h2>Create your first collection</h2>
            <p>Collections are client-ready galleries you can customize and share.</p>
            <AppButton onClick={() => setCreateOpen(true)}>New Collection</AppButton>
          </div>
        )
      ) : (
        <div className="collections-grid">
          {collections.map((collection) => {
            const cover = getCoverSrc(collection)
            const count = collection.sets.reduce((n, s) => n + s.photoIds.length, 0)
            return (
              <article key={collection.id} className="collection-card-wrap">
                <Link href={`/editor/${collection.id}`} className="collection-card">
                  {cover ? (
                    <img src={cover} alt={`${collection.name} collection`} />
                  ) : (
                    <div className="collection-cover-empty">No cover</div>
                  )}
                  <h2>{collection.name}</h2>
                  <p>
                    <i className={collection.status === 'published' ? 'live' : 'muted'} />
                    {count} items <span>•</span> {formatDateLabel(collection.eventDate)}
                  </p>
                </Link>
                <div className="card-actions">
                  <button
                    type="button"
                    aria-label="Star collection"
                    className={collection.starred ? 'starred' : ''}
                    onClick={() => {
                      toggleCollectionStar(collection.id)
                      notify(collection.starred ? 'Removed from starred' : 'Collection starred')
                    }}
                  >
                    <Star size={16} fill={collection.starred ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setDeleteId(collection.id)}
                    className="text-button"
                  >
                    Delete
                  </button>
                </div>
              </article>
            )
          })}
        </div>
      )}

      <Modal open={createOpen} title="NEW COLLECTION" onClose={() => setCreateOpen(false)}>
        <div className="form-fields">
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Yves" />
          </label>
          <label>
            Event date
            <input
              type="date"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setCreateOpen(false)}>
            Cancel
          </button>
          <AppButton loading={creating} onClick={submitCreate}>
            Create
          </AppButton>
        </div>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete collection"
        message="This removes the collection. Photos remain in your library."
        confirmLabel="Delete"
        danger
        onCancel={() => setDeleteId(null)}
        onConfirm={() => {
          if (deleteId) {
            deleteCollection(deleteId)
            notify('Collection deleted')
          }
          setDeleteId(null)
        }}
      />
    </>
  )
}
