'use client'

import { useState } from 'react'
import { AppButton } from '@/components/app-button'
import { useToast } from '@/components/toast-provider'

export function AdminSettingsScreen() {
  const { notify } = useToast()
  const [platformName, setPlatformName] = useState('Pixeo')
  const [maintenance, setMaintenance] = useState(false)
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    await new Promise((r) => setTimeout(r, 300))
    setSaving(false)
    notify(maintenance ? 'Maintenance mode enabled (mock)' : 'Settings saved')
  }

  return (
    <>
      <h1>Platform settings</h1>
      <p className="page-lead">Global configuration for the Pixeo SaaS platform.</p>

      <div className="settings-form">
        <label className="stacked-label">
          Platform name
          <input value={platformName} onChange={(e) => setPlatformName(e.target.value)} />
        </label>

        <label className="toggle-row">
          <input
            type="checkbox"
            checked={maintenance}
            onChange={(e) => setMaintenance(e.target.checked)}
          />
          Maintenance mode (mock)
        </label>
        {maintenance && (
          <p className="form-error">Users would see a maintenance banner in production.</p>
        )}

        <AppButton loading={saving} onClick={save}>
          Save settings
        </AppButton>
      </div>
    </>
  )
}
