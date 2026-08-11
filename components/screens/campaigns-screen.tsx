'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Mail, Zap } from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { ConfirmDialog, Modal } from '@/components/modal'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import type { Campaign } from '@/lib/types'

export function CampaignsScreen() {
  const { state, createCampaign, updateCampaign, deleteCampaign } = useGallery()
  const { notify } = useToast()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Campaign | null>(null)
  const [name, setName] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const openCreate = () => {
    setEditing(null)
    setName('')
    setSubject('')
    setBody('')
    setOpen(true)
  }

  const openEdit = (campaign: Campaign) => {
    setEditing(campaign)
    setName(campaign.name)
    setSubject(campaign.subject)
    setBody(campaign.body)
    setOpen(true)
  }

  const save = async () => {
    if (!name.trim() || !subject.trim()) {
      notify('Name and subject are required.', 'error')
      return
    }
    setSaving(true)
    await new Promise((r) => setTimeout(r, 350))
    if (editing) {
      updateCampaign(editing.id, { name, subject, body })
      notify('Campaign updated')
    } else {
      createCampaign({ name, subject, body })
      notify('Campaign draft created')
    }
    setSaving(false)
    setOpen(false)
  }

  const send = async (campaign: Campaign) => {
    if (state.contacts.filter((c) => c.optedIn).length === 0) {
      notify('Add opted-in contacts before sending.', 'error')
      return
    }
    updateCampaign(campaign.id, { status: 'sent' })
    notify(`Campaign “${campaign.name}” marked as sent`)
  }

  return (
    <>
      <div className="page-heading">
        <h1>Email Campaigns</h1>
        <AppButton onClick={openCreate}>New Campaign</AppButton>
      </div>

      <div className="upgrade-pill">
        <Zap size={16} /> DEMO SEND
      </div>

      {state.campaigns.length === 0 ? (
        <div className="campaign-empty">
          <Mail size={90} strokeWidth={1} />
          <h2>Create your first email campaign</h2>
          <p>
            Power up your marketing with email campaigns to opted-in contacts.{' '}
            <Link href="/contacts">
              <b>Manage contacts.</b>
            </Link>
          </p>
          <AppButton onClick={openCreate}>New Campaign</AppButton>
        </div>
      ) : (
        <div className="list-table">
          {state.campaigns.map((campaign) => (
            <div key={campaign.id} className="list-row">
              <div>
                <strong>{campaign.name}</strong>
                <p>{campaign.subject || 'No subject'}</p>
              </div>
              <span className={`status-chip ${campaign.status}`}>{campaign.status}</span>
              <div className="row-actions">
                <button type="button" className="text-button" onClick={() => openEdit(campaign)}>
                  Edit
                </button>
                {campaign.status === 'draft' && (
                  <button type="button" className="text-button" onClick={() => send(campaign)}>
                    Send
                  </button>
                )}
                <button type="button" className="text-button" onClick={() => setDeleteId(campaign.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={open} title={editing ? 'EDIT CAMPAIGN' : 'NEW CAMPAIGN'} onClose={() => setOpen(false)} wide>
        <div className="form-fields">
          <label>
            Campaign name
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label>
            Subject
            <input value={subject} onChange={(e) => setSubject(e.target.value)} />
          </label>
          <label>
            Body
            <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={6} />
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="outline-button" onClick={() => setOpen(false)}>
            Cancel
          </button>
          <AppButton loading={saving} onClick={save}>
            Save draft
          </AppButton>
        </div>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete campaign"
        message="This campaign draft will be permanently removed."
        confirmLabel="Delete"
        danger
        onCancel={() => setDeleteId(null)}
        onConfirm={() => {
          if (deleteId) deleteCampaign(deleteId)
          notify('Campaign deleted')
          setDeleteId(null)
        }}
      />
    </>
  )
}
