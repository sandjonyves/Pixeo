import { PublicGalleryScreen } from '@/components/screens/public-gallery-screen'

export default async function PublicCollectionPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return <PublicGalleryScreen slug={slug} />
}
