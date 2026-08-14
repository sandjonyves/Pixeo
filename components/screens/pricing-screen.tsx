'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, formatFcfa, getPlan, type PlanId } from '@/lib/plans'
import { useToast } from '@/components/toast-provider'

export function PricingScreen() {
  const { state, isAuthenticated, changePlan } = useGallery()
  const { notify } = useToast()
  const router = useRouter()
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const currentPlanId = state.user?.planId

  const handleSelect = (planId: PlanId) => {
    if (!isAuthenticated) {
      router.push(`/register?plan=${planId}`)
      return
    }
    if (currentPlanId === planId) {
      router.push('/billing')
      return
    }
    changePlan(planId)
    notify(`Plan updated to ${getPlan(planId, plans).name}`)
    router.push('/billing')
  }

  return (
    <div className="pricing-page">
      <header className="landing-nav">
        <Link href="/" className="brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo</b>
        </Link>
        <div className="landing-actions">
          {isAuthenticated ? (
            <Link href="/collections" className="primary-button">
              Dashboard
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

      <section className="pricing-hero">
        <p className="eyebrow">PIXEO PLANS</p>
        <h1>Simple pricing for photographers</h1>
        <p>Choose a plan that fits your delivery workflow. Upgrade anytime.</p>
      </section>

      <div className="pricing-grid">
        {plans.map((plan) => {
          const isCurrent = isAuthenticated && currentPlanId === plan.id
          return (
            <article
              key={plan.id}
              className={`pricing-card ${plan.highlighted ? 'featured' : ''} ${isCurrent ? 'current' : ''}`}
            >
              <h2>{plan.name}</h2>
              <p className="pricing-price">{formatFcfa(plan.priceMonthlyFcfa)}</p>
              <ul>
                {plan.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <AppButton
                secondary={isCurrent}
                onClick={() => handleSelect(plan.id)}
              >
                {isCurrent ? 'Current plan' : isAuthenticated ? 'Switch plan' : 'Get started'}
              </AppButton>
            </article>
          )
        })}
      </div>

      <p className="pricing-foot">
        <Link href="/">← Back to home</Link>
      </p>
    </div>
  )
}
