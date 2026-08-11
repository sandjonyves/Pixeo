import { Suspense } from 'react'
import { LoginScreen } from '@/components/screens/login-screen'
import { PageSkeleton } from '@/components/skeleton'

export default function LoginPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <LoginScreen />
    </Suspense>
  )
}
