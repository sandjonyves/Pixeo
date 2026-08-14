export type PlanId = 'free' | 'starter' | 'pro' | 'studio'

export type PlanDefinition = {
  id: PlanId
  name: string
  priceMonthlyFcfa: number
  storageLimitBytes: number
  /** null = soft unlimited (cap for safety) */
  galleryLimit: number | null
  softGalleryCap: number
  features: string[]
  highlighted?: boolean
}

const GB = 1024 * 1024 * 1024

export const DEFAULT_PLANS: PlanDefinition[] = [
  {
    id: 'free',
    name: 'Free',
    priceMonthlyFcfa: 0,
    storageLimitBytes: 5 * GB,
    galleryLimit: 2,
    softGalleryCap: 2,
    features: [
      '5 Go storage',
      '2 galleries',
      'Private client link',
      'Password protection',
      'Pixeo watermark',
    ],
  },
  {
    id: 'starter',
    name: 'Starter',
    priceMonthlyFcfa: 2000,
    storageLimitBytes: 50 * GB,
    galleryLimit: 10,
    softGalleryCap: 10,
    features: [
      '50 Go storage',
      '10 galleries',
      'HD downloads',
      'Password protection',
      'No watermark',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    priceMonthlyFcfa: 5000,
    storageLimitBytes: 250 * GB,
    galleryLimit: null,
    softGalleryCap: 200,
    highlighted: true,
    features: [
      '250 Go storage',
      'Unlimited galleries',
      'HD downloads',
      'Branding & homepage',
      'Basic stats',
    ],
  },
  {
    id: 'studio',
    name: 'Studio',
    priceMonthlyFcfa: 10000,
    storageLimitBytes: 1024 * GB,
    galleryLimit: null,
    softGalleryCap: 500,
    features: [
      '1 To storage',
      'Unlimited galleries',
      'Priority support',
      'All Pro features',
      'Advanced delivery tools',
    ],
  },
]

export function getPlan(id: PlanId, plans: PlanDefinition[] = DEFAULT_PLANS) {
  return plans.find((p) => p.id === id) ?? DEFAULT_PLANS[0]
}

export function formatFcfa(amount: number) {
  if (amount === 0) return 'Gratuit'
  return `${amount.toLocaleString('fr-FR')} FCFA/mois`
}

export function effectiveGalleryLimit(plan: PlanDefinition) {
  return plan.galleryLimit ?? plan.softGalleryCap
}
