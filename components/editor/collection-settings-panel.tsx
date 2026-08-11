'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import {
  Download,
  Heart,
  Info,
  Lock,
  Plus,
  Radio,
  RefreshCw,
  ShoppingCart,
  Trash2,
  Wrench,
} from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { Modal } from '@/components/modal'
import { useGallery } from '@/lib/gallery-context'
import { slugify } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'
import type { Collection, GalleryActivity } from '@/lib/types'

export type SettingsSection = 'general' | 'privacy' | 'download' | 'favorite' | 'store'

type Props = {
  collection: Collection
  publicUrl: string
  active: SettingsSection
  onChangeSection: (section: SettingsSection) => void
  onOpenDirectLink?: () => void
}

function StatusPill({ on }: { on: boolean }) {
  return <span className={`on-off-pill ${on ? 'on' : 'off'}`}>{on ? 'ON' : 'OFF'}</span>
}

function Toggle({
  on,
  onToggle,
  label,
}: {
  on: boolean
  onToggle: () => void
  label?: string
}) {
  return (
    <button type="button" className="toggle-row" onClick={onToggle} aria-pressed={on}>
      <span className={`toggle ${on ? 'on' : 'off'}`}>
        <i />
      </span>
      {label ?? (on ? 'On' : 'Off')}
    </button>
  )
}

function ActivityList({
  items,
  empty,
}: {
  items: GalleryActivity[]
  empty: string
}) {
  if (!items.length) {
    return <p className="confirm-copy">{empty}</p>
  }
  return (
    <div className="activity-list">
      {items.map((item) => (
        <div key={item.id} className="activity-row">
          <div>
            <strong>
              {item.type === 'download'
                ? 'Download'
                : item.type === 'favorite'
                  ? 'Favorite'
                  : item.type === 'note'
                    ? 'Note'
                    : 'View'}
            </strong>
            <p>
              {item.photoName || 'Gallery'} · {item.visitorLabel}
              {item.note ? ` — “${item.note}”` : ''}
            </p>
          </div>
          <small>{new Date(item.createdAt).toLocaleString()}</small>
        </div>
      ))}
    </div>
  )
}

export function CollectionSettingsNav({
  collection,
  active,
  onChangeSection,
}: {
  collection: Collection
  active: SettingsSection
  onChangeSection: (section: SettingsSection) => void
}) {
  return (
    <div className="editor-set settings-nav">
      <small>SETTINGS</small>
      <button
        type="button"
        className={`set-row settings-nav-item ${active === 'general' ? 'active' : ''}`}
        onClick={() => onChangeSection('general')}
      >
        <Wrench size={18} />
        <span>General</span>
      </button>
      <button
        type="button"
        className={`set-row settings-nav-item ${active === 'privacy' ? 'active' : ''}`}
        onClick={() => onChangeSection('privacy')}
      >
        <Lock size={18} />
        <span>Privacy</span>
      </button>
      <button
        type="button"
        className={`set-row settings-nav-item ${active === 'download' ? 'active' : ''}`}
        onClick={() => onChangeSection('download')}
      >
        <Download size={18} />
        <span className="nav-stack">
          <b>Download</b>
          <small>
            {collection.downloadPinEnabled
              ? `PIN ${'•'.repeat(4)}`
              : 'No PIN'}
          </small>
        </span>
        <StatusPill on={collection.downloadEnabled} />
      </button>
      <button
        type="button"
        className={`set-row settings-nav-item ${active === 'favorite' ? 'active' : ''}`}
        onClick={() => onChangeSection('favorite')}
      >
        <Heart size={18} />
        <span>Favorite</span>
        <StatusPill on={collection.favoritesEnabled} />
      </button>
      <button
        type="button"
        className={`set-row settings-nav-item ${active === 'store' ? 'active' : ''}`}
        onClick={() => onChangeSection('store')}
      >
        <ShoppingCart size={18} />
        <span>Store</span>
        <StatusPill on={collection.storeEnabled} />
      </button>
    </div>
  )
}

export function CollectionSettingsPanel({
  collection,
  publicUrl,
  active,
}: Props) {
  const {
    state,
    updateCollection,
    addFavoriteList,
    deleteFavoriteList,
  } = useGallery()
  const { notify } = useToast()
  const [slugDraft, setSlugDraft] = useState(collection.slug)
  const [tagsDraft, setTagsDraft] = useState((collection.categoryTags ?? []).join(', '))
  const [passwordDraft, setPasswordDraft] = useState(collection.password || '')
  const [downloadTab, setDownloadTab] = useState<'general' | 'advanced'>('general')
  const [showExtraDownload, setShowExtraDownload] = useState(true)
  const [activityOpen, setActivityOpen] = useState<'download' | 'favorite' | null>(null)
  const [listModal, setListModal] = useState(false)
  const [listName, setListName] = useState('Must-haves')
  const [listLimit, setListLimit] = useState(20)

  useEffect(() => {
    setSlugDraft(collection.slug)
    setTagsDraft((collection.categoryTags ?? []).join(', '))
    setPasswordDraft(collection.password || '')
  }, [collection])

  const activities = useMemo(
    () =>
      (state.galleryActivities ?? []).filter((a) => a.collectionId === collection.id),
    [state.galleryActivities, collection.id],
  )
  const downloadActivities = activities.filter((a) => a.type === 'download')
  const favoriteActivities = activities.filter(
    (a) => a.type === 'favorite' || a.type === 'note',
  )

  const resetPin = () => {
    const pin = Math.random().toString().slice(2, 6)
    updateCollection(collection.id, { downloadPin: pin, downloadPinEnabled: true })
    notify('Download PIN reset')
  }

  const savePassword = (value: string) => {
    updateCollection(collection.id, { password: value.trim() })
    notify(value.trim() ? 'Password saved' : 'Password cleared')
  }

  return (
    <section className="editor-grid collection-settings">
      {active === 'general' && (
        <>
          <h1>General Settings</h1>
          <div className="settings-form editor-settings">
            <h3>Collection Contact</h3>
            <p>
              Link this collection to one or more contacts and view in Studio Manager.{' '}
              <Link href="/contacts">
                <b>Learn more</b>
              </Link>
            </p>
            <div className="chip-row">
              {(collection.contactIds ?? []).map((id) => {
                const contact = state.contacts.find((c) => c.id === id)
                if (!contact) return null
                return (
                  <button
                    key={id}
                    type="button"
                    className="chip"
                    onClick={() =>
                      updateCollection(collection.id, {
                        contactIds: collection.contactIds.filter((x) => x !== id),
                      })
                    }
                  >
                    {contact.name} ×
                  </button>
                )
              })}
            </div>
            <button
              type="button"
              className="linkish"
              onClick={() => {
                const available = state.contacts.find(
                  (c) => !collection.contactIds.includes(c.id),
                )
                if (!available) {
                  notify('Add contacts first in Marketing → Contacts', 'info')
                  return
                }
                updateCollection(collection.id, {
                  contactIds: [...collection.contactIds, available.id],
                })
                notify(`Linked ${available.name}`)
              }}
            >
              <Plus size={16} /> Add Contact
            </button>

            <h3>Collection URL</h3>
            <div className="field">
              <input
                value={slugDraft}
                onChange={(e) => setSlugDraft(slugify(e.target.value))}
              />
            </div>
            <p>
              Choose a unique url for visitors to access this collection.{' '}
              <span className="mono-url">
                {publicUrl.replace(collection.slug, slugDraft || collection.slug)}
              </span>
            </p>

            <h3>Category Tags</h3>
            <div className="field">
              <input
                value={tagsDraft}
                onChange={(e) => setTagsDraft(e.target.value)}
                placeholder="Portrait, Wedding"
              />
            </div>

            <div className="modal-actions left">
              <AppButton
                onClick={() => {
                  updateCollection(collection.id, {
                    slug: slugDraft || collection.slug,
                    categoryTags: tagsDraft
                      .split(',')
                      .map((t) => t.trim())
                      .filter(Boolean),
                    category: tagsDraft.split(',')[0]?.trim() || undefined,
                  })
                  notify('Settings saved')
                }}
              >
                Save settings
              </AppButton>
            </div>
          </div>
        </>
      )}

      {active === 'privacy' && (
        <>
          <h1>Privacy Settings</h1>
          <div className="settings-form editor-settings">
            <h3>Collection Password</h3>
            <div className="field password-field">
              <input
                value={passwordDraft}
                onChange={(e) => setPasswordDraft(e.target.value)}
                onBlur={() => {
                  if ((collection.password || '') !== passwordDraft.trim()) {
                    savePassword(passwordDraft)
                  }
                }}
                placeholder="Add a password"
              />
              <button
                type="button"
                className="field-action"
                onClick={() => {
                  const generated = Math.random().toString(36).slice(2, 10)
                  setPasswordDraft(generated)
                  savePassword(generated)
                }}
              >
                <RefreshCw size={16} /> Generate
              </button>
            </div>
            <p>Require visitors to enter this password in order to see the collection.</p>

            <h3>Show on Homepage</h3>
            <Toggle
              on={collection.showOnHomepage}
              onToggle={() => {
                updateCollection(collection.id, {
                  showOnHomepage: !collection.showOnHomepage,
                })
                notify(
                  collection.showOnHomepage
                    ? 'Hidden from homepage'
                    : 'Shown on homepage',
                )
              }}
            />
            <p>
              Show this collection on your{' '}
              <Link href="/homepage">
                <b>Homepage</b>
              </Link>
              . Manage Homepage in{' '}
              <Link href="/homepage">
                <b>Homepage settings</b>
              </Link>
              .
            </p>

            <h3>Client Exclusive Access</h3>
            <Toggle
              on={collection.clientExclusive}
              onToggle={() => {
                updateCollection(collection.id, {
                  clientExclusive: !collection.clientExclusive,
                })
                notify(
                  collection.clientExclusive
                    ? 'Client exclusive disabled'
                    : 'Client exclusive enabled — share the private link or password',
                )
              }}
            />
            <p>Only invited clients with a private link or password can access this gallery.</p>
          </div>
        </>
      )}

      {active === 'download' && (
        <>
          <div className="page-heading">
            <h1>
              Download Settings <Info size={16} className="info-inline" />
            </h1>
            <button
              type="button"
              className="activity-link"
              onClick={() => setActivityOpen('download')}
            >
              <Radio size={16} /> Download Activity
            </button>
          </div>

          <div className="tabs settings-tabs">
            <button
              type="button"
              className={downloadTab === 'general' ? 'active' : undefined}
              onClick={() => setDownloadTab('general')}
            >
              General Settings
            </button>
            <button
              type="button"
              className={downloadTab === 'advanced' ? 'active' : undefined}
              onClick={() => setDownloadTab('advanced')}
            >
              Advanced Settings
            </button>
          </div>

          <div className="settings-form editor-settings">
            {downloadTab === 'general' && (
              <>
                <h3>Photo Download</h3>
                <Toggle
                  on={collection.downloadEnabled}
                  onToggle={() => {
                    updateCollection(collection.id, {
                      downloadEnabled: !collection.downloadEnabled,
                    })
                    notify(
                      collection.downloadEnabled
                        ? 'Downloads disabled'
                        : 'Downloads enabled',
                    )
                  }}
                />
                <p>Allow visitors to download photos in your gallery.</p>
                <button
                  type="button"
                  className="linkish"
                  onClick={() => setShowExtraDownload((v) => !v)}
                >
                  Additional options {showExtraDownload ? '⌃' : '⌄'}
                </button>

                {showExtraDownload && collection.downloadEnabled && (
                  <>
                    <h3>Photo Download Sizes</h3>
                    <label className="check-row">
                      <input
                        type="checkbox"
                        checked={collection.downloadHighRes}
                        onChange={(e) =>
                          updateCollection(collection.id, {
                            downloadHighRes: e.target.checked,
                          })
                        }
                      />
                      <b>High Resolution</b>
                    </label>
                    <div
                      className={`indent-options ${collection.downloadHighRes ? '' : 'is-disabled'}`}
                    >
                      <label className="radio-row disabled">
                        <input type="radio" disabled checked={false} readOnly />
                        Original — Upgrade required.{' '}
                        <button
                          type="button"
                          className="linkish"
                          onClick={() =>
                            notify('Upgrade unlocks original-resolution downloads', 'info')
                          }
                        >
                          Upgrade
                        </button>
                      </label>
                      <label className="radio-row">
                        <input
                          type="radio"
                          name="hires"
                          disabled={!collection.downloadHighRes}
                          checked={collection.downloadHighResSize === '3600'}
                          onChange={() =>
                            updateCollection(collection.id, {
                              downloadHighResSize: '3600',
                              downloadHighRes: true,
                            })
                          }
                        />
                        3600px
                      </label>
                    </div>

                    <label className="check-row">
                      <input
                        type="checkbox"
                        checked={collection.downloadWebSize}
                        onChange={(e) =>
                          updateCollection(collection.id, {
                            downloadWebSize: e.target.checked,
                          })
                        }
                      />
                      <b>Web Size</b>
                    </label>
                    <div
                      className={`indent-options ${collection.downloadWebSize ? '' : 'is-disabled'}`}
                    >
                      {(['2048', '1024', '640'] as const).map((size) => (
                        <label key={size} className="radio-row">
                          <input
                            type="radio"
                            name="web"
                            disabled={!collection.downloadWebSize}
                            checked={collection.downloadWebSizePx === size}
                            onChange={() =>
                              updateCollection(collection.id, {
                                downloadWebSizePx: size,
                                downloadWebSize: true,
                              })
                            }
                          />
                          {size}px
                        </label>
                      ))}
                    </div>
                    <p>
                      Allow photos to be downloaded in select sizes.{' '}
                      <button
                        type="button"
                        className="linkish"
                        onClick={() => notify('Download size guide opened', 'info')}
                      >
                        Learn more
                      </button>
                    </p>
                  </>
                )}

                <h3>Download PIN</h3>
                <Toggle
                  on={collection.downloadPinEnabled}
                  onToggle={() => {
                    const next = !collection.downloadPinEnabled
                    updateCollection(collection.id, {
                      downloadPinEnabled: next,
                      downloadPin:
                        collection.downloadPin || Math.random().toString().slice(2, 6),
                    })
                    notify(next ? 'Download PIN enabled' : 'Download PIN disabled')
                  }}
                />
                {collection.downloadPinEnabled && (
                  <>
                    <div className="field read pin-field">
                      <b>{collection.downloadPin || '----'}</b>
                      <button type="button" className="field-action" onClick={resetPin}>
                        <RefreshCw size={16} /> Reset PIN
                      </button>
                    </div>
                    <p>Require visitors to enter a 4-digit PIN to download photos and videos.</p>
                  </>
                )}
              </>
            )}

            {downloadTab === 'advanced' && (
              <>
                <h3>Advanced</h3>
                <p>Limit bulk downloads and watermark embedded files for client delivery.</p>
                <Toggle
                  on={state.branding.watermarkEnabled}
                  label={
                    state.branding.watermarkEnabled
                      ? 'Watermark on downloads'
                      : 'No watermark'
                  }
                  onToggle={() =>
                    notify('Manage watermarks in Dashboard → Settings → Watermark', 'info')
                  }
                />
                <div className="modal-actions left">
                  <AppButton
                    secondary
                    onClick={() => notify('Single-photo download mode noted', 'info')}
                  >
                    Allow single photo only
                  </AppButton>
                </div>
              </>
            )}
          </div>
        </>
      )}

      {active === 'favorite' && (
        <>
          <div className="page-heading">
            <h1>
              Favorite Settings <Info size={16} className="info-inline" />
            </h1>
            <button
              type="button"
              className="activity-link"
              onClick={() => setActivityOpen('favorite')}
            >
              <Radio size={16} /> Favorite Activity
            </button>
          </div>
          <div className="settings-form editor-settings">
            <h3>Favorite Photos</h3>
            <Toggle
              on={collection.favoritesEnabled}
              onToggle={() => {
                updateCollection(collection.id, {
                  favoritesEnabled: !collection.favoritesEnabled,
                })
                notify(
                  collection.favoritesEnabled
                    ? 'Favorites disabled'
                    : 'Favorites enabled',
                )
              }}
            />
            <p>
              Allow visitors to favorite photos. You can review these afterwards in Favorite
              Activity.
            </p>

            <h3>Favorite Notes</h3>
            <Toggle
              on={collection.favoriteNotesEnabled}
              onToggle={() => {
                updateCollection(collection.id, {
                  favoriteNotesEnabled: !collection.favoriteNotesEnabled,
                })
                notify(
                  collection.favoriteNotesEnabled
                    ? 'Favorite notes disabled'
                    : 'Favorite notes enabled',
                )
              }}
            />
            <p>
              Allow clients to add notes to photos they have favorited.{' '}
              <button
                type="button"
                className="linkish"
                onClick={() =>
                  notify(
                    'Notes appear next to favorited photos in Favorite Activity.',
                    'info',
                  )
                }
              >
                Learn more
              </button>
            </p>

            <div className="favorite-promo">
              <Heart size={22} />
              <div>
                <strong>Preset Favorite Lists</strong>
                <p>
                  Create Favorite lists and set selection limits for your clients during
                  proofing.
                </p>
              </div>
              <AppButton secondary onClick={() => setListModal(true)}>
                Create list
              </AppButton>
            </div>

            {(collection.favoriteLists ?? []).length > 0 && (
              <div className="list-table" style={{ marginTop: 18 }}>
                {collection.favoriteLists.map((list) => (
                  <div key={list.id} className="list-row">
                    <div>
                      <strong>{list.name}</strong>
                      <p>Limit: {list.selectionLimit} photos</p>
                    </div>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => {
                        deleteFavoriteList(collection.id, list.id)
                        notify('Favorite list removed')
                      }}
                    >
                      <Trash2 size={16} /> Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {active === 'store' && (
        <>
          <h1>Store</h1>
          <div className="settings-form editor-settings">
            <Toggle
              on={collection.storeEnabled}
              label={collection.storeEnabled ? 'Store On' : 'Store Off'}
              onToggle={() => {
                updateCollection(collection.id, {
                  storeEnabled: !collection.storeEnabled,
                })
                notify(
                  collection.storeEnabled ? 'Store turned off' : 'Store turned on (demo)',
                )
              }}
            />
            <p>
              Sell prints and digital downloads directly from this collection. Price sheets and
              checkout are simulated in this demo.
            </p>
            <StatusPill on={collection.storeEnabled} />
            <div className="modal-actions left">
              <AppButton
                onClick={() =>
                  notify(
                    collection.storeEnabled
                      ? 'Storefront preview: clients can request prints from the gallery.'
                      : 'Enable Store to open the storefront demo.',
                    'info',
                  )
                }
              >
                {collection.storeEnabled ? 'Preview storefront' : 'Upgrade to enable Store'}
              </AppButton>
            </div>
          </div>
        </>
      )}

      <Modal
        open={activityOpen === 'download'}
        title="DOWNLOAD ACTIVITY"
        onClose={() => setActivityOpen(null)}
        wide
      >
        <ActivityList
          items={downloadActivities}
          empty="No download activity yet. When clients download photos, their events will appear here."
        />
        <div className="modal-actions">
          <AppButton onClick={() => setActivityOpen(null)}>Close</AppButton>
        </div>
      </Modal>

      <Modal
        open={activityOpen === 'favorite'}
        title="FAVORITE ACTIVITY"
        onClose={() => setActivityOpen(null)}
        wide
      >
        <ActivityList
          items={favoriteActivities}
          empty="No client favorites yet. Stars from the public gallery will appear here."
        />
        <div className="modal-actions">
          <AppButton onClick={() => setActivityOpen(null)}>Close</AppButton>
        </div>
      </Modal>

      <Modal open={listModal} title="CREATE FAVORITE LIST" onClose={() => setListModal(false)}>
        <div className="form-fields">
          <label>
            List name
            <input value={listName} onChange={(e) => setListName(e.target.value)} />
          </label>
          <label>
            Selection limit
            <input
              type="number"
              min={1}
              max={500}
              value={listLimit}
              onChange={(e) => setListLimit(Number(e.target.value) || 1)}
            />
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setListModal(false)}>
            Cancel
          </button>
          <AppButton
            onClick={() => {
              if (!listName.trim()) {
                notify('List name is required', 'error')
                return
              }
              addFavoriteList(collection.id, {
                name: listName,
                selectionLimit: listLimit,
              })
              notify('Favorite list created')
              setListModal(false)
              setListName('Must-haves')
              setListLimit(20)
            }}
          >
            Create
          </AppButton>
        </div>
      </Modal>
    </section>
  )
}

export function GetDirectLinkModal({
  open,
  onClose,
  publicUrl,
  collection,
  onOpenDownloadSettings,
}: {
  open: boolean
  onClose: () => void
  publicUrl: string
  collection: Collection
  onOpenDownloadSettings: () => void
}) {
  const { notify } = useToast()

  return (
    <Modal open={open} title="GET DIRECT LINK" onClose={onClose}>
      <div className="direct-link-modal">
        <h3>Collection URL</h3>
        <div className="field read">
          {publicUrl}
          <button
            type="button"
            className="field-action"
            onClick={async () => {
              await navigator.clipboard.writeText(publicUrl)
              notify('URL copied')
            }}
          >
            Copy
          </button>
        </div>
        <p>
          Share this unique URL for this collection with your client. You can also use your{' '}
          <Link href="/settings">
            <b>custom domain</b>
          </Link>{' '}
          if it&apos;s enabled.
        </p>

        <h3>Download PIN</h3>
        <div className="field read">
          {collection.downloadPinEnabled ? collection.downloadPin : 'Disabled'}
          <button
            type="button"
            className="field-action"
            disabled={!collection.downloadPinEnabled}
            onClick={async () => {
              await navigator.clipboard.writeText(collection.downloadPin)
              notify('PIN copied')
            }}
          >
            Copy
          </button>
        </div>
        <p>
          Share this 4-digit PIN with your client to allow them to download from the collection.
          You may turn off this functionality under{' '}
          <button type="button" className="linkish" onClick={onOpenDownloadSettings}>
            Download Settings
          </button>
          .
        </p>

        <div className="social-row">
          <a
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(publicUrl)}`}
            target="_blank"
            rel="noreferrer"
            aria-label="Share on Facebook"
          >
            f
          </a>
          <a
            href={`https://pinterest.com/pin/create/button/?url=${encodeURIComponent(publicUrl)}`}
            target="_blank"
            rel="noreferrer"
            aria-label="Share on Pinterest"
          >
            p
          </a>
          <a
            href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(publicUrl)}`}
            target="_blank"
            rel="noreferrer"
            aria-label="Share on X"
          >
            𝕏
          </a>
        </div>
      </div>
    </Modal>
  )
}
