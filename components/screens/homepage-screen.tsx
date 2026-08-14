'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Copy } from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function HomepageScreen() {
  const { state, updateHomepage, getCoverSrc } = useGallery()
  const { notify } = useToast()
  const [bio, setBio] = useState(state.homepage.biography)
  const [password, setPassword] = useState(state.homepage.password)
  const [saving, setSaving] = useState(false)

  const siteUrl =
    typeof window !== 'undefined'
      ? `${window.location.origin}/site`
      : `https://${state.branding.username}.pixeo.app`

  const listed = state.collections.filter((c) => c.showOnHomepage && c.status === 'published')

  const save = async () => {
    setSaving(true)
    await new Promise((r) => setTimeout(r, 300))
    updateHomepage({ biography: bio, password })
    setSaving(false)
    notify('Homepage settings saved')
  }

  return (
    <>
      <div className="page-heading">
        <h1>Homepage</h1>
        <div className="heading-actions">
          <AppButton secondary onClick={save} loading={saving}>
            Save
          </AppButton>
          <Link href="/site" target="_blank" className="primary-button">
            View Site
          </Link>
        </div>
      </div>

      <div className="homepage-layout">
        <div className="form-stack">
          <h3>Homepage Status</h3>
          <button
            type="button"
            className="toggle-row"
            onClick={() => {
              updateHomepage({ enabled: !state.homepage.enabled })
              notify(
                state.homepage.enabled ? 'Homepage turned off' : 'Homepage turned on',
              )
            }}
          >
            <span className={`toggle ${state.homepage.enabled ? 'on' : 'off'}`}>
              <i />
            </span>
            {state.homepage.enabled ? 'On' : 'Off'}
          </button>
          <p>
            Your Homepage is a public page where your collections are listed. You can also select
            which collections will be shown here under each collection’s setting.{' '}
            <Link href="/collections">
              <b>Manage collections</b>
            </Link>
          </p>

          <h3>Homepage URL</h3>
          <div className="field read">
            {siteUrl}
            <button
              type="button"
              className="field-action"
              onClick={async () => {
                await navigator.clipboard.writeText(siteUrl)
                notify('Homepage URL copied')
              }}
            >
              <Copy size={18} />
              <b>Copy</b>
            </button>
          </div>

          <h3>Homepage Password</h3>
          <div className="field">
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Add a password"
            />
            <button
              type="button"
              className="field-action"
              onClick={() => {
                const generated = Math.random().toString(36).slice(2, 10)
                setPassword(generated)
                notify('Password generated — click Save to apply', 'info')
              }}
            >
              ↻ Generate
            </button>
          </div>
          <p>Protect your Homepage with a password</p>

          <h3>Biography</h3>
          <textarea
            className="bio"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Tell clients about your work"
          />
        </div>

        <div className="site-preview">
          <div className="preview-window">
            <b>{state.homepage.brandName || 'Pixeo'}</b>
            <p className="preview-bio">{bio || 'Your biography will appear here.'}</p>
            <div className="preview-squares">
              {listed.slice(0, 6).map((collection) => {
                const cover = getCoverSrc(collection)
                return cover ? (
                  <img key={collection.id} src={cover} alt={collection.name} />
                ) : (
                  <span key={collection.id} />
                )
              })}
              {listed.length === 0 &&
                [1, 2, 3, 4, 5, 6].map((i) => <span key={i} />)}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
