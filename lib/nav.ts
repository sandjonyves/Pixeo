import {
  CreditCard,
  Image as ImageIcon,
  LayoutGrid,
  Settings as SettingsIcon,
  Star,
  type LucideIcon,
} from 'lucide-react'

export type DashboardRoute =
  | 'collections'
  | 'library'
  | 'starred'
  | 'homepage'
  | 'settings'
  | 'billing'

export const mainNav: {
  label: string
  icon: LucideIcon
  href: `/${DashboardRoute}`
  route: DashboardRoute
}[] = [
  { label: 'Collections', icon: ImageIcon, href: '/collections', route: 'collections' },
  { label: 'Library', icon: LayoutGrid, href: '/library', route: 'library' },
  { label: 'Starred', icon: Star, href: '/starred', route: 'starred' },
  { label: 'Homepage', icon: LayoutGrid, href: '/homepage', route: 'homepage' },
  { label: 'Settings', icon: SettingsIcon, href: '/settings', route: 'settings' },
]

/** Full studio sidebar including billing */
export const studioNav: {
  label: string
  icon: LucideIcon
  href: `/${DashboardRoute}`
  route: DashboardRoute
}[] = [
  ...mainNav,
  { label: 'Billing', icon: CreditCard, href: '/billing', route: 'billing' },
]

/** Optional marketing tools — not part of primary studio nav */
export const marketingHref = '/campaigns'
