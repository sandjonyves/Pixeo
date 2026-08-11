'use client'

import { GalleryProvider } from '@/lib/gallery-context'
import { ToastProvider } from '@/components/toast-provider'

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <GalleryProvider>
      <ToastProvider>{children}</ToastProvider>
    </GalleryProvider>
  )
}
