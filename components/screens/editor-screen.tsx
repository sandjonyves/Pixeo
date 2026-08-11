'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  ArrowLeftRight,
  Check,
  ChevronLeft,
  Copy,
  Download,
  Expand,
  FolderInput,
  GripHorizontal,
  Heart,
  History,
  Image as ImageIcon,
  LayoutGrid,
  Link2,
  Mail,
  Maximize2,
  Monitor,
  MoreHorizontal,
  MoveRight,
  Palette,
  Pencil,
  Plus,
  QrCode,
  Radio,
  Search,
  Settings as SettingsIcon,
  Share2,
  Smartphone,
  SortAsc,
  Sparkles,
  Trash2,
  Upload,
} from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { ConfirmDialog, Modal } from '@/components/modal'
import { CoverLayoutPicker, CoverPreview } from '@/components/editor/cover-preview'
import { ShareCollectionOverlay } from '@/components/editor/share-collection-overlay'
import {
  CollectionSettingsNav,
  CollectionSettingsPanel,
  GetDirectLinkModal,
  type SettingsSection,
} from '@/components/editor/collection-settings-panel'
import { useGallery, readImageFiles } from '@/lib/gallery-context'
import { formatDateLabel } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'
import type { CollectionStatus, CoverLayout, Photo } from '@/lib/types'

const STATUSES: CollectionStatus[] = ['published', 'pre-release', 'hidden', 'draft']
type EditorTab = 'photos' | 'design' | 'settings' | 'integrations'
type DesignTool = 'cover' | 'stripe' | 'divider'

export function EditorScreen({ collectionId }: { collectionId: string }) {
  const router = useRouter()
  const fileRef = useRef<HTMLInputElement>(null)
  const replaceRef = useRef<HTMLInputElement>(null)
  const coverPickRef = useRef<HTMLInputElement>(null)
  const {
    state,
    getCollectionPhotos,
    getCoverSrc,
    updateCollection,
    setCollectionStatus,
    addPhotosToCollection,
    addStockPhotos,
    removePhotosFromCollection,
    movePhotosToSet,
    addSet,
    updateSet,
    deleteSet,
    reorderSets,
    updatePhoto,
    replacePhoto,
    setCoverPhoto,
    deleteCollection,
    duplicateCollection,
    savePreset,
    applyPreset,
  } = useGallery()
  const { notify } = useToast()

  const collection = state.collections.find((c) => c.id === collectionId)
  const [tab, setTab] = useState<EditorTab>('photos')
  const [designTool, setDesignTool] = useState<DesignTool>('cover')
  const [settingsSection, setSettingsSection] = useState<SettingsSection>('general')
  const [activeSetId, setActiveSetId] = useState(collection?.sets[0]?.id)
  const [selected, setSelected] = useState<string[]>([])
  const [query, setQuery] = useState('')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'mobile'>('desktop')
  const [gridCols, setGridCols] = useState(5)
  const [sortAsc, setSortAsc] = useState(true)
  const [statusOpen, setStatusOpen] = useState(false)
  const [moreOpen, setMoreOpen] = useState(false)
  const [shareMenuOpen, setShareMenuOpen] = useState(false)
  const [setMenuId, setSetMenuId] = useState<string | null>(null)
  const [photoMenuId, setPhotoMenuId] = useState<string | null>(null)
  const [modal, setModal] = useState<
    | 'media'
    | 'share-email'
    | 'edit-set'
    | 'rename-photo'
    | 'move-photo'
    | 'focal'
    | 'email-history'
    | 'presets'
    | 'move-collection'
    | 'qr'
    | 'create-style'
    | 'direct-link'
    | null
  >(null)
  const [shareInitialMode, setShareInitialMode] = useState<'email' | 'link' | 'qr'>('email')
  const [styleName, setStyleName] = useState('')
  const [moveFolder, setMoveFolder] = useState('Client Galleries')
  const [editingSetId, setEditingSetId] = useState<string | null>(null)
  const [setName, setSetName] = useState('')
  const [setDescription, setSetDescription] = useState('')
  const [photoNameDraft, setPhotoNameDraft] = useState('')
  const [renamePhotoId, setRenamePhotoId] = useState<string | null>(null)
  const [movePhotoIds, setMovePhotoIds] = useState<string[]>([])
  const [lightbox, setLightbox] = useState<number | null>(null)
  const [uploading, setUploading] = useState(false)
  const [confirmDeleteSet, setConfirmDeleteSet] = useState<string | null>(null)
  const [confirmDeleteCollection, setConfirmDeleteCollection] = useState(false)
  const [dragFrom, setDragFrom] = useState<number | null>(null)
  const [titleEditing, setTitleEditing] = useState(false)
  const [titleDraft, setTitleDraft] = useState(collection?.name ?? '')

  useEffect(() => {
    if (collection) {
      setActiveSetId((current) => current || collection.sets[0]?.id)
      setTitleDraft(collection.name)
    }
  }, [collection])

  const photos = useMemo(() => {
    if (!collection) return []
    const list = getCollectionPhotos(collection, activeSetId || collection.sets[0]?.id)
    const q = query.trim().toLowerCase()
    const filtered = q ? list.filter((p) => p.name.toLowerCase().includes(q)) : list
    return [...filtered].sort((a, b) =>
      sortAsc ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name),
    )
  }, [collection, activeSetId, getCollectionPhotos, query, sortAsc])

  if (!collection) {
    return (
      <div className="editor-shell missing">
        <p>Collection not found.</p>
        <Link href="/collections" className="primary-button">
          Back to collections
        </Link>
      </div>
    )
  }

  const cover = getCoverSrc(collection)
  const activeSet = collection.sets.find((s) => s.id === activeSetId) || collection.sets[0]
  const publicUrl =
    typeof window !== 'undefined'
      ? `${window.location.origin}/c/${collection.slug}`
      : `/c/${collection.slug}`

  const uploadFiles = async (files: FileList | null) => {
    if (!files?.length) return
    setUploading(true)
    try {
      const images = await readImageFiles(files)
      if (!images.length) {
        notify('Select image files only.', 'error')
        return
      }
      addPhotosToCollection(collection.id, images, activeSetId)
      notify(`${images.length} photo(s) uploaded`)
      setModal(null)
    } catch {
      notify('Upload failed. Try smaller images.', 'error')
    } finally {
      setUploading(false)
    }
  }

  const downloadPhoto = async (photo: Photo) => {
    try {
      const res = await fetch(photo.src)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = photo.name || 'photo.jpg'
      a.click()
      URL.revokeObjectURL(url)
      notify('Download started')
    } catch {
      notify('Could not download this photo.', 'error')
    }
  }

  const publish = () => {
    setCollectionStatus(collection.id, 'published')
    notify('Collection published')
  }

  return (
    <div className={`editor-shell v2 ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <header className="editor-top">
        <div className="editor-top-left">
          <Link href="/collections" aria-label="Back">
            <ChevronLeft />
          </Link>
          <div className="editor-title-block">
            {titleEditing ? (
              <input
                className="inline-title-input"
                value={titleDraft}
                autoFocus
                onChange={(e) => setTitleDraft(e.target.value)}
                onBlur={() => {
                  if (titleDraft.trim()) {
                    updateCollection(collection.id, { name: titleDraft.trim() })
                    notify('Title updated')
                  }
                  setTitleEditing(false)
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') (e.target as HTMLInputElement).blur()
                }}
              />
            ) : (
              <button type="button" className="title-btn" onClick={() => setTitleEditing(true)}>
                <b>{collection.name}</b>
              </button>
            )}
            <button
              type="button"
              className="date-btn"
              onClick={() => {
                const next = window.prompt('Event date (YYYY-MM-DD)', collection.eventDate || '')
                if (next !== null) {
                  updateCollection(collection.id, { eventDate: next || undefined })
                  notify(next ? 'Event date saved' : 'Event date cleared')
                }
              }}
            >
              {collection.eventDate ? formatDateLabel(collection.eventDate) : 'Add event date'}
            </button>
          </div>
          <div className="menu-anchor">
            <button
              type="button"
              className={`published-label ${collection.status}`}
              onClick={() => setStatusOpen((v) => !v)}
            >
              {collection.status.toUpperCase()}⌄
            </button>
            {statusOpen && (
              <div className="dropdown-panel">
                {STATUSES.map((status) => (
                  <button
                    key={status}
                    type="button"
                    onClick={() => {
                      setCollectionStatus(collection.id, status)
                      setStatusOpen(false)
                      notify(`Status set to ${status}`)
                    }}
                  >
                    {status}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <label className="editor-search">
          <Search size={18} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search"
            aria-label="Search photos"
          />
        </label>

        <div className="editor-actions">
          <div className="menu-anchor">
            <button
              type="button"
              onClick={() => {
                setMoreOpen((v) => !v)
                setShareMenuOpen(false)
              }}
            >
              More⌄
            </button>
            {moreOpen && (
              <div className="dropdown-panel more-menu">
                <button
                  type="button"
                  onClick={async () => {
                    setModal('direct-link')
                    setMoreOpen(false)
                  }}
                >
                  <Link2 size={16} /> Get direct link
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setModal('email-history')
                    setMoreOpen(false)
                  }}
                >
                  <History size={16} /> View email history
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setModal('presets')
                    setMoreOpen(false)
                  }}
                >
                  <SettingsIcon size={16} /> Manage presets
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setModal('move-collection')
                    setMoreOpen(false)
                  }}
                >
                  <FolderInput size={16} /> Move to
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const copy = duplicateCollection(collection.id)
                    setMoreOpen(false)
                    if (copy) {
                      notify('Collection duplicated')
                      router.push(`/editor/${copy.id}`)
                    }
                  }}
                >
                  <Copy size={16} /> Duplicate
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMoreOpen(false)
                    setConfirmDeleteCollection(true)
                  }}
                >
                  <Trash2 size={16} /> Delete collection
                </button>
                <hr className="menu-divider" />
                <button
                  type="button"
                  onClick={() => {
                    setStyleName(`${collection.name} Style`)
                    setModal('create-style')
                    setMoreOpen(false)
                  }}
                >
                  <Sparkles size={16} /> Create Style
                </button>
              </div>
            )}
          </div>
          <button type="button" onClick={() => window.open(publicUrl, '_blank')}>
            Preview
          </button>
          {collection.status === 'published' ? (
            <div className="share-split menu-anchor">
              <button
                type="button"
                className="share-main"
                onClick={() => {
                  setShareInitialMode('email')
                  setModal('share-email')
                  setShareMenuOpen(false)
                }}
              >
                Share
              </button>
              <button
                type="button"
                className="share-chevron"
                aria-label="Share options"
                onClick={() => {
                  setShareMenuOpen((v) => !v)
                  setMoreOpen(false)
                }}
              >
                ⌄
              </button>
              {shareMenuOpen && (
                <div className="dropdown-panel share-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setShareInitialMode('email')
                      setModal('share-email')
                      setShareMenuOpen(false)
                    }}
                  >
                    <Mail size={16} /> Share by email
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setModal('direct-link')
                      setShareMenuOpen(false)
                    }}
                  >
                    <Link2 size={16} /> Get direct link
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setModal('qr')
                      setShareMenuOpen(false)
                    }}
                  >
                    <QrCode size={16} /> Get QR code
                  </button>
                </div>
              )}
            </div>
          ) : (
            <AppButton onClick={publish}>Publish</AppButton>
          )}
        </div>
      </header>

      <div className="editor-body v2">
        <aside className="editor-sidebar v2">
          <div className="editor-cover-thumb">
            {cover ? <img src={cover} alt="cover" /> : <div className="collection-cover-empty tall">No cover</div>}
          </div>

          <div className="editor-icons">
            {(
              [
                ['photos', ImageIcon],
                ['design', Palette],
                ['settings', SettingsIcon],
                ['integrations', Radio],
              ] as const
            ).map(([key, Icon]) => (
              <button
                key={key}
                type="button"
                className={tab === key ? 'active-icon' : undefined}
                aria-label={key}
                onClick={() => {
                  setTab(key)
                  if (key === 'settings') setSettingsSection('privacy')
                }}
              >
                <Icon size={22} />
              </button>
            ))}
          </div>

          {tab === 'photos' && (
            <div className="editor-set">
              <small>
                PHOTOS{' '}
                <button
                  type="button"
                  className="linkish"
                  onClick={() => {
                    const id = addSet(collection.id, `Set ${collection.sets.length + 1}`)
                    setActiveSetId(id)
                    notify('Set added')
                  }}
                >
                  <Plus size={14} /> Add Set
                </button>
              </small>
              {collection.sets.map((set, index) => (
                <div
                  key={set.id}
                  className={`set-row-wrap ${activeSetId === set.id ? 'active' : ''}`}
                  draggable
                  onDragStart={() => setDragFrom(index)}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={() => {
                    if (dragFrom === null || dragFrom === index) return
                    reorderSets(collection.id, dragFrom, index)
                    setDragFrom(null)
                    notify('Sets reordered')
                  }}
                >
                  <button
                    type="button"
                    className="set-row"
                    onClick={() => {
                      setActiveSetId(set.id)
                      setSelected([])
                      setSetMenuId(null)
                    }}
                  >
                    <GripHorizontal size={16} />
                    <span>
                      {set.name} ({set.photoIds.length})
                    </span>
                  </button>
                  <div className="menu-anchor">
                    <button
                      type="button"
                      className="set-more"
                      onClick={() => setSetMenuId(setMenuId === set.id ? null : set.id)}
                    >
                      <MoreHorizontal size={18} />
                    </button>
                    {setMenuId === set.id && (
                      <div className="dropdown-panel set-menu">
                        <button
                          type="button"
                          onClick={() => {
                            setEditingSetId(set.id)
                            setSetName(set.name)
                            setSetDescription(set.description || '')
                            setModal('edit-set')
                            setSetMenuId(null)
                          }}
                        >
                          <Pencil size={16} /> Edit set
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setConfirmDeleteSet(set.id)
                            setSetMenuId(null)
                          }}
                        >
                          <Trash2 size={16} /> Delete set
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === 'design' && (
            <div className="editor-set design-nav">
              <small>DESIGN</small>
              {(
                [
                  ['cover', 'Cover', ImageIcon],
                  ['stripe', 'Stripe', LayoutGrid],
                  ['divider', 'Divider', ArrowLeftRight],
                ] as const
              ).map(([id, label, Icon]) => (
                <button
                  key={id}
                  type="button"
                  className={`set-row ${designTool === id ? 'active' : ''}`}
                  onClick={() => setDesignTool(id)}
                >
                  <Icon size={18} />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          )}

          {tab === 'settings' && (
            <CollectionSettingsNav
              collection={collection}
              active={settingsSection}
              onChangeSection={setSettingsSection}
            />
          )}

          {tab === 'integrations' && (
            <div className="editor-set">
              <small>INTEGRATIONS</small>
              <p className="side-hint">Connect Lightroom or Drive in a future release.</p>
            </div>
          )}

          <button
            type="button"
            className="sidebar-collapse"
            aria-label="Collapse sidebar"
            onClick={() => setSidebarCollapsed((v) => !v)}
          >
            <ChevronLeft size={18} />
          </button>
        </aside>

        {tab === 'photos' && (
          <section className="editor-grid" key={`photos-${activeSetId}`}>
            <div className="page-heading">
              <div>
                <h1>{activeSet?.name || 'Highlights'}</h1>
                {activeSet?.description ? (
                  <p className="set-desc">{activeSet.description}</p>
                ) : null}
              </div>
              <div className="heading-actions">
                <button
                  type="button"
                  className="icon-tool"
                  aria-label="Sort"
                  onClick={() => {
                    setSortAsc((v) => !v)
                    notify(sortAsc ? 'Sorted Z–A' : 'Sorted A–Z')
                  }}
                >
                  <SortAsc size={18} />
                </button>
                <button
                  type="button"
                  className="icon-tool"
                  aria-label="Grid density"
                  onClick={() => setGridCols((c) => (c === 5 ? 3 : c === 3 ? 6 : 5))}
                >
                  <LayoutGrid size={18} />
                </button>
                {selected.length > 0 && (
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => {
                      setMovePhotoIds(selected)
                      setModal('move-photo')
                    }}
                  >
                    Move
                  </button>
                )}
                <AppButton onClick={() => setModal('media')}>＋ Add Media</AppButton>
              </div>
            </div>

            {photos.length === 0 ? (
              <div className="empty-state compact">
                <Upload size={42} />
                <h2>Add photos to this set</h2>
                <p>Upload from your computer or insert sample photos.</p>
                <AppButton onClick={() => setModal('media')}>Add Media</AppButton>
              </div>
            ) : (
              <div className="photo-grid" style={{ gridTemplateColumns: `repeat(${gridCols}, minmax(100px, 1fr))` }}>
                {photos.map((photo, index) => {
                  const isSelected = selected.includes(photo.id)
                  return (
                    <div
                      key={photo.id}
                      className={isSelected ? 'photo-card selected' : 'photo-card'}
                    >
                      <button
                        type="button"
                        className="photo-hit"
                        onClick={() =>
                          setSelected((current) =>
                            current.includes(photo.id)
                              ? current.filter((id) => id !== photo.id)
                              : [...current, photo.id],
                          )
                        }
                        onDoubleClick={() => setLightbox(index)}
                      >
                        <img src={photo.src} alt={photo.name} />
                        {isSelected && (
                          <span className="photo-check">
                            <Check size={16} />
                          </span>
                        )}
                      </button>
                      <div className="menu-anchor photo-menu-anchor">
                        <button
                          type="button"
                          className="photo-kebab"
                          aria-label="Photo actions"
                          onClick={() =>
                            setPhotoMenuId(photoMenuId === photo.id ? null : photo.id)
                          }
                        >
                          ⋮
                        </button>
                        {photoMenuId === photo.id && (
                          <div className="dropdown-panel photo-menu">
                            <button type="button" onClick={() => { setLightbox(index); setPhotoMenuId(null) }}>
                              <Maximize2 size={16} /> Open
                            </button>
                            <button
                              type="button"
                              onClick={async () => {
                                await navigator.clipboard.writeText(`${publicUrl}?photo=${photo.id}`)
                                notify('Quick share link copied')
                                setPhotoMenuId(null)
                              }}
                            >
                              <Link2 size={16} /> Quick share
                            </button>
                            <button type="button" onClick={() => { void downloadPhoto(photo); setPhotoMenuId(null) }}>
                              <Download size={16} /> Download
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setMovePhotoIds([photo.id])
                                setModal('move-photo')
                                setPhotoMenuId(null)
                              }}
                            >
                              <MoveRight size={16} /> Move/Copy
                            </button>
                            <button
                              type="button"
                              onClick={async () => {
                                await navigator.clipboard.writeText(photo.name)
                                notify('Filename copied')
                                setPhotoMenuId(null)
                              }}
                            >
                              <Copy size={16} /> Copy filename
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setCoverPhoto(collection.id, photo.id)
                                notify('Cover photo updated')
                                setPhotoMenuId(null)
                              }}
                            >
                              <ImageIcon size={16} /> Set as cover
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setRenamePhotoId(photo.id)
                                setPhotoNameDraft(photo.name)
                                setModal('rename-photo')
                                setPhotoMenuId(null)
                              }}
                            >
                              <Pencil size={16} /> Rename
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setRenamePhotoId(photo.id)
                                replaceRef.current?.click()
                                setPhotoMenuId(null)
                              }}
                            >
                              <ArrowLeftRight size={16} /> Replace photo
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </section>
        )}

        {tab === 'design' && (
          <section className="editor-design" key={`design-${designTool}`}>
            <div className="design-middle">
              {designTool === 'cover' && (
                <>
                  <div className="page-heading">
                    <h1>Cover</h1>
                    <div className="heading-actions">
                      <button
                        type="button"
                        className="linkish"
                        onClick={() => coverPickRef.current?.click()}
                      >
                        <ImageIcon size={16} /> Cover Photo
                      </button>
                      <button type="button" className="linkish" onClick={() => setModal('focal')}>
                        <Expand size={16} /> Focal
                      </button>
                    </div>
                  </div>
                  <CoverLayoutPicker
                    collection={collection}
                    coverSrc={cover}
                    onSelect={(layout: CoverLayout) => {
                      updateCollection(collection.id, { coverLayout: layout })
                      notify(`${layout} layout applied`)
                    }}
                  />
                </>
              )}
              {designTool === 'stripe' && (
                <div className="block-picker">
                  <h1>Stripe</h1>
                  <p>Full-width image band for storytelling between photo sets.</p>
                  <div className="block-card">
                    <div
                      className="block-stripe"
                      style={cover ? { backgroundImage: `url(${cover})` } : undefined}
                    />
                    <span>Stripe</span>
                  </div>
                  <AppButton onClick={() => notify('Stripe block enabled on client gallery', 'info')}>
                    Use Stripe block
                  </AppButton>
                </div>
              )}
              {designTool === 'divider' && (
                <div className="block-picker">
                  <h1>Divider</h1>
                  <p>Split two images side by side with an optional title panel.</p>
                  <div className="block-card">
                    <div className="block-divider">
                      <div style={cover ? { backgroundImage: `url(${cover})` } : undefined}>
                        <span>TITLE</span>
                      </div>
                      <div
                        style={
                          photos[1]
                            ? { backgroundImage: `url(${photos[1].src})` }
                            : cover
                              ? { backgroundImage: `url(${cover})` }
                              : undefined
                        }
                      />
                    </div>
                    <span>Divider</span>
                  </div>
                  <AppButton onClick={() => notify('Divider block enabled on client gallery', 'info')}>
                    Use Divider block
                  </AppButton>
                </div>
              )}
            </div>

            <div className="design-preview-pane">
              <div className={`preview-canvas ${previewDevice}`}>
                <CoverPreview
                  layout={collection.coverLayout || 'center'}
                  title={collection.name}
                  imageSrc={cover}
                  focal={collection.coverFocal}
                />
                <div className="preview-gallery-strip">
                  {photos.slice(0, 4).map((p) => (
                    <div key={p.id} className="preview-item">
                      <img src={p.src} alt="" />
                      <div className="preview-item-actions">
                        <Share2 size={14} />
                        <Heart size={14} />
                        <Download size={14} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="device-toggle">
                <button
                  type="button"
                  className={previewDevice === 'desktop' ? 'active' : undefined}
                  onClick={() => setPreviewDevice('desktop')}
                  aria-label="Desktop preview"
                >
                  <Monitor size={18} />
                </button>
                <button
                  type="button"
                  className={previewDevice === 'mobile' ? 'active' : undefined}
                  onClick={() => setPreviewDevice('mobile')}
                  aria-label="Mobile preview"
                >
                  <Smartphone size={18} />
                </button>
              </div>
            </div>
          </section>
        )}

        {tab === 'settings' && (
          <CollectionSettingsPanel
            key={settingsSection}
            collection={collection}
            publicUrl={publicUrl}
            active={settingsSection}
            onChangeSection={setSettingsSection}
          />
        )}

        {tab === 'integrations' && (
          <section className="editor-grid">
            <h1>Integrations</h1>
            <p className="confirm-copy">
              Connect Adobe Lightroom, Dropbox or Google Drive to import photos automatically.
            </p>
            <AppButton secondary onClick={() => notify('Integration catalog opened', 'info')}>
              Browse integrations
            </AppButton>
          </section>
        )}
      </div>

      <input ref={fileRef} type="file" accept="image/*" multiple hidden onChange={(e) => void uploadFiles(e.target.files)} />
      <input
        ref={replaceRef}
        type="file"
        accept="image/*"
        hidden
        onChange={async (e) => {
          if (!renamePhotoId || !e.target.files?.length) return
          const [image] = await readImageFiles(e.target.files)
          replacePhoto(renamePhotoId, image)
          notify('Photo replaced')
          setRenamePhotoId(null)
          e.target.value = ''
        }}
      />
      <input
        ref={coverPickRef}
        type="file"
        accept="image/*"
        hidden
        onChange={async (e) => {
          if (!e.target.files?.length) return
          const images = await readImageFiles(e.target.files)
          const ids = addPhotosToCollection(collection.id, images, activeSetId)
          if (ids[0]) {
            setCoverPhoto(collection.id, ids[0])
            notify('Cover photo updated')
          }
          e.target.value = ''
        }}
      />

      <Modal open={modal === 'media'} title="ADD MEDIA" onClose={() => setModal(null)} wide>
        <div className="media-tabs">
          <button type="button" className="active">Upload</button>
          <button
            type="button"
            onClick={() => {
              addStockPhotos(collection.id, 4, activeSetId)
              notify('Sample photos added')
              setModal(null)
            }}
          >
            Samples
          </button>
        </div>
        <div
          className="drop-zone"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault()
            void uploadFiles(e.dataTransfer.files)
          }}
        >
          <Upload size={34} />
          <strong>Drag photos here to upload</strong>
          <AppButton loading={uploading} onClick={() => fileRef.current?.click()}>
            My Computer
          </AppButton>
        </div>
      </Modal>

      {modal === 'share-email' && (
        <ShareCollectionOverlay
          collection={collection}
          coverSrc={cover}
          publicUrl={publicUrl}
          brandName={state.homepage.brandName}
          initialMode={shareInitialMode}
          onClose={() => setModal(null)}
          onGetDirectLink={() => setModal('direct-link')}
        />
      )}

      <Modal open={modal === 'qr'} title="QR CODE" onClose={() => setModal(null)}>
        <div className="qr-card compact">
          <img
            src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(publicUrl)}`}
            alt="Gallery QR code"
          />
          <p>{publicUrl}</p>
          <AppButton
            onClick={async () => {
              await navigator.clipboard.writeText(publicUrl)
              notify('Direct link copied')
            }}
          >
            Copy link
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'email-history'} title="EMAIL HISTORY" onClose={() => setModal(null)} wide>
        {state.emailHistory?.filter((e) => e.collectionId === collection.id).length === 0 ? (
          <p className="confirm-copy">No emails sent for this collection yet.</p>
        ) : (
          <div className="list-table">
            {(state.emailHistory ?? [])
              .filter((e) => e.collectionId === collection.id)
              .map((item) => (
                <div key={item.id} className="list-row">
                  <div>
                    <strong>{item.to}</strong>
                    <p>{item.subject}</p>
                    <small>
                      {new Date(item.sentAt).toLocaleString()}
                      {item.scheduledFor
                        ? ` · scheduled ${new Date(item.scheduledFor).toLocaleString()}`
                        : ''}
                    </small>
                  </div>
                  <span className={`status-chip ${item.status}`}>{item.status}</span>
                </div>
              ))}
          </div>
        )}
        <div className="modal-actions">
          <AppButton
            onClick={() => {
              setModal('share-email')
              setShareInitialMode('email')
            }}
          >
            Share by email
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'presets'} title="MANAGE PRESETS" onClose={() => setModal(null)}>
        <div className="list-table">
          {state.presets.map((preset) => (
            <div key={preset.id} className="list-row">
              <div>
                <strong>{preset.name}</strong>
                <p>{preset.coverLayout} layout</p>
              </div>
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  applyPreset(collection.id, preset.id)
                  notify(`Preset “${preset.name}” applied`)
                  setTab('design')
                  setModal(null)
                }}
              >
                Apply
              </button>
            </div>
          ))}
        </div>
        <div className="modal-actions">
          <AppButton
            onClick={() => {
              setStyleName(`${collection.name} Style`)
              setModal('create-style')
            }}
          >
            Create Style
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'move-collection'} title="MOVE TO" onClose={() => setModal(null)}>
        <p className="confirm-copy">Organize this collection into a folder (demo labels).</p>
        <div className="form-fields">
          {['Client Galleries', 'Archives', 'Weddings', 'Portraits'].map((folder) => (
            <button
              key={folder}
              type="button"
              className={`list-choice ${moveFolder === folder ? 'selected' : ''}`}
              onClick={() => setMoveFolder(folder)}
            >
              {folder}
            </button>
          ))}
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setModal(null)}>
            Cancel
          </button>
          <AppButton
            onClick={() => {
              updateCollection(collection.id, {
                categoryTags: Array.from(
                  new Set([...(collection.categoryTags || []), moveFolder]),
                ),
              })
              notify(`Moved to ${moveFolder}`)
              setModal(null)
            }}
          >
            Move
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'create-style'} title="CREATE STYLE" onClose={() => setModal(null)}>
        <div className="form-fields">
          <label>
            Style name
            <input value={styleName} onChange={(e) => setStyleName(e.target.value)} />
          </label>
          <p className="help-text">
            Saves the current cover layout ({collection.coverLayout}) as a reusable preset.
          </p>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setModal(null)}>
            Cancel
          </button>
          <AppButton
            onClick={() => {
              if (!styleName.trim()) {
                notify('Style name is required', 'error')
                return
              }
              savePreset(styleName.trim(), collection.coverLayout || 'center')
              notify('Style saved to presets')
              setModal(null)
            }}
          >
            Save style
          </AppButton>
        </div>
      </Modal>

      <GetDirectLinkModal
        open={modal === 'direct-link'}
        onClose={() => setModal(null)}
        publicUrl={publicUrl}
        collection={collection}
        onOpenDownloadSettings={() => {
          setModal(null)
          setTab('settings')
          setSettingsSection('download')
        }}
      />

      <Modal open={modal === 'edit-set'} title="EDIT PHOTO SET" onClose={() => setModal(null)}>
        <div className="form-fields">
          <label>
            Photo Set Name
            <input value={setName} onChange={(e) => setSetName(e.target.value)} />
          </label>
          <label>
            Description
            <textarea
              value={setDescription}
              maxLength={500}
              rows={5}
              placeholder="Optional"
              onChange={(e) => setSetDescription(e.target.value)}
            />
            <small className="char-count">{setDescription.length} / 500</small>
          </label>
          <p className="help-text">
            Description is shown to clients viewing this photo set for additional storytelling.
          </p>
        </div>
        <div className="modal-actions">
          <button type="button" className="text-button" onClick={() => setModal(null)}>
            Cancel
          </button>
          <AppButton
            onClick={() => {
              if (!editingSetId || !setName.trim()) {
                notify('Set name is required', 'error')
                return
              }
              updateSet(collection.id, editingSetId, {
                name: setName.trim(),
                description: setDescription.slice(0, 500),
              })
              notify('Photo set saved')
              setModal(null)
            }}
          >
            Save
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'rename-photo'} title="RENAME PHOTO" onClose={() => setModal(null)}>
        <div className="form-fields">
          <label>
            Filename
            <input value={photoNameDraft} onChange={(e) => setPhotoNameDraft(e.target.value)} />
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setModal(null)}>
            Cancel
          </button>
          <AppButton
            onClick={() => {
              if (!renamePhotoId || !photoNameDraft.trim()) return
              updatePhoto(renamePhotoId, { name: photoNameDraft.trim() })
              notify('Photo renamed')
              setModal(null)
            }}
          >
            Save
          </AppButton>
        </div>
      </Modal>

      <Modal open={modal === 'move-photo'} title="MOVE / COPY" onClose={() => setModal(null)}>
        <p className="confirm-copy">Choose a destination set for {movePhotoIds.length} photo(s).</p>
        <div className="form-fields">
          {collection.sets.map((set) => (
            <button
              key={set.id}
              type="button"
              className="list-choice"
              onClick={() => {
                movePhotosToSet(collection.id, movePhotoIds, set.id)
                notify(`Moved to ${set.name}`)
                setSelected([])
                setModal(null)
              }}
            >
              {set.name} ({set.photoIds.length})
            </button>
          ))}
        </div>
      </Modal>

      <Modal open={modal === 'focal'} title="FOCAL POINT" onClose={() => setModal(null)}>
        <p className="confirm-copy">Click the image to set the focal point used by cover layouts.</p>
        <button
          type="button"
          className="focal-canvas"
          style={cover ? { backgroundImage: `url(${cover})` } : undefined}
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect()
            const x = Math.round(((e.clientX - rect.left) / rect.width) * 100)
            const y = Math.round(((e.clientY - rect.top) / rect.height) * 100)
            updateCollection(collection.id, { coverFocal: { x, y } })
            notify(`Focal set to ${x}% / ${y}%`)
          }}
        >
          <span
            className="focal-dot"
            style={{ left: `${collection.coverFocal?.x ?? 50}%`, top: `${collection.coverFocal?.y ?? 50}%` }}
          />
        </button>
        <div className="modal-actions">
          <AppButton onClick={() => setModal(null)}>Done</AppButton>
        </div>
      </Modal>

      {lightbox !== null && photos[lightbox] && (
        <div className="lightbox" onClick={() => setLightbox(null)}>
          <img src={photos[lightbox].src} alt={photos[lightbox].name} onClick={(e) => e.stopPropagation()} />
        </div>
      )}

      <ConfirmDialog
        open={Boolean(confirmDeleteSet)}
        title="Delete set"
        message="Delete this photo set? Photos remain in your library."
        confirmLabel="Delete"
        danger
        onCancel={() => setConfirmDeleteSet(null)}
        onConfirm={() => {
          if (!confirmDeleteSet) return
          if (collection.sets.length <= 1) {
            notify('Keep at least one set.', 'error')
            setConfirmDeleteSet(null)
            return
          }
          deleteSet(collection.id, confirmDeleteSet)
          if (activeSetId === confirmDeleteSet) {
            setActiveSetId(collection.sets.find((s) => s.id !== confirmDeleteSet)?.id)
          }
          notify('Set deleted')
          setConfirmDeleteSet(null)
        }}
      />

      <ConfirmDialog
        open={confirmDeleteCollection}
        title="Delete collection"
        message="Delete this collection? Photos remain in your library."
        confirmLabel="Delete"
        danger
        onCancel={() => setConfirmDeleteCollection(false)}
        onConfirm={() => {
          deleteCollection(collection.id)
          notify('Collection deleted')
          router.push('/collections')
        }}
      />

      <button
        type="button"
        className="chat"
        aria-label="Support chat"
        onClick={() => notify('Support chat opened', 'info')}
      >
        <span />
      </button>
    </div>
  )
}
