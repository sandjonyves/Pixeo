'use client'

import { useState } from 'react'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { DEFAULT_PLANS, type PlanDefinition, type PlanId } from '@/lib/plans'
import { useToast } from '@/components/toast-provider'

const GB = 1024 * 1024 * 1024

export function AdminPlansScreen() {
  const { state, updatePlans } = useGallery()
  const { notify } = useToast()
  const [draft, setDraft] = useState<PlanDefinition[]>(
    () => (state.plans?.length ? state.plans : DEFAULT_PLANS).map((p) => ({ ...p })),
  )
  const [saving, setSaving] = useState(false)

  const updateDraft = (id: PlanId, patch: Partial<PlanDefinition>) => {
    setDraft((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)))
  }

  const save = async () => {
    setSaving(true)
    await new Promise((r) => setTimeout(r, 300))
    updatePlans(draft)
    setSaving(false)
    notify('Plans updated')
  }

  return (
    <>
      <h1>Plans</h1>
      <p className="page-lead">Edit storage limits and monthly pricing. Collections are unlimited on every plan.</p>

      <table className="data-table">
        <thead>
          <tr>
            <th>Plan</th>
            <th>Storage (GB)</th>
            <th>Price (FCFA/mo)</th>
          </tr>
        </thead>
        <tbody>
          {draft.map((plan) => (
            <tr key={plan.id}>
              <td>
                <strong>{plan.name}</strong>
                <small className="block muted">{plan.id}</small>
              </td>
              <td>
                <input
                  type="number"
                  min={1}
                  value={Math.round(plan.storageLimitBytes / GB)}
                  onChange={(e) =>
                    updateDraft(plan.id, {
                      storageLimitBytes: Math.max(1, Number(e.target.value)) * GB,
                    })
                  }
                />
              </td>
              <td>
                <input
                  type="number"
                  min={0}
                  step={500}
                  value={plan.priceMonthlyFcfa}
                  onChange={(e) =>
                    updateDraft(plan.id, { priceMonthlyFcfa: Math.max(0, Number(e.target.value)) })
                  }
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="modal-actions left">
        <AppButton loading={saving} onClick={save}>
          Save plans
        </AppButton>
      </div>
    </>
  )
}
