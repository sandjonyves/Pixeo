import { AuthGuard } from '@/components/auth-guard'
import { OnboardingGate } from '@/components/onboarding'
import { DashboardShell } from '@/components/dashboard-shell'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthGuard>
      <DashboardShell>
        {children}
        <OnboardingGate />
      </DashboardShell>
    </AuthGuard>
  )
}
