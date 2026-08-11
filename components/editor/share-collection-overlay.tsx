'use client'

import { useMemo, useState } from 'react'
import {
  Calendar,
  FileText,
  History,
  Link2,
  Mail,
  Palette,
  QrCode,
  X,
} from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import type { Collection } from '@/lib/types'

const TEMPLATES = [
  {
    id: 'ready',
    label: 'Photos are ready',
    subject: (name: string) => `Photos for ${name} are ready`,
    body: (name: string) =>
      `Hi!\n\nYour photos for ${name} are ready to view. Click the button below to open your private gallery.\n\nWarmly`,
  },
  {
    id: 'reminder',
    label: 'Friendly reminder',
    subject: (name: string) => `Reminder: ${name} gallery`,
    body: (name: string) =>
      `Just a quick reminder that your ${name} gallery is waiting for you. Favorites and downloads are available inside.`,
  },
  {
    id: 'thanks',
    label: 'Thank you',
    subject: (name: string) => `Thank you — ${name}`,
    body: () =>
      `Thank you again for trusting us. We hope you love the gallery as much as we loved creating it.`,
  },
]

type ShareCollectionOverlayProps = {
  collection: Collection
  coverSrc?: string
  publicUrl: string
  brandName: string
  onClose: () => void
  onGetDirectLink?: () => void
  initialMode?: 'email' | 'link' | 'qr'
}

export function ShareCollectionOverlay({
  collection,
  coverSrc,
  publicUrl,
  brandName,
  onClose,
  onGetDirectLink,
  initialMode = 'email',
}: ShareCollectionOverlayProps) {
  const { state, recordEmailShare, updateCollection } = useGallery()
  const { notify } = useToast()
  const [moreOpen, setMoreOpen] = useState(false)
  const [sendMenuOpen, setSendMenuOpen] = useState(false)
  const [showQr, setShowQr] = useState(initialMode === 'qr')
  const [to, setTo] = useState(state.contacts[0]?.email || 'guest@email.com')
  const [subject, setSubject] = useState(`Photos for ${collection.name} are ready`)
  const [body, setBody] = useState('')
  const [includeDownload, setIncludeDownload] = useState(true)
  const [includePin, setIncludePin] = useState(Boolean(collection.password))
  const [sending, setSending] = useState(false)
  const [scheduleAt, setScheduleAt] = useState('')
  const [showCustomSchedule, setShowCustomSchedule] = useState(false)
  const [showTemplates, setShowTemplates] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const history = useMemo(
    () => (state.emailHistory ?? []).filter((e) => e.collectionId === collection.id),
    [state.emailHistory, collection.id],
  )

  const qrSrc = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(publicUrl)}`

  const tomorrowLabel = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    d.setHours(9, 0, 0, 0)
    const offset = -d.getTimezoneOffset() / 60
    const sign = offset >= 0 ? '+' : '-'
    return {
      iso: d.toISOString(),
      label: `Tomorrow at 9:00am GMT${sign}${Math.abs(offset)}`,
    }
  }, [])

  const copyLink = async () => {
    if (onGetDirectLink) {
      onGetDirectLink()
      return
    }
    await navigator.clipboard.writeText(publicUrl)
    notify('Direct link copied')
  }

  const sendEmail = async (scheduledFor?: string) => {
    if (!to.includes('@')) {
      notify('Enter a valid recipient email.', 'error')
      return
    }
    if (!subject.trim()) {
      notify('Subject is required.', 'error')
      return
    }
    setSending(true)
    await new Promise((r) => setTimeout(r, 450))
    if (includePin && !collection.password) {
      const pin = Math.random().toString().slice(2, 6)
      updateCollection(collection.id, { password: pin })
    }
    recordEmailShare({
      collectionId: collection.id,
      collectionName: collection.name,
      to: to.trim(),
      subject: subject.trim(),
      body,
      includeDownload,
      includePin,
      status: scheduledFor ? 'scheduled' : 'sent',
      scheduledFor,
    })
    setSending(false)
    notify(scheduledFor ? 'Email scheduled' : `Email sent to ${to.trim()}`)
    if (!scheduledFor) onClose()
  }

  return (
    <div className="share-overlay">
      <header className="share-overlay-top">
        <button type="button" className="icon-btn" aria-label="Close" onClick={onClose}>
          <X size={22} />
        </button>
        <h1>Share Collection</h1>
        <div className="share-overlay-actions">
          <div className="menu-anchor">
            <button type="button" onClick={() => setMoreOpen((v) => !v)}>
              More⌄
            </button>
            {moreOpen && (
              <div className="dropdown-panel">
                <button
                  type="button"
                  onClick={() => {
                    setShowQr(true)
                    setMoreOpen(false)
                  }}
                >
                  <QrCode size={16} /> Get QR code
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowHistory(true)
                    setMoreOpen(false)
                  }}
                >
                  <History size={16} /> View email history
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMoreOpen(false)
                    notify('Open Design → Cover to choose a theme', 'info')
                    onClose()
                  }}
                >
                  <Palette size={16} /> Choose theme
                </button>
              </div>
            )}
          </div>
          <button type="button" className="text-button teal" onClick={() => void copyLink()}>
            Get direct link
          </button>
        </div>
      </header>

      <div className="share-overlay-body">
        <section className="share-compose">
          <label className="share-to">
            <span>To:</span>
            <input
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="guest@email.com"
            />
          </label>

          <input
            className="share-subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />

          <textarea
            className="share-body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Enter your text here"
          />

          <div className="share-templates">
            <button
              type="button"
              className="linkish"
              onClick={() => setShowTemplates((v) => !v)}
            >
              <FileText size={16} /> Insert Email Template
            </button>
            {showTemplates && (
              <div className="template-list">
                {TEMPLATES.map((tpl) => (
                  <button
                    key={tpl.id}
                    type="button"
                    onClick={() => {
                      setSubject(tpl.subject(collection.name))
                      setBody(tpl.body(collection.name))
                      setShowTemplates(false)
                      notify(`Template “${tpl.label}” inserted`)
                    }}
                  >
                    {tpl.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="share-footer-row">
            <div>
              <p className="include-label">Include collection info:</p>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={includeDownload}
                  onChange={(e) => setIncludeDownload(e.target.checked)}
                />
                Download
              </label>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={includePin}
                  onChange={(e) => setIncludePin(e.target.checked)}
                />
                PIN
              </label>
            </div>

            <div className="split-send menu-anchor">
              <AppButton loading={sending} onClick={() => void sendEmail()}>
                Send
              </AppButton>
              <button
                type="button"
                className="split-chevron"
                aria-label="Schedule send"
                onClick={() => setSendMenuOpen((v) => !v)}
              >
                ⌄
              </button>
              {sendMenuOpen && (
                <div className="dropdown-panel send-schedule-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setSendMenuOpen(false)
                      void sendEmail(tomorrowLabel.iso)
                    }}
                  >
                    <Mail size={16} /> {tomorrowLabel.label}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSendMenuOpen(false)
                      setShowCustomSchedule(true)
                    }}
                  >
                    <Calendar size={16} /> Custom schedule
                  </button>
                </div>
              )}
            </div>
          </div>

          {showCustomSchedule && (
            <div className="custom-schedule">
              <label>
                Schedule date & time
                <input
                  type="datetime-local"
                  value={scheduleAt}
                  onChange={(e) => setScheduleAt(e.target.value)}
                />
              </label>
              <div className="modal-actions">
                <button type="button" className="text-button" onClick={() => setShowCustomSchedule(false)}>
                  Cancel
                </button>
                <AppButton
                  onClick={() => {
                    if (!scheduleAt) {
                      notify('Pick a date and time', 'error')
                      return
                    }
                    void sendEmail(new Date(scheduleAt).toISOString())
                    setShowCustomSchedule(false)
                  }}
                >
                  Schedule
                </AppButton>
              </div>
            </div>
          )}

          {showHistory && (
            <div className="email-history-box">
              <h3>Email history</h3>
              {history.length === 0 ? (
                <p>No emails sent for this collection yet.</p>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="history-row">
                    <div>
                      <strong>{item.to}</strong>
                      <p>{item.subject}</p>
                    </div>
                    <span className={`status-chip ${item.status}`}>{item.status}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </section>

        <aside className="share-preview">
          {showQr ? (
            <div className="qr-card">
              <h3>QR code</h3>
              <img src={qrSrc} alt="Gallery QR code" />
              <p>{publicUrl}</p>
              <button type="button" className="text-button" onClick={() => setShowQr(false)}>
                Back to email preview
              </button>
              <AppButton
                secondary
                onClick={async () => {
                  await navigator.clipboard.writeText(publicUrl)
                  notify('Link copied from QR')
                }}
              >
                <Link2 size={16} /> Copy link
              </AppButton>
            </div>
          ) : (
            <div className="email-preview-card">
              <p className="email-brand">{brandName}</p>
              <h2>{collection.name}</h2>
              {coverSrc ? (
                <img src={coverSrc} alt="" className="email-hero" />
              ) : (
                <div className="email-hero placeholder" />
              )}
              <p className="email-preview-body">
                {body || 'Your message will appear here.'}
              </p>
              <div className="email-cta">View Gallery</div>
              {(includeDownload || includePin) && (
                <p className="email-meta">
                  {includeDownload ? 'Downloads enabled' : null}
                  {includeDownload && includePin ? ' · ' : null}
                  {includePin ? `PIN: ${collection.password || 'will be generated'}` : null}
                </p>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}
