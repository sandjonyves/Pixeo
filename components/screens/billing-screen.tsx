'use client'

import Link from 'next/link'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import {
  DEFAULT_PLANS,
  effectiveGalleryLimit,
  formatFcfa,
  getPlan,
  type PlanId,
} from '@/lib/plans'
import { formatBytes } from '@/lib/seed'
import { useToast } from '@/components/toast-provider'

export function BillingScreen() {
  const { state, usedStorageBytes, changePlan } = useGallery()
  const { notify } = useToast()
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const planId = state.user?.planId ?? 'free'
  const currentPlan = getPlan(planId, plans)
  const galleryLimit = effectiveGalleryLimit(currentPlan)
  const galleryCount = state.collections.length
  const storagePct = Math.min(100, Math.round((usedStorageBytes / state.storageLimitBytes) * 100))
  const galleryPct = Math.min(100, Math.round((galleryCount / galleryLimit) * 100))

  const upgrade = (targetId: PlanId) => {
    if (targetId === planId) return
    changePlan(targetId)
    notify(`Upgraded to ${getPlan(targetId, plans).name}`)
  }

  const higherPlans = plans.filter((p) => p.priceMonthlyFcfa > currentPlan.priceMonthlyFcfa)

  return (
    <>
      <h1>Billing</h1>

      <div className="billing-overview">
        <section className="billing-card">
          <h2>Current plan</h2>
          <p className="billing-plan-name">{currentPlan.name}</p>
          <p className="billing-plan-price">{formatFcfa(currentPlan.priceMonthlyFcfa)}</p>
          {planId === 'free' && (
            <p className="billing-watermark-note">
              The Free plan includes a &ldquo;Powered by Pixeo&rdquo; watermark on public galleries.
              Upgrade to remove it.
            </p>
          )}
          <Link href="/pricing" className="text-button">
            View all plans →
          </Link>
        </section>

        <section className="billing-card">
          <h2>Storage</h2>
          <div className="gauge-bar">
            <span style={{ width: `${storagePct}%` }} />
          </div>
          <p>
            {formatBytes(usedStorageBytes)} of {formatBytes(state.storageLimitBytes)} used ({storagePct}%)
          </p>
        </section>

        <section className="billing-card">
          <h2>Galleries</h2>
          <div className="gauge-bar">
            <span style={{ width: `${galleryPct}%` }} />
          </div>
          <p>
            {galleryCount} of {currentPlan.galleryLimit === null ? `${galleryLimit}+` : galleryLimit} galleries
          </p>
        </section>
      </div>

      {higherPlans.length > 0 && (
        <section className="billing-upgrades">
          <h2>Upgrade</h2>
          <div className="billing-upgrade-row">
            {higherPlans.map((p) => (
              <AppButton key={p.id} onClick={() => upgrade(p.id)}>
                Upgrade to {p.name} — {formatFcfa(p.priceMonthlyFcfa)}
              </AppButton>
            ))}
          </div>
        </section>
      )}

      <section className="billing-history">
        <h2>Billing history</h2>
        {state.billingHistory.length === 0 ? (
          <p className="muted">No billing events yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {state.billingHistory.map((event) => (
                <tr key={event.id}>
                  <td>{new Date(event.createdAt).toLocaleDateString('fr-FR')}</td>
                  <td>{event.label}</td>
                  <td>{formatFcfa(event.amountFcfa)}</td>
                  <td>
                    <span className={`status-pill ${event.status}`}>{event.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  )
}
