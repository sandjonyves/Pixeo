'use client'

import Link from 'next/link'

type PublicPixeoFooterProps = {
  /** Show prominent free-tier watermark banner above the footer link */
  showWatermarkBanner?: boolean
}

export function PublicPixeoFooter({ showWatermarkBanner = false }: PublicPixeoFooterProps) {
  return (
    <footer className="public-pixeo-footer">
      {showWatermarkBanner && (
        <p className="public-watermark-banner">
          Galerie hébergée sur Pixeo — le filigrane disparaît avec un plan payant.
        </p>
      )}
      <Link href="/" className="public-pixeo-link">
        Powered by Pixeo
      </Link>
    </footer>
  )
}
