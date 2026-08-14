import { Suspense } from 'react'
import { RegisterScreen } from '@/components/screens/register-screen'
import { PageSkeleton } from '@/components/skeleton'

export default function RegisterPage() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <RegisterScreen />
    </Suspense>
  )
}
