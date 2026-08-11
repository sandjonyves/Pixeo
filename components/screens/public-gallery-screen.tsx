'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { ChevronLeft, ChevronRight, Heart, Download, Share2, X } from 'lucide-react'
import { useGallery } from '@/lib/gallery-context'
import { AppButton } from '@/components/app-button'
import { CoverPreview } from '@/components/editor/cover-preview'
import { Modal } from '@/components/modal'
import { formatDateLabel } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'
import type { Photo } from '@/lib/types'

export function PublicGalleryScreen({ slug }: { slug: string }) {
  const { ready, state, getCollectionPhotos, getCoverSrc, logGalleryActivity } = useGallery()
  const { notify } = useToast()
  const collection = state.collections.find((c) => c.slug === slug)
  const [unlocked, setUnlocked] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [lightbox, setLightbox] = useState<number | null>(null)
  const [liked, setLiked] = useState<Record<string, boolean>>({})
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [downloadUnlocked, setDownloadUnlocked] = useState(false)
  const [downloadPinInput, setDownloadPinInput] = useState('')
  const [downloadPrompt, setDownloadPrompt] = useState<string | null>(null)
  const [notePrompt, setNotePrompt] = useState<Photo | null>(null)
  const [noteDraft, setNoteDraft] = useState('')

  const photos = useMemo(
    () => (collection ? getCollectionPhotos(collection) : []),
    [collection, getCollectionPhotos],
  )

  useEffect(() => {
    if (!collection || collection.status === 'draft' || collection.status === 'hidden') return
    if (collection.password && !unlocked) return
    logGalleryActivity({
      collectionId: collection.id,
      type: 'view',
    })
    // only once per mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collection?.id, unlocked])

  if (!ready) return <div className="public-shell">Loading…</div>

  if (!collection || collection.status === 'draft' || collection.status === 'hidden') {
    return (
      <div className="public-shell centered">
        <h1>Gallery unavailable</h1>
        <p>This collection is not published or does not exist.</p>
        <Link href="/site" className="primary-button">
          Back to homepage
        </Link>
      </div>
    )
  }

  const needsPassword =
    (Boolean(collection.password) || collection.clientExclusive) && !unlocked

  const downloadPhoto = async (photo: Photo) => {
    try {
      const res = await fetch(photo.src)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = photo.name
      a.click()
      URL.revokeObjectURL(url)
      logGalleryActivity({
        collectionId: collection.id,
        type: 'download',
        photoId: photo.id,
        photoName: photo.name,
      })
      notify('Download started')
    } catch {
      notify('Download failed', 'error')
    }
  }

  const requestDownload = (photo: Photo) => {
    if (!collection.downloadEnabled) {
      notify('Downloads are disabled', 'info')
      return
    }
    if (collection.downloadPinEnabled && !downloadUnlocked) {
      setDownloadPrompt(photo.id)
      return
    }
    void downloadPhoto(photo)
  }

  const toggleFavorite = (photo: Photo) => {
    if (!collection.favoritesEnabled) {
      notify('Favorites are disabled for this gallery', 'info')
      return
    }
    const next = !liked[photo.id]
    setLiked((prev) => ({ ...prev, [photo.id]: next }))
    if (next) {
      logGalleryActivity({
        collectionId: collection.id,
        type: 'favorite',
        photoId: photo.id,
        photoName: photo.name,
      })
      if (collection.favoriteNotesEnabled) {
        setNotePrompt(photo)
        setNoteDraft(notes[photo.id] || '')
      } else {
        notify('Added to favorites')
      }
    } else {
      notify('Removed from favorites')
    }
  }

  if (needsPassword) {
    const submit = (e: FormEvent) => {
      e.preventDefault()
      if (collection.password) {
        if (password === collection.password) {
          setUnlocked(true)
          setError('')
        } else setError('Incorrect password')
        return
      }
      // client exclusive without password — accept any non-empty access code for demo
      if (password.trim().length >= 4) {
        setUnlocked(true)
        setError('')
      } else setError('Enter your client access code (min. 4 characters)')
    }
    return (
      <div className="public-shell centered">
        <form className="auth-card" onSubmit={submit}>
          <h1>{collection.name}</h1>
          <p>
            {collection.password
              ? 'Enter the gallery password to view photos.'
              : 'This gallery is client exclusive. Enter your access code.'}
          </p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="form-error">{error}</p>}
          <AppButton type="submit">View gallery</AppButton>
        </form>
      </div>
    )
  }

  const cover = getCoverSrc(collection)

  return (
    <div className="public-shell">
      <div className="public-cover-wrap">
        <CoverPreview
          layout={collection.coverLayout || 'center'}
          title={collection.name}
          imageSrc={cover}
          focal={collection.coverFocal}
        />
        <div className="public-cover-meta">
          <Link href="/site" className="text-button light">
            ← All collections
          </Link>
          <p>
            {collection.eventDate ? formatDateLabel(collection.eventDate) : ''}
            {collection.eventDate ? ' · ' : ''}
            {photos.length} photos
          </p>
          {(collection.favoriteLists ?? []).length > 0 && (
            <p className="public-lists-hint">
              Favorite lists:{' '}
              {collection.favoriteLists.map((l) => `${l.name} (max ${l.selectionLimit})`).join(' · ')}
            </p>
          )}
          <a href="#gallery" className="view-gallery-link">
            VIEW GALLERY
          </a>
        </div>
      </div>

      <div id="gallery" className="public-sets">
        {collection.sets.map((set) => {
          const setPhotos = set.photoIds
            .map((id) => state.photos.find((p) => p.id === id))
            .filter(Boolean)
          if (!setPhotos.length) return null
          return (
            <section key={set.id} className="public-set-block">
              <header className="public-set-header">
                <div>
                  <h2>{set.name}</h2>
                  <small>{state.homepage.brandName}</small>
                  {set.description ? <p>{set.description}</p> : null}
                </div>
              </header>
              <div className="public-photo-grid">
                {setPhotos.map((photo) => {
                  if (!photo) return null
                  const index = photos.findIndex((p) => p.id === photo.id)
                  return (
                    <article key={photo.id} className="public-photo-card">
                      <div className="public-photo-card-head">
                        <div>
                          <strong>{collection.name}</strong>
                          <small>{state.homepage.brandName}</small>
                        </div>
                        <div className="public-photo-card-actions">
                          <button
                            type="button"
                            aria-label="Favorite"
                            className={liked[photo.id] ? 'liked' : undefined}
                            onClick={() => toggleFavorite(photo)}
                          >
                            <Heart size={18} fill={liked[photo.id] ? 'currentColor' : 'none'} />
                          </button>
                          <button
                            type="button"
                            aria-label="Share"
                            onClick={async () => {
                              await navigator.clipboard.writeText(window.location.href)
                              notify('Link copied')
                            }}
                          >
                            <Share2 size={18} />
                          </button>
                          <button
                            type="button"
                            aria-label="Download"
                            onClick={() => requestDownload(photo)}
                          >
                            <Download size={18} />
                          </button>
                        </div>
                      </div>
                      <button
                        type="button"
                        className="public-photo"
                        onClick={() => setLightbox(index)}
                      >
                        <img src={photo.src} alt={photo.name} />
                      </button>
                      {notes[photo.id] && (
                        <p className="public-note">Note: {notes[photo.id]}</p>
                      )}
                    </article>
                  )
                })}
              </div>
            </section>
          )
        })}
      </div>

      {lightbox !== null && photos[lightbox] && (
        <div className="lightbox" onClick={() => setLightbox(null)}>
          <button type="button" className="lightbox-close" aria-label="Close">
            <X />
          </button>
          <button
            type="button"
            className="lightbox-nav prev"
            onClick={(e) => {
              e.stopPropagation()
              setLightbox((i) => (i === null ? i : (i - 1 + photos.length) % photos.length))
            }}
          >
            <ChevronLeft />
          </button>
          <img
            src={photos[lightbox].src}
            alt={photos[lightbox].name}
            onClick={(e) => e.stopPropagation()}
          />
          <div className="lightbox-actions" onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => toggleFavorite(photos[lightbox])}>
              <Heart size={18} fill={liked[photos[lightbox].id] ? 'currentColor' : 'none'} /> Favorite
            </button>
            <button type="button" onClick={() => requestDownload(photos[lightbox])}>
              <Download size={18} /> Download
            </button>
          </div>
          <button
            type="button"
            className="lightbox-nav next"
            onClick={(e) => {
              e.stopPropagation()
              setLightbox((i) => (i === null ? i : (i + 1) % photos.length))
            }}
          >
            <ChevronRight />
          </button>
        </div>
      )}

      {downloadPrompt && (
        <div className="modal-backdrop" onClick={() => setDownloadPrompt(null)}>
          <form
            className="auth-card"
            onClick={(e) => e.stopPropagation()}
            onSubmit={async (e) => {
              e.preventDefault()
              if (downloadPinInput !== collection.downloadPin) {
                notify('Incorrect download PIN', 'error')
                return
              }
              setDownloadUnlocked(true)
              const photo = state.photos.find((p) => p.id === downloadPrompt)
              setDownloadPrompt(null)
              notify('PIN accepted — downloads unlocked')
              setDownloadPinInput('')
              if (photo) await downloadPhoto(photo)
            }}
          >
            <h1>Download PIN</h1>
            <p>Enter the 4-digit PIN to download photos.</p>
            <input
              value={downloadPinInput}
              onChange={(e) => setDownloadPinInput(e.target.value)}
              placeholder="••••"
              maxLength={4}
              inputMode="numeric"
            />
            <AppButton type="submit">Unlock downloads</AppButton>
          </form>
        </div>
      )}

      <Modal
        open={Boolean(notePrompt)}
        title="ADD A NOTE"
        onClose={() => setNotePrompt(null)}
      >
        <p className="confirm-copy">
          Optional note for “{notePrompt?.name}”. Clients use notes during proofing.
        </p>
        <textarea
          className="bio"
          value={noteDraft}
          onChange={(e) => setNoteDraft(e.target.value)}
          placeholder="e.g. Prefer this for the album cover"
          rows={4}
        />
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setNotePrompt(null)}>
            Skip
          </button>
          <AppButton
            onClick={() => {
              if (!notePrompt) return
              setNotes((prev) => ({ ...prev, [notePrompt.id]: noteDraft.trim() }))
              if (noteDraft.trim()) {
                logGalleryActivity({
                  collectionId: collection.id,
                  type: 'note',
                  photoId: notePrompt.id,
                  photoName: notePrompt.name,
                  note: noteDraft.trim(),
                })
              }
              notify('Favorite saved')
              setNotePrompt(null)
            }}
          >
            Save note
          </AppButton>
        </div>
      </Modal>
    </div>
  )
}
