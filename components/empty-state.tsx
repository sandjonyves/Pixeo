import Link from 'next/link'
import { Star } from 'lucide-react'

type EmptyKind = 'library' | 'photos' | 'collections' | 'campaigns' | 'contacts' | 'search'

const copy: Record<EmptyKind, [string, string]> = {
  library: [
    'You have no photos yet',
    'All photos added to your collections will appear here. Get started by creating a collection.',
  ],
  photos: [
    'You have no starred photos yet',
    'Track your favorite photos with stars.',
  ],
  collections: [
    'You have no starred collections yet',
    'Track your favorite collections with stars.',
  ],
  campaigns: [
    'Create your first email campaign',
    'Power up your marketing with email campaigns to opted-in contacts.',
  ],
  contacts: [
    'No contacts yet',
    'Add opted-in emails to start building your list.',
  ],
  search: [
    'No results found',
    'Try a different search term or clear your filters.',
  ],
}

export function EmptyState({
  kind,
  actionHref,
  actionLabel,
}: {
  kind: EmptyKind
  actionHref?: string
  actionLabel?: string
}) {
  const [title, description] = copy[kind]
  const href = actionHref ?? (kind === 'library' ? '/collections' : undefined)
  const label = actionLabel ?? (kind === 'library' ? 'New Collection' : undefined)

  return (
    <div className="empty-state">
      <div className="empty-art">
        <Star size={58} strokeWidth={1} />
      </div>
      <h2>{title}</h2>
      <p>{description}</p>
      {href && label && (
        <Link href={href} className="primary-button">
          {label}
        </Link>
      )}
    </div>
  )
}
