import {
  Image as ImageIcon,
  LayoutGrid,
  Mail,
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
  | 'campaigns'

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

export const marketingHref = '/campaigns'
