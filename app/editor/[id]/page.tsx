import { AuthGuard } from '@/components/auth-guard'
import { OnboardingGate } from '@/components/onboarding'
import { EditorScreen } from '@/components/screens/editor-screen'

export default async function EditorPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return (
    <AuthGuard>
      <EditorScreen collectionId={id} />
      <OnboardingGate />
    </AuthGuard>
  )
}
