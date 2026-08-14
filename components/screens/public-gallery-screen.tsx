'use client'

import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Heart,
  ImageOff,
  Share2,
  X,
} from 'lucide-react'
import { useGallery } from '@/lib/gallery-context'
import { AppButton } from '@/components/app-button'
import { Modal } from '@/components/modal'
import { PublicPixeoFooter } from '@/components/public-pixeo-footer'
import { useToast } from '@/components/toast-provider'
import type { Photo } from '@/lib/types'

function photographerPlanId(state: ReturnType<typeof useGallery>['state']) {
  if (state.user?.planId) return state.user.planId
  const owner = state.accounts.find((a) => a.role === 'photographer')
  return owner?.planId ?? 'free'
}

function formatCoverDate(iso?: string) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso.toUpperCase()
  const day = d.getDate()
  const ord =
    day % 10 === 1 && day !== 11
      ? 'ST'
      : day % 10 === 2 && day !== 12
        ? 'ND'
        : day % 10 === 3 && day !== 13
          ? 'RD'
          : 'TH'
  const month = d.toLocaleDateString('en-US', { month: 'long' }).toUpperCase()
  return `${month} ${day}${ord}, ${d.getFullYear()}`
}

export function PublicGalleryScreen({
  slug,
  ownerPreview = false,
}: {
  slug: string
  ownerPreview?: boolean
}) {
  const { ready, state, getCollectionPhotos, getCoverSrc, logGalleryActivity } = useGallery()
  const { notify } = useToast()
  const collection = state.collections.find((c) => c.slug === slug)
  const galleryRef = useRef<HTMLElement | null>(null)
  const navRef = useRef<HTMLElement | null>(null)
  const [unlocked, setUnlocked] = useState(ownerPreview)
  const [scrollingToGallery, setScrollingToGallery] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [lightbox, setLightbox] = useState<number | null>(null)
  const [liked, setLiked] = useState<Record<string, boolean>>({})
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [downloadUnlocked, setDownloadUnlocked] = useState(false)
  const [downloadPinInput, setDownloadPinInput] = useState('')
  const [downloadPrompt, setDownloadPrompt] = useState<string | null>(null)
  const [bulkDownloading, setBulkDownloading] = useState(false)
  const [notePrompt, setNotePrompt] = useState<Photo | null>(null)
  const [noteDraft, setNoteDraft] = useState('')

  const ownerPlanId = photographerPlanId(state)
  const showWatermarkBanner = ownerPlanId === 'free' || state.branding.watermarkEnabled
  const brand = (state.homepage.brandName || 'PIXEO').toUpperCase()

  const photos = useMemo(
    () => (collection ? getCollectionPhotos(collection) : []),
    [collection, getCollectionPhotos],
  )

  const downloadsAllowed = Boolean(collection?.downloadEnabled)
  const favoritesAllowed = Boolean(collection?.favoritesEnabled)
  const unpublished =
    Boolean(collection) && (collection!.status === 'draft' || collection!.status === 'hidden')

  useEffect(() => {
    if (!collection) return
    if (unpublished && !ownerPreview) return
    if (collection.password && !unlocked && !ownerPreview) return
    logGalleryActivity({
      collectionId: collection.id,
      type: 'view',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collection?.id, unlocked, ownerPreview])

  if (!ready) return <div className="public-shell">Loading…</div>

  if (!collection || (unpublished && !ownerPreview)) {
    return (
      <div className="public-shell centered">
        <h1>Gallery unavailable</h1>
        <p>
          This Pixeo gallery is not published or does not exist. Ask your photographer for an
          updated link.
        </p>
        <Link href="/site" className="primary-button">
          Back to homepage
        </Link>
        <PublicPixeoFooter />
      </div>
    )
  }

  const needsPassword =
    !ownerPreview && (Boolean(collection.password) || collection.clientExclusive) && !unlocked

  const downloadPhoto = async (photo: Photo, silent = false) => {
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
      if (!silent) notify('Download started')
    } catch {
      if (!silent) notify('Download failed', 'error')
      throw new Error('download failed')
    }
  }

  const ensureDownloadAccess = () => {
    if (!collection.downloadEnabled) {
      notify('Downloads are disabled for this Pixeo gallery', 'info')
      return false
    }
    if (collection.downloadPinEnabled && !downloadUnlocked && !ownerPreview) {
      setDownloadPrompt('__all__')
      return false
    }
    return true
  }

  const requestDownload = (photo: Photo) => {
    if (!collection.downloadEnabled) {
      notify('Downloads are disabled for this Pixeo gallery', 'info')
      return
    }
    if (collection.downloadPinEnabled && !downloadUnlocked && !ownerPreview) {
      setDownloadPrompt(photo.id)
      return
    }
    void downloadPhoto(photo)
  }

  const downloadAllPhotos = async (skipAccessCheck = false) => {
    if (!skipAccessCheck && !ensureDownloadAccess()) return
    if (!photos.length) {
      notify('No photos to download', 'info')
      return
    }
    setBulkDownloading(true)
    notify(`Downloading ${photos.length} photos…`, 'info')
    try {
      for (const photo of photos) {
        await downloadPhoto(photo, true)
        await new Promise((r) => setTimeout(r, 280))
      }
      notify('All downloads started')
    } catch {
      notify('Some downloads failed', 'error')
    } finally {
      setBulkDownloading(false)
    }
  }

  const shareGallery = async () => {
    const url = `${window.location.origin}/c/${collection.slug}`
    try {
      if (navigator.share) {
        await navigator.share({
          title: collection.name,
          text: `View ${collection.name} on Pixeo`,
          url,
        })
        return
      }
      await navigator.clipboard.writeText(url)
      notify('Gallery link copied')
    } catch {
      try {
        await navigator.clipboard.writeText(url)
        notify('Gallery link copied')
      } catch {
        notify(url, 'info')
      }
    }
  }

  const scrollToGallery = () => {
    const el = navRef.current ?? galleryRef.current
    if (!el) return
    setScrollingToGallery(true)
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    window.setTimeout(() => setScrollingToGallery(false), 900)
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
              ? 'This Pixeo gallery is password protected. Enter the password from your photographer.'
              : 'This gallery is client exclusive on Pixeo. Enter your access code.'}
          </p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="form-error">{error}</p>}
          <AppButton type="submit">View gallery</AppButton>
        </form>
        <PublicPixeoFooter showWatermarkBanner={showWatermarkBanner} />
      </div>
    )
  }

  const cover = getCoverSrc(collection)
  const hasVisiblePhotos = photos.length > 0
  const coverDate = formatCoverDate(collection.eventDate)

  return (
    <div className="public-shell gallery-page">
      {ownerPreview && (
        <div className="owner-preview-banner">
          Viewing collection as <b>Owner.</b>
        </div>
      )}

      <section className="gallery-intro on-page">
        <div
          className="gallery-intro-bg"
          style={cover ? { backgroundImage: `url(${cover})` } : undefined}
        />
        <div className="gallery-intro-content">
          <h1>{collection.name}</h1>
          {coverDate ? <p className="gallery-intro-date">{coverDate}</p> : null}
          {hasVisiblePhotos ? (
            <button
              type="button"
              className={`view-gallery-btn ${scrollingToGallery ? 'is-animating' : ''}`}
              onClick={scrollToGallery}
            >
              VIEW GALLERY
            </button>
          ) : (
            <p className="gallery-intro-empty">No photos yet</p>
          )}
        </div>
        <p className="gallery-intro-brand">{brand}</p>
        {hasVisiblePhotos && (
          <button
            type="button"
            className="gallery-scroll-hint"
            onClick={scrollToGallery}
            aria-label="Scroll to photos"
          >
            <span />
          </button>
        )}
      </section>

      <nav ref={navRef} className="gallery-below-nav" aria-label="Gallery actions">
        <div className="gallery-sticky-nav-meta">
          <strong>{collection.name}</strong>
          {coverDate ? <span>{coverDate}</span> : null}
        </div>
        <div className="gallery-sticky-nav-actions">
          <button
            type="button"
            className={!downloadsAllowed ? 'action-disabled' : undefined}
            disabled={bulkDownloading}
            onClick={() => void downloadAllPhotos()}
          >
            <Download size={16} />
            {bulkDownloading ? 'Downloading…' : 'Download all'}
          </button>
          <button type="button" onClick={() => void shareGallery()}>
            <Share2 size={16} />
            Share
          </button>
        </div>
      </nav>

      <section
        id="gallery"
        ref={galleryRef}
        className={`gallery-photos-section ${scrollingToGallery ? 'is-revealing' : ''}`}
      >
        {!hasVisiblePhotos ? (
          <div className="public-empty-state">
            <ImageOff size={40} strokeWidth={1.25} />
            <h2>No photos yet</h2>
            <p>
              {state.homepage.brandName || 'Your photographer'} is still preparing this Pixeo
              gallery. Check back soon or contact them for updates.
            </p>
          </div>
        ) : (
          <div className="public-masonry">
            {photos.map((photo, index) => (
              <article key={photo.id} className="public-masonry-item">
                <button
                  type="button"
                  className="public-masonry-photo"
                  onClick={() => setLightbox(index)}
                >
                  <img src={photo.src} alt={photo.name} />
                </button>
                <div className="public-masonry-actions">
                  <button
                    type="button"
                    aria-label="Like"
                    className={[
                      liked[photo.id] ? 'liked' : undefined,
                      !favoritesAllowed ? 'action-disabled' : undefined,
                    ]
                      .filter(Boolean)
                      .join(' ')}
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(photo)
                    }}
                  >
                    <Heart size={18} fill={liked[photo.id] ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    type="button"
                    aria-label="Share"
                    onClick={(e) => {
                      e.stopPropagation()
                      void shareGallery()
                    }}
                  >
                    <Share2 size={18} />
                  </button>
                  <button
                    type="button"
                    aria-label="Download"
                    className={!downloadsAllowed ? 'action-disabled' : undefined}
                    onClick={(e) => {
                      e.stopPropagation()
                      requestDownload(photo)
                    }}
                  >
                    <Download size={18} />
                  </button>
                </div>
                {notes[photo.id] && <p className="public-note">Note: {notes[photo.id]}</p>}
              </article>
            ))}
          </div>
        )}
      </section>

      <PublicPixeoFooter showWatermarkBanner={showWatermarkBanner} />

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
            <button
              type="button"
              className={!favoritesAllowed ? 'action-disabled' : undefined}
              onClick={() => toggleFavorite(photos[lightbox])}
            >
              <Heart size={18} fill={liked[photos[lightbox].id] ? 'currentColor' : 'none'} />{' '}
              Favorite
            </button>
            <button type="button" onClick={() => void shareGallery()}>
              <Share2 size={18} /> Share
            </button>
            <button
              type="button"
              className={!downloadsAllowed ? 'action-disabled' : undefined}
              onClick={() => requestDownload(photos[lightbox])}
            >
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
              const prompt = downloadPrompt
              setDownloadPrompt(null)
              notify('PIN accepted — downloads unlocked')
              setDownloadPinInput('')
              if (prompt === '__all__') {
                await downloadAllPhotos(true)
                return
              }
              const photo = state.photos.find((p) => p.id === prompt)
              if (photo) await downloadPhoto(photo)
            }}
          >
            <h1>Download PIN</h1>
            <p>Enter the 4-digit PIN from your photographer to download photos on Pixeo.</p>
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

      <Modal open={Boolean(notePrompt)} title="ADD A NOTE" onClose={() => setNotePrompt(null)}>
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
