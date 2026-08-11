'use client'

import { useEffect, useState } from 'react'
import { AppButton } from '@/components/app-button'

const ONBOARDING_KEY = 'gallery-onboarding-complete'

const steps = [
  [
    'Edit Name and Event Date',
    'Change the name of your collection and add an optional event date.',
  ],
  [
    'Add your photos',
    'Upload photos from your computer or add sample photos to get started.',
  ],
  [
    'Customize Your Design',
    'Personalize the look and feel of your collection in a few clicks.',
  ],
  [
    'Publish your collection',
    'Share your finished gallery with clients when you are ready.',
  ],
] as const

function OnboardingModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(0)
  const current = steps[step]

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="tutorial-card" onClick={(e) => e.stopPropagation()}>
        <p className="eyebrow">GET STARTED</p>
        <h3>{current[0]}</h3>
        <p>{current[1]}</p>
        <div className="tutorial-actions">
          <span>
            {step + 1} of {steps.length}
          </span>
          <button type="button" className="text-button" onClick={onClose}>
            Skip
          </button>
          {step < steps.length - 1 ? (
            <AppButton onClick={() => setStep(step + 1)}>Next</AppButton>
          ) : (
            <AppButton onClick={onClose}>Finish</AppButton>
          )}
        </div>
      </div>
    </div>
  )
}

export function OnboardingGate() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!window.localStorage.getItem(ONBOARDING_KEY)) {
      setOpen(true)
    }
  }, [])

  const close = () => {
    window.localStorage.setItem(ONBOARDING_KEY, 'true')
    setOpen(false)
  }

  if (!open) return null
  return <OnboardingModal onClose={close} />
}
