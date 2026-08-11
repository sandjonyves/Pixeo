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
          <b>Client Gallery</b>
        </div>
        <div className="landing-actions">
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
        <p className="eyebrow">FOR PHOTOGRAPHERS</p>
        <h1>Client galleries that feel effortless</h1>
        <p>
          Upload, organize, and share polished photo collections with a branded client
          experience — built for delivery day.
        </p>
        <div className="landing-cta">
          <Link href={isAuthenticated ? '/collections' : '/register'} className="primary-button">
            {isAuthenticated ? 'Go to collections' : 'Start free'}
          </Link>
          <Link href="/site" className="outline-button">
            View sample homepage
          </Link>
        </div>
      </section>
    </div>
  )
}
