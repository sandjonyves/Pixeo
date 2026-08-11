'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import {
  Bell,
  ChevronDown,
  CircleHelp,
  LogOut,
  Mail,
  Plus,
  Settings as SettingsIcon,
  User,
} from 'lucide-react'
import { marketingHref, mainNav } from '@/lib/nav'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'
import type { DashboardRoute } from '@/lib/nav'

function routeFromPathname(pathname: string): DashboardRoute | 'other' {
  if (pathname.startsWith('/library')) return 'library'
  if (pathname.startsWith('/starred')) return 'starred'
  if (pathname.startsWith('/homepage')) return 'homepage'
  if (pathname.startsWith('/settings')) return 'settings'
  if (pathname.startsWith('/campaign') || pathname.startsWith('/contacts')) return 'campaigns'
  if (pathname.startsWith('/collections')) return 'collections'
  return 'other'
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const route = routeFromPathname(pathname)
  const marketingOpen =
    route === 'campaigns' || pathname.startsWith('/campaign') || pathname.startsWith('/contacts')
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
          <b>Client Gallery</b>
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
          {mainNav.map(({ label, icon: Icon, href, route: itemRoute }) => (
            <Link
              key={itemRoute}
              href={href}
              className={route === itemRoute && itemRoute !== 'campaigns' ? 'active' : undefined}
            >
              <Icon size={23} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="tools">
          <small>Tools</small>
          <Link href={marketingHref} className={marketingOpen ? 'active' : undefined}>
            <Mail size={23} />
            <span>Marketing</span>
          </Link>
          {marketingOpen && (
            <div className="subnav">
              <Link
                href="/campaigns"
                className={pathname.startsWith('/campaigns') ? 'active' : undefined}
              >
                <Mail size={20} />
                Email Campaigns
              </Link>
              <Link
                href="/contacts"
                className={pathname.startsWith('/contacts') ? 'active' : undefined}
              >
                <span className="sub-icon">♙</span>
                Contacts
              </Link>
              <Link href="/settings">
                <SettingsIcon size={20} />
                Settings
              </Link>
            </div>
          )}
        </div>

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
            onClick={() => notify('Upgrade plans unlock more storage and custom domains.', 'info')}
          >
            <Plus size={16} />
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
