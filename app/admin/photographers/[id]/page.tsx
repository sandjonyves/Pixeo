import { AdminPhotographerDetailScreen } from '@/components/screens/admin/photographer-detail-screen'

export default async function AdminPhotographerDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <AdminPhotographerDetailScreen accountId={id} />
}
