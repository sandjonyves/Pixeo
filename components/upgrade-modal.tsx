'use client'

import Link from 'next/link'
import { Modal } from '@/components/modal'
import { AppButton } from '@/components/app-button'

type UpgradeModalProps = {
  open: boolean
  title: string
  message: string
  onClose: () => void
  /** Where to send users who want to upgrade */
  ctaHref?: '/billing' | '/pricing'
  ctaLabel?: string
}

export function UpgradeModal({
  open,
  title,
  message,
  onClose,
  ctaHref = '/billing',
  ctaLabel = 'View plans',
}: UpgradeModalProps) {
  return (
    <Modal open={open} title={title} onClose={onClose}>
      <p className="confirm-copy">{message}</p>
      <div className="modal-actions">
        <AppButton secondary onClick={onClose}>
          Not now
        </AppButton>
        <Link href={ctaHref} className="primary-button" onClick={onClose}>
          {ctaLabel}
        </Link>
      </div>
    </Modal>
  )
}
