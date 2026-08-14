'use client'

import Link from 'next/link'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, formatFcfa, getPlan, type PlanId } from '@/lib/plans'
import { useToast } from '@/components/toast-provider'

export function AdminPhotographerDetailScreen({ accountId }: { accountId: string }) {
  const { state, updateAccount } = useGallery()
  const { notify } = useToast()
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const account = state.accounts.find((a) => a.id === accountId)

  if (!account) {
    return (
      <>
        <h1>Photographer not found</h1>
        <Link href="/admin/photographers" className="text-button">
          ← Back to photographers
        </Link>
      </>
    )
  }

  const plan = getPlan(account.planId, plans)
  const galleryCount = state.collections.length

  return (
    <>
      <p className="breadcrumb">
        <Link href="/admin/photographers">Photographers</Link> / {account.name}
      </p>
      <h1>{account.name}</h1>

      <div className="detail-grid">
        <section className="billing-card">
          <h2>Account</h2>
          <dl className="detail-list">
            <div>
              <dt>Email</dt>
              <dd>{account.email}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd>{account.role}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>
                <span className={`status-pill ${account.status}`}>{account.status}</span>
              </dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{new Date(account.createdAt).toLocaleDateString('fr-FR')}</dd>
            </div>
          </dl>
        </section>

        <section className="billing-card">
          <h2>Subscription</h2>
          <p className="billing-plan-name">{plan.name}</p>
          <p className="billing-plan-price">{formatFcfa(plan.priceMonthlyFcfa)}</p>
          <label className="stacked-label">
            Change plan
            <select
              value={account.planId}
              onChange={(e) => {
                updateAccount(account.id, { planId: e.target.value as PlanId })
                notify('Plan updated')
              }}
            >
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        </section>

        <section className="billing-card">
          <h2>Usage (mock)</h2>
          <p>{galleryCount} collections on platform demo data</p>
          <p>Storage limit: {(plan.storageLimitBytes / (1024 ** 3)).toFixed(0)} GB</p>
        </section>
      </div>

      <div className="modal-actions left">
        <button
          type="button"
          className={account.status === 'active' ? 'danger-button' : 'primary-button'}
          onClick={() => {
            const next = account.status === 'active' ? 'suspended' : 'active'
            updateAccount(account.id, { status: next })
            notify(`Account ${next}`)
          }}
        >
          {account.status === 'active' ? 'Suspend account' : 'Activate account'}
        </button>
        <Link href="/admin/photographers" className="outline-button">
          Back to list
        </Link>
      </div>
    </>
  )
}
