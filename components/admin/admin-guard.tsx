'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useGallery } from '@/lib/gallery-context'
import { PageSkeleton } from '@/components/skeleton'

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const { ready, isAuthenticated, isAdmin } = useGallery()
  const router = useRouter()

  useEffect(() => {
    if (!ready) return
    if (!isAuthenticated) {
      router.replace('/login?next=/admin')
      return
    }
    if (!isAdmin) {
      router.replace('/collections')
    }
  }, [ready, isAuthenticated, isAdmin, router])

  if (!ready || !isAuthenticated || !isAdmin) return <PageSkeleton />
  return <>{children}</>
}
