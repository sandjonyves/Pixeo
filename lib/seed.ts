import type { AppState, Collection, Photo } from '@/lib/types'

const STOCK = [
  'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1497250681960-ef046c08a56e?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1531058020387-3be344556be6?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1506377585622-bedcbb027afc?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1544986581-efac024faf62?auto=format&fit=crop&w=900&q=85',
  'https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=900&q=85',
]

export function uid(prefix = 'id') {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36).slice(-4)}`
}

export function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
    .slice(0, 48) || 'collection'
}

export function formatBytes(bytes: number) {
  const gb = bytes / (1024 * 1024 * 1024)
  if (gb >= 0.01) return `${gb.toFixed(2)} GB`
  const mb = bytes / (1024 * 1024)
  if (mb >= 0.1) return `${mb.toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

export function formatDateLabel(iso?: string) {
  if (!iso) return 'No date'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function createSeedState(): AppState {
  const now = new Date().toISOString()
  const photoIds = STOCK.map((_, i) => `photo_seed_${i + 1}`)
  const photos: Photo[] = STOCK.map((src, i) => ({
    id: photoIds[i],
    src,
    name: `Highlight ${String(i + 1).padStart(2, '0')}.jpg`,
    starred: i === 1 || i === 4,
    createdAt: now,
    sizeBytes: 1_800_000 + i * 40_000,
    collectionIds: ['col_yves'],
  }))

  const collection: Collection = {
    id: 'col_yves',
    name: 'Yves',
    slug: 'yves',
    coverPhotoId: photoIds[1],
    coverLayout: 'center',
    coverFocal: { x: 50, y: 50 },
    eventDate: now.slice(0, 10),
    status: 'published',
    starred: false,
    showOnHomepage: true,
    category: 'Portrait',
    categoryTags: ['Portrait'],
    contactIds: ['contact_1'],
    sets: [{ id: 'set_highlights', name: 'Highlights', description: '', photoIds: [...photoIds] }],
    createdAt: now,
    updatedAt: now,
    password: '',
    clientExclusive: false,
    downloadEnabled: true,
    downloadHighRes: true,
    downloadHighResSize: '3600',
    downloadWebSize: true,
    downloadWebSizePx: '1024',
    downloadPinEnabled: true,
    downloadPin: '2118',
    favoritesEnabled: true,
    favoriteNotesEnabled: true,
    favoriteLists: [],
    storeEnabled: false,
    shareToken: 'share_yves_demo',
  }

  return {
    user: {
      id: 'user_demo',
      name: 'Simple Shoot',
      email: 'demo@simpleshoot.com',
      password: 'demo1234',
      initials: 'S',
    },
    photos,
    collections: [collection],
    campaigns: [],
    contacts: [
      {
        id: 'contact_1',
        email: 'client@example.com',
        name: 'Alex Client',
        optedIn: true,
        createdAt: now,
      },
    ],
    homepage: {
      enabled: true,
      password: '',
      biography: 'Photography with warmth and clarity.',
      brandName: 'SIMPLESHOOT',
    },
    branding: {
      username: 'simpleshoot',
      customDomain: '',
      watermarkEnabled: false,
      watermarkText: 'SimpleShoot',
    },
    storageLimitBytes: 3 * 1024 * 1024 * 1024,
    notifications: [
      {
        id: 'n1',
        message: 'Welcome to Client Gallery',
        read: false,
        createdAt: now,
      },
    ],
    emailHistory: [],
    galleryActivities: [],
    presets: [
      { id: 'preset_clean', name: 'Clean Center', coverLayout: 'center' },
      { id: 'preset_novel', name: 'Editorial Novel', coverLayout: 'novel' },
      { id: 'preset_vintage', name: 'Vintage Frame', coverLayout: 'vintage' },
    ],
  }
}

export { STOCK as STOCK_PHOTOS }
