'use client'

import Link from 'next/link'
import { useGallery } from '@/lib/gallery-context'

export function LandingScreen() {
  const { isAuthenticated } = useGallery()

  return (
    <div className="landing-shell">
      <header className="landing-nav">
        <div className="brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo</b>
        </div>
        <div className="landing-actions">
          <Link href="/pricing" className="text-button">
            Pricing
          </Link>
          {isAuthenticated ? (
            <Link href="/collections" className="primary-button">
              Open dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" className="text-button">
                Sign in
              </Link>
              <Link href="/register" className="primary-button">
                Get started
              </Link>
            </>
          )}
        </div>
      </header>

      <section className="landing-hero">
        <p className="eyebrow">PIXEO FOR PHOTOGRAPHERS</p>
        <h1>Client galleries that feel effortless</h1>
        <p>
          Upload, organize, and share polished photo collections with a branded client
          experience — built for delivery day. Simple plans in FCFA, no surprises.
        </p>
        <div className="landing-cta">
          <Link href={isAuthenticated ? '/collections' : '/register'} className="primary-button">
            {isAuthenticated ? 'Go to collections' : 'Start free'}
          </Link>
          <Link href="/pricing" className="outline-button">
            View pricing
          </Link>
          <Link href="/site" className="text-button">
            Sample homepage
          </Link>
        </div>
      </section>

      <section className="landing-features">
        <article>
          <h3>Deliver with confidence</h3>
          <p>Password-protected galleries, HD downloads, and client favorites — all in one place.</p>
        </article>
        <article>
          <h3>Grow on your terms</h3>
          <p>Start free, upgrade when you need more storage or unlimited galleries.</p>
        </article>
        <article>
          <h3>Built for West Africa</h3>
          <p>Transparent FCFA pricing and workflows tuned for professional photographers.</p>
        </article>
      </section>
    </div>
  )
}
