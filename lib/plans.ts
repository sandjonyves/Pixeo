export type PlanId = 'free' | 'starter' | 'pro' | 'studio'

export type PlanDefinition = {
  id: PlanId
  name: string
  priceMonthlyFcfa: number
  storageLimitBytes: number
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
    features: [
      '5 Go storage',
      'Unlimited galleries',
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
    features: [
      '50 Go storage',
      'Unlimited galleries',
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
