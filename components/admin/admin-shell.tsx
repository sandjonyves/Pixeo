'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  CreditCard,
  Image as ImageIcon,
  LayoutDashboard,
  LogOut,
  Settings as SettingsIcon,
  Users,
  Wallet,
} from 'lucide-react'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

const adminNav = [
  { label: 'Overview', href: '/admin', icon: LayoutDashboard, exact: true },
  { label: 'Users', href: '/admin/photographers', icon: Users },
  { label: 'Plans', href: '/admin/plans', icon: Wallet },
  { label: 'Galleries', href: '/admin/galleries', icon: ImageIcon },
  { label: 'Billing', href: '/admin/billing', icon: CreditCard },
  { label: 'Settings', href: '/admin/settings', icon: SettingsIcon },
]

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { logout } = useGallery()
  const { notify } = useToast()

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href)

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <Link href="/admin" className="brand admin-brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo Admin</b>
        </Link>
        <nav>
          {adminNav.map(({ label, href, icon: Icon, exact }) => (
            <Link
              key={href}
              href={href}
              className={isActive(href, exact) ? 'active' : undefined}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>
        <button
          type="button"
          className="admin-logout"
          onClick={() => {
            logout()
            notify('Signed out')
            router.push('/login')
          }}
        >
          <LogOut size={18} />
          Log out
        </button>
      </aside>
      <main className="admin-content">{children}</main>
    </div>
  )
}
