'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, getPlan, type PlanId } from '@/lib/plans'
import { useToast } from '@/components/toast-provider'

const VALID_PLANS: PlanId[] = ['free', 'starter', 'pro', 'studio']

export function RegisterScreen() {
  const { register, state } = useGallery()
  const { notify } = useToast()
  const router = useRouter()
  const params = useSearchParams()
  const planParam = params.get('plan')
  const selectedPlan = useMemo(() => {
    if (planParam && VALID_PLANS.includes(planParam as PlanId)) return planParam as PlanId
    return 'free' as PlanId
  }, [planParam])
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const plan = getPlan(selectedPlan, plans)

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await register(name, email, password, selectedPlan)
    setLoading(false)
    if (!result.ok) {
      setError(result.error || 'Registration failed')
      notify(result.error || 'Registration failed', 'error')
      return
    }
    notify(`Account created on ${plan.name} plan`)
    router.replace('/collections')
  }

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={onSubmit}>
        <div className="brand auth-brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo</b>
        </div>
        <h1>Create account</h1>
        {selectedPlan !== 'free' && (
          <p className="auth-sub">
            Selected plan: <strong>{plan.name}</strong>
          </p>
        )}
        <label>
          Studio name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <AppButton type="submit" loading={loading}>
          Create account
        </AppButton>
        <p className="auth-foot">
          Already have an account? <Link href="/login">Sign in</Link>
        </p>
        <p className="auth-foot">
          <Link href="/pricing">Compare plans</Link>
        </p>
      </form>
    </div>
  )
}
