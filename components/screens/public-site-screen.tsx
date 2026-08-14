'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import { FolderOpen } from 'lucide-react'
import { useGallery } from '@/lib/gallery-context'
import { AppButton } from '@/components/app-button'
import { PublicPixeoFooter } from '@/components/public-pixeo-footer'
import { formatDateLabel } from '@/lib/seed'

function photographerPlanId(state: ReturnType<typeof useGallery>['state']) {
  if (state.user?.planId) return state.user.planId
  const owner = state.accounts.find((a) => a.role === 'photographer')
  return owner?.planId ?? 'free'
}

export function PublicSiteScreen() {
  const { ready, state, getCoverSrc } = useGallery()
  const [unlocked, setUnlocked] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const ownerPlanId = photographerPlanId(state)
  const showWatermarkBanner =
    ownerPlanId === 'free' || state.branding.watermarkEnabled

  const collections = useMemo(
    () =>
      state.collections.filter(
        (c) => c.showOnHomepage && c.status === 'published' && state.homepage.enabled,
      ),
    [state.collections, state.homepage.enabled],
  )

  if (!ready) return <div className="public-shell">Loading…</div>

  if (!state.homepage.enabled) {
    return (
      <div className="public-shell centered">
        <h1>Homepage is offline</h1>
        <p>
          This Pixeo homepage is currently turned off. If you are the photographer, sign in to
          re-enable it.
        </p>
        <Link href="/login" className="primary-button">
          Photographer login
        </Link>
        <PublicPixeoFooter />
      </div>
    )
  }

  if (state.homepage.password && !unlocked) {
    const submit = (e: FormEvent) => {
      e.preventDefault()
      if (password === state.homepage.password) {
        setUnlocked(true)
        setError('')
      } else {
        setError('Incorrect password')
      }
    }
    return (
      <div className="public-shell centered">
        <form className="auth-card" onSubmit={submit}>
          <h1>{state.homepage.brandName || 'Pixeo'}</h1>
          <p>Enter the homepage password to view collections on Pixeo.</p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          {error && <p className="form-error">{error}</p>}
          <AppButton type="submit">Unlock</AppButton>
        </form>
        <PublicPixeoFooter showWatermarkBanner={showWatermarkBanner} />
      </div>
    )
  }

  return (
    <div className="public-shell">
      <header className="public-header">
        <b>{state.homepage.brandName || 'Pixeo'}</b>
        <p>{state.homepage.biography || 'Client galleries powered by Pixeo.'}</p>
      </header>
      <div className="public-grid">
        {collections.length === 0 ? (
          <div className="public-empty-state">
            <FolderOpen size={40} strokeWidth={1.25} />
            <h2>No galleries published yet</h2>
            <p>
              {state.homepage.brandName || 'This studio'} has not shared any collections on their
              Pixeo homepage. New galleries will appear here when published.
            </p>
          </div>
        ) : (
          collections.map((collection) => {
            const cover = getCoverSrc(collection)
            return (
              <Link key={collection.id} href={`/c/${collection.slug}`} className="public-card">
                {cover ? (
                  <img src={cover} alt={collection.name} />
                ) : (
                  <div className="collection-cover-empty" />
                )}
                <h2>{collection.name}</h2>
                <p>{formatDateLabel(collection.eventDate)}</p>
              </Link>
            )
          })
        )}
      </div>
      <PublicPixeoFooter showWatermarkBanner={showWatermarkBanner} />
    </div>
  )
}
