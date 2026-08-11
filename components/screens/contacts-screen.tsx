'use client'

import { useState } from 'react'
import { Mail } from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { ConfirmDialog, Modal } from '@/components/modal'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function ContactsScreen() {
  const { state, addContact, deleteContact } = useGallery()
  const { notify } = useToast()
  const [open, setOpen] = useState(false)
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const submit = () => {
    const result = addContact({ email, name })
    if (!result.ok) {
      notify(result.error || 'Could not add contact', 'error')
      return
    }
    notify('Contact added')
    setEmail('')
    setName('')
    setOpen(false)
  }

  return (
    <>
      <div className="page-heading">
        <h1>Contacts</h1>
        <AppButton onClick={() => setOpen(true)}>Add contact</AppButton>
      </div>

      {state.contacts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-art">
            <Mail size={58} strokeWidth={1} />
          </div>
          <h2>No contacts yet</h2>
          <p>Add opted-in emails to start building your list.</p>
          <AppButton onClick={() => setOpen(true)}>Add contact</AppButton>
        </div>
      ) : (
        <div className="list-table">
          {state.contacts.map((contact) => (
            <div key={contact.id} className="list-row">
              <div>
                <strong>{contact.name}</strong>
                <p>{contact.email}</p>
              </div>
              <span className={`status-chip ${contact.optedIn ? 'published' : 'draft'}`}>
                {contact.optedIn ? 'opted-in' : 'opted-out'}
              </span>
              <div className="row-actions">
                <button type="button" className="text-button" onClick={() => setDeleteId(contact.id)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={open} title="ADD CONTACT" onClose={() => setOpen(false)}>
        <div className="form-fields">
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setOpen(false)}>
            Cancel
          </button>
          <AppButton onClick={submit}>Save</AppButton>
        </div>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Remove contact"
        message="Remove this contact from your marketing list?"
        confirmLabel="Remove"
        danger
        onCancel={() => setDeleteId(null)}
        onConfirm={() => {
          if (deleteId) deleteContact(deleteId)
          notify('Contact removed')
          setDeleteId(null)
        }}
      />
    </>
  )
}
