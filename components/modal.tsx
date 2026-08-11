'use client'

import { X } from 'lucide-react'

type ModalProps = {
  open: boolean
  title?: string
  onClose: () => void
  children: React.ReactNode
  wide?: boolean
  className?: string
}

export function Modal({ open, title, onClose, children, wide, className }: ModalProps) {
  if (!open) return null

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className={`edit-modal ${wide ? 'wide' : ''} ${className ?? ''}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        {title && (
          <div className="modal-title">
            <span>{title}</span>
            <button type="button" aria-label="Close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        )}
        {children}
      </div>
    </div>
  )
}

type ConfirmProps = {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  danger,
  loading,
  onConfirm,
  onCancel,
}: ConfirmProps) {
  return (
    <Modal open={open} title={title} onClose={onCancel}>
      <p className="confirm-copy">{message}</p>
      <div className="modal-actions">
        <button type="button" className="outline-button" onClick={onCancel} disabled={loading}>
          Cancel
        </button>
        <button
          type="button"
          className={danger ? 'danger-button' : 'primary-button'}
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? 'Please wait…' : confirmLabel}
        </button>
      </div>
    </Modal>
  )
}
