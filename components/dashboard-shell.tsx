'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import {
  Bell,
  ChevronDown,
  CircleHelp,
  CreditCard,
  LogOut,
  Settings as SettingsIcon,
  User,
} from 'lucide-react'
import { studioNav } from '@/lib/nav'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import type { DashboardRoute } from '@/lib/nav'

function routeFromPathname(pathname: string): DashboardRoute | 'other' {
  if (pathname.startsWith('/library')) return 'library'
  if (pathname.startsWith('/starred')) return 'starred'
  if (pathname.startsWith('/homepage')) return 'homepage'
  if (pathname.startsWith('/settings')) return 'settings'
  if (pathname.startsWith('/billing')) return 'billing'
  if (pathname.startsWith('/collections')) return 'collections'
  return 'other'
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const route = routeFromPathname(pathname)
  const { state, usedStorageLabel, usedStorageBytes, logout, markNotificationsRead } = useGallery()
  const { notify } = useToast()
  const [accountOpen, setAccountOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  const unread = useMemo(
    () => state.notifications.filter((n) => !n.read).length,
    [state.notifications],
  )

  const usagePct = Math.min(
    100,
    Math.round((usedStorageBytes / state.storageLimitBytes) * 100),
  )

  return (
    <main className="dashboard-shell">
      <header className="dashboard-top">
        <Link href="/collections" className="brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo</b>
          <ChevronDown size={14} />
        </Link>
        <div className="top-user">
          <button
            type="button"
            aria-label="Help"
            onClick={() => notify('Help center: use the sidebar to manage collections, library and sharing.', 'info')}
          >
            <CircleHelp size={24} />
          </button>
          <div className="menu-anchor">
            <button
              type="button"
              aria-label="Notifications"
              onClick={() => {
                setNotifOpen((v) => !v)
                setAccountOpen(false)
                markNotificationsRead()
              }}
            >
              <Bell size={22} />
              {unread > 0 && <em className="badge">{unread}</em>}
            </button>
            {notifOpen && (
              <div className="dropdown-panel notif-panel">
                <strong>Notifications</strong>
                {state.notifications.length === 0 ? (
                  <p>You are all caught up.</p>
                ) : (
                  state.notifications.slice(0, 6).map((n) => (
                    <button
                      key={n.id}
                      type="button"
                      onClick={() => {
                        setNotifOpen(false)
                        notify(n.message, 'info')
                      }}
                    >
                      {n.message}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
          <div className="menu-anchor">
            <button
              type="button"
              aria-label="Account menu"
              onClick={() => {
                setAccountOpen((v) => !v)
                setNotifOpen(false)
              }}
            >
              <span>{state.user?.initials ?? 'U'}</span>
            </button>
            {accountOpen && (
              <div className="dropdown-panel account-panel">
                <p className="account-meta">
                  <b>{state.user?.name}</b>
                  <small>{state.user?.email}</small>
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setAccountOpen(false)
                    router.push('/account')
                  }}
                >
                  <User size={16} /> Account
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAccountOpen(false)
                    router.push('/billing')
                  }}
                >
                  <CreditCard size={16} /> Billing
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAccountOpen(false)
                    router.push('/settings')
                  }}
                >
                  <SettingsIcon size={16} /> Settings
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAccountOpen(false)
                    logout()
                    notify('Signed out')
                    router.push('/login')
                  }}
                >
                  <LogOut size={16} /> Log out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <aside className="dashboard-sidebar">
        <nav>
          {studioNav.map(({ label, icon: Icon, href, route: itemRoute }) => (
            <Link
              key={itemRoute}
              href={href}
              className={route === itemRoute ? 'active' : undefined}
            >
              <Icon size={23} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="storage" title={usedStorageLabel}>
          <span
            className="storage-ring"
            style={{
              background: `conic-gradient(#16c2af ${usagePct}%, #d9dfdd 0)`,
            }}
          />
          {usedStorageLabel}
          <button
            type="button"
            className="storage-add"
            aria-label="Upgrade storage"
            onClick={() => router.push('/billing')}
          >
            ↑
          </button>
        </div>
      </aside>

      <section className="dashboard-content">{children}</section>

      <button
        type="button"
        className="chat"
        aria-label="Support chat"
        onClick={() => notify('Support chat will respond shortly.', 'info')}
      >
        <span />
      </button>
    </main>
  )
}
