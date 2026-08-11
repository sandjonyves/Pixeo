'use client'

import { useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useGallery } from '@/lib/gallery-context'
import { PageSkeleton } from '@/components/skeleton'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { ready, isAuthenticated } = useGallery()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!ready) return
    if (!isAuthenticated) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`)
    }
  }, [ready, isAuthenticated, router, pathname])

  if (!ready) return <PageSkeleton />
  if (!isAuthenticated) return <PageSkeleton />
  return <>{children}</>
}
