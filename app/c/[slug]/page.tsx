import { PublicGalleryScreen } from '@/components/screens/public-gallery-screen'

export default async function PublicCollectionPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ preview?: string }>
}) {
  const { slug } = await params
  const { preview } = await searchParams
  return <PublicGalleryScreen slug={slug} ownerPreview={preview === '1'} />
}
