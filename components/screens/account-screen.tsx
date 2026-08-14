'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import { DEFAULT_PLANS, getPlan } from '@/lib/plans'

export function AccountScreen() {
  const { state, updateUser, resetDemoData } = useGallery()
  const { notify } = useToast()
  const router = useRouter()
  const [name, setName] = useState(state.user?.name ?? '')
  const [email, setEmail] = useState(state.user?.email ?? '')
  const [password, setPassword] = useState('')
  const [saving, setSaving] = useState(false)
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const currentPlan = getPlan(state.user?.planId ?? 'free', plans)

  const save = async () => {
    if (!name.trim() || !email.includes('@')) {
      notify('Enter a valid name and email.', 'error')
      return
    }
    setSaving(true)
    await new Promise((r) => setTimeout(r, 300))
    updateUser({
      name: name.trim(),
      email: email.trim().toLowerCase(),
      initials: name.trim().slice(0, 1).toUpperCase(),
      ...(password ? { password } : {}),
    })
    setPassword('')
    setSaving(false)
    notify('Account updated')
  }

  return (
    <>
      <h1>Account</h1>
      <div className="settings-form">
        <label className="stacked-label">
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label className="stacked-label">
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
        </label>
        <label className="stacked-label">
          New password
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="Leave blank to keep current"
          />
        </label>
        <div className="account-plan-summary">
          <h3>Subscription</h3>
          <p>
            Current plan: <b>{currentPlan.name}</b>
          </p>
          <Link href="/billing" className="text-button">
            Manage billing & upgrades →
          </Link>
        </div>
        <div className="modal-actions left">
          <AppButton loading={saving} onClick={save}>
            Save account
          </AppButton>
          <Link href="/settings" className="outline-button">
            Branding settings
          </Link>
          <Link href="/billing" className="outline-button">
            Billing
          </Link>
        </div>
        <hr className="divider" />
        <AppButton
          secondary
          onClick={() => {
            resetDemoData()
            notify('Demo data restored')
            router.push('/collections')
          }}
        >
          Restore Yves demo collection
        </AppButton>
      </div>
    </>
  )
}
