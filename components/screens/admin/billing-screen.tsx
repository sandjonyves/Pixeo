'use client'

import { useMemo } from 'react'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, formatFcfa, getPlan } from '@/lib/plans'

export function AdminBillingScreen() {
  const { state } = useGallery()

  const summary = useMemo(() => {
    const plans = state.plans?.length ? state.plans : DEFAULT_PLANS
    const photographers = state.accounts.filter(
      (a) => a.role === 'photographer' && a.status === 'active',
    )
    const byPlan = plans.map((plan) => ({
      plan: plan.name,
      count: photographers.filter((a) => a.planId === plan.id).length,
      revenue: photographers
        .filter((a) => a.planId === plan.id)
        .reduce((sum) => sum + plan.priceMonthlyFcfa, 0),
    }))
    const totalMrr = byPlan.reduce((sum, row) => sum + row.revenue, 0)
    const paidInvoices = state.billingHistory.filter((b) => b.status === 'paid').length
    const pendingInvoices = state.billingHistory.filter((b) => b.status === 'pending').length

    return { byPlan, totalMrr, paidInvoices, pendingInvoices }
  }, [state.accounts, state.billingHistory, state.plans])

  return (
    <>
      <h1>Platform billing</h1>
      <p className="page-lead">Mock revenue overview across photographer subscriptions.</p>

      <div className="kpi-grid">
        <article className="kpi-card featured">
          <small>Total MRR</small>
          <strong>{formatFcfa(summary.totalMrr)}</strong>
        </article>
        <article className="kpi-card">
          <small>Paid invoices</small>
          <strong>{summary.paidInvoices}</strong>
        </article>
        <article className="kpi-card">
          <small>Pending invoices</small>
          <strong>{summary.pendingInvoices}</strong>
        </article>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Plan</th>
            <th>Active subscribers</th>
            <th>Monthly revenue</th>
          </tr>
        </thead>
        <tbody>
          {summary.byPlan.map((row) => (
            <tr key={row.plan}>
              <td>{row.plan}</td>
              <td>{row.count}</td>
              <td>{formatFcfa(row.revenue)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <section className="billing-history">
        <h2>Recent platform invoices</h2>
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
            {state.billingHistory.slice(0, 10).map((event) => (
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
      </section>
    </>
  )
}
