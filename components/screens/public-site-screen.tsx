'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import { useGallery } from '@/lib/gallery-context'
import { AppButton } from '@/components/app-button'
import { formatDateLabel } from '@/lib/seed'

export function PublicSiteScreen() {
  const { ready, state, getCoverSrc } = useGallery()
  const [unlocked, setUnlocked] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

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
        <p>This photographer has turned off their public homepage.</p>
        <Link href="/login" className="primary-button">
          Photographer login
        </Link>
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
          <h1>{state.homepage.brandName}</h1>
          <p>Enter the homepage password to continue.</p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          {error && <p className="form-error">{error}</p>}
          <AppButton type="submit">Unlock</AppButton>
        </form>
      </div>
    )
  }

  return (
    <div className="public-shell">
      <header className="public-header">
        <b>{state.homepage.brandName}</b>
        <p>{state.homepage.biography}</p>
      </header>
      <div className="public-grid">
        {collections.length === 0 ? (
          <p className="public-empty">No published collections on the homepage yet.</p>
        ) : (
          collections.map((collection) => {
            const cover = getCoverSrc(collection)
            return (
              <Link key={collection.id} href={`/c/${collection.slug}`} className="public-card">
                {cover ? <img src={cover} alt={collection.name} /> : <div className="collection-cover-empty" />}
                <h2>{collection.name}</h2>
                <p>{formatDateLabel(collection.eventDate)}</p>
              </Link>
            )
          })
        )}
      </div>
    </div>
  )
}
