'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import { AppButton } from '@/components/app-button'
import { Modal } from '@/components/modal'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, formatFcfa, getPlan, type PlanId } from '@/lib/plans'
import { useToast } from '@/components/toast-provider'

export function AdminPhotographersScreen() {
  const { state, updateAccount, createPlatformAccount } = useGallery()
  const { notify } = useToast()
  const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
  const accounts = state.accounts

  const [createOpen, setCreateOpen] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'photographer' | 'platform_admin'>('photographer')
  const [planId, setPlanId] = useState<PlanId>('free')
  const [saving, setSaving] = useState(false)
  const [roleFilter, setRoleFilter] = useState<'all' | 'photographer' | 'platform_admin'>('all')

  const filtered = useMemo(() => {
    return accounts.filter((a) => (roleFilter === 'all' ? true : a.role === roleFilter))
  }, [accounts, roleFilter])

  const toggleStatus = (id: string, current: 'active' | 'suspended') => {
    const next = current === 'active' ? 'suspended' : 'active'
    updateAccount(id, { status: next })
    notify(`Account ${next === 'active' ? 'activated' : 'suspended'}`)
  }

  const changePlan = (id: string, nextPlan: PlanId) => {
    updateAccount(id, { planId: nextPlan })
    notify(`Plan updated to ${getPlan(nextPlan, plans).name}`)
  }

  const resetForm = () => {
    setName('')
    setEmail('')
    setPassword('')
    setRole('photographer')
    setPlanId('free')
  }

  const onCreate = (e: FormEvent) => {
    e.preventDefault()
    setSaving(true)
    const result = createPlatformAccount({ name, email, password, role, planId })
    setSaving(false)
    if (!result.ok) {
      notify(result.error || 'Could not create account', 'error')
      return
    }
    notify(
      role === 'platform_admin'
        ? 'Admin account created'
        : 'Photographer account created',
    )
    resetForm()
    setCreateOpen(false)
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>Users</h1>
          <p className="page-lead">Add photographers or platform admins, manage plans and status.</p>
        </div>
        <AppButton onClick={() => setCreateOpen(true)}>Add user</AppButton>
      </div>

      <div className="admin-filter-row">
        <button
          type="button"
          className={roleFilter === 'all' ? 'chip active' : 'chip'}
          onClick={() => setRoleFilter('all')}
        >
          All ({accounts.length})
        </button>
        <button
          type="button"
          className={roleFilter === 'photographer' ? 'chip active' : 'chip'}
          onClick={() => setRoleFilter('photographer')}
        >
          Photographers ({accounts.filter((a) => a.role === 'photographer').length})
        </button>
        <button
          type="button"
          className={roleFilter === 'platform_admin' ? 'chip active' : 'chip'}
          onClick={() => setRoleFilter('platform_admin')}
        >
          Admins ({accounts.filter((a) => a.role === 'platform_admin').length})
        </button>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((account) => {
            const plan = getPlan(account.planId, plans)
            return (
              <tr key={account.id}>
                <td>
                  {account.role === 'photographer' ? (
                    <Link href={`/admin/photographers/${account.id}`}>{account.name}</Link>
                  ) : (
                    account.name
                  )}
                </td>
                <td>{account.email}</td>
                <td>
                  <span className={`role-pill ${account.role}`}>
                    {account.role === 'platform_admin' ? 'Admin' : 'Photographer'}
                  </span>
                </td>
                <td>
                  {account.role === 'photographer' ? (
                    <>
                      {plan.name} ({formatFcfa(plan.priceMonthlyFcfa)})
                    </>
                  ) : (
                    '—'
                  )}
                </td>
                <td>
                  <span className={`status-pill ${account.status}`}>{account.status}</span>
                </td>
                <td className="table-actions">
                  <button
                    type="button"
                    className="outline-button"
                    onClick={() => toggleStatus(account.id, account.status)}
                  >
                    {account.status === 'active' ? 'Suspend' : 'Activate'}
                  </button>
                  {account.role === 'photographer' && (
                    <select
                      value={account.planId}
                      onChange={(e) => changePlan(account.id, e.target.value as PlanId)}
                      aria-label={`Plan for ${account.name}`}
                    >
                      {plans.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <Modal open={createOpen} title="Add user" onClose={() => setCreateOpen(false)}>
        <form className="admin-create-form" onSubmit={onCreate}>
          <label>
            Role
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'photographer' | 'platform_admin')}
            >
              <option value="photographer">Photographer</option>
              <option value="platform_admin">Platform admin</option>
            </select>
          </label>
          <label>
            Name
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
              minLength={6}
              required
            />
          </label>
          {role === 'photographer' && (
            <label>
              Plan
              <select value={planId} onChange={(e) => setPlanId(e.target.value as PlanId)}>
                {plans.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} — {formatFcfa(p.priceMonthlyFcfa)}
                  </option>
                ))}
              </select>
            </label>
          )}
          <div className="modal-actions">
            <button type="button" className="outline-button" onClick={() => setCreateOpen(false)}>
              Cancel
            </button>
            <AppButton type="submit" loading={saving}>
              Create account
            </AppButton>
          </div>
        </form>
      </Modal>
    </>
  )
}
