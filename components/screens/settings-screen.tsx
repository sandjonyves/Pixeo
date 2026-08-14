'use client'

import { useState } from 'react'
import { Plus, Zap } from 'lucide-react'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import { readImageFiles } from '@/lib/gallery-context'

const tabs = [
  'Branding',
  'Watermark',
  'Presets',
  'Email Templates',
  'Preferences',
  'Integrations',
] as const

type Tab = (typeof tabs)[number]

export function SettingsScreen() {
  const { state, updateBranding, updateHomepage, resetDemoData } = useGallery()
  const { notify } = useToast()
  const [tab, setTab] = useState<Tab>('Branding')
  const [username, setUsername] = useState(state.branding.username)
  const [domain, setDomain] = useState(state.branding.customDomain)
  const [watermarkText, setWatermarkText] = useState(state.branding.watermarkText)
  const [saving, setSaving] = useState(false)

  const saveBranding = async () => {
    if (!username.trim()) {
      notify('Username is required.', 'error')
      return
    }
    setSaving(true)
    await new Promise((r) => setTimeout(r, 300))
    updateBranding({
      username: username.trim().toLowerCase(),
      customDomain: domain.trim(),
      watermarkText,
    })
    updateHomepage({ brandName: username.trim().toUpperCase() })
    setSaving(false)
    notify('Settings saved')
  }

  const uploadLogo = async (files: FileList | null) => {
    if (!files?.length) return
    const [image] = await readImageFiles(files)
    updateBranding({ logoUrl: image.src })
    notify('Logo uploaded')
  }

  return (
    <>
      <div className="page-heading">
        <h1>Settings</h1>
        <AppButton loading={saving} onClick={saveBranding}>
          Save changes
        </AppButton>
      </div>

      <div className="tabs settings-tabs">
        {tabs.map((item) => (
          <button
            key={item}
            type="button"
            className={tab === item ? 'active' : undefined}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </div>

      {tab === 'Branding' && (
        <div className="settings-form">
          <h3>Domain</h3>
          <div className="field read">{username || 'username'}.pixeo.app</div>
          <p>
            Your client galleries and mobile gallery apps are always available with your default
            site address. To change your default domain, edit your username under <b>Account.</b>
          </p>

          <h3>
            Username
            <span className="upgrade">
              <Zap size={15} /> FREE
            </span>
          </h3>
          <div className="field">
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>

          <h3>
            Custom Domain{' '}
            <span className="upgrade">
              <Zap size={15} /> UPGRADE
            </span>
          </h3>
          <div className="field muted">
            <input
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="www.yourdomain.com"
            />
          </div>
          <p>
            Use your own custom domain for your client galleries. This feature is available with an
            upgraded account.
          </p>

          <div className="upgrade-card">
            <h2>Upgrade for more brand control</h2>
            <p>Upgrade to a paid plan to add your full logo, custom favicon and more.</p>
            <AppButton onClick={() => notify('Demo upgrade unlocked for branding tools.', 'info')}>
              Upgrade
            </AppButton>
            <h3>Logos</h3>
            <label className="logo-placeholder logo-upload">
              {state.branding.logoUrl ? (
                <img src={state.branding.logoUrl} alt="Logo" />
              ) : (
                <Plus size={24} />
              )}
              <input
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => uploadLogo(e.target.files)}
              />
            </label>
          </div>
        </div>
      )}

      {tab === 'Watermark' && (
        <div className="settings-form">
          <h3>Watermark</h3>
          <button
            type="button"
            className="toggle-row"
            onClick={() =>
              updateBranding({ watermarkEnabled: !state.branding.watermarkEnabled })
            }
          >
            <span className={`toggle ${state.branding.watermarkEnabled ? 'on' : 'off'}`}>
              <i />
            </span>
            {state.branding.watermarkEnabled ? 'Enabled' : 'Disabled'}
          </button>
          <label className="stacked-label">
            Watermark text
            <input
              value={watermarkText}
              onChange={(e) => setWatermarkText(e.target.value)}
            />
          </label>
          <AppButton onClick={saveBranding} loading={saving}>
            Save watermark
          </AppButton>
        </div>
      )}

      {tab === 'Presets' && (
        <div className="settings-form">
          <h3>Design presets</h3>
          <p>Save visual presets from any collection editor, then reuse them on new galleries.</p>
          <AppButton onClick={() => notify('Open a collection editor to save a preset.', 'info')}>
            Browse collection presets
          </AppButton>
        </div>
      )}

      {tab === 'Email Templates' && (
        <div className="settings-form">
          <h3>Email templates</h3>
          <p>Customize gallery delivery and reminder emails.</p>
          <AppButton onClick={() => notify('Email template editor opened', 'info')}>
            Edit delivery template
          </AppButton>
        </div>
      )}

      {tab === 'Preferences' && (
        <div className="settings-form">
          <h3>Preferences</h3>
          <p>Reset demo data if you want to restore the Yves sample collection.</p>
          <AppButton
            danger
            onClick={() => {
              resetDemoData()
              notify('Demo data restored')
            }}
          >
            Reset demo data
          </AppButton>
        </div>
      )}

      {tab === 'Integrations' && (
        <div className="settings-form">
          <h3>Integrations</h3>
          <p>Connect Lightroom, Dropbox or Google Drive in a production workspace.</p>
          <AppButton secondary onClick={() => notify('Integration marketplace coming soon', 'info')}>
            Browse integrations
          </AppButton>
        </div>
      )}
    </>
  )
}
