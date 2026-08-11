export type CollectionStatus = 'published' | 'draft' | 'hidden' | 'pre-release'

export type CoverLayout =
  | 'center'
  | 'bottom-left'
  | 'novel'
  | 'stamp'
  | 'outline'
  | 'vintage'
  | 'frame'

export type Photo = {
  id: string
  src: string
  name: string
  starred: boolean
  createdAt: string
  sizeBytes: number
  collectionIds: string[]
}

export type PhotoSet = {
  id: string
  name: string
  description: string
  photoIds: string[]
}

export type FavoriteList = {
  id: string
  name: string
  selectionLimit: number
  createdAt: string
}

export type GalleryActivity = {
  id: string
  collectionId: string
  type: 'download' | 'favorite' | 'note' | 'view'
  photoId?: string
  photoName?: string
  note?: string
  visitorLabel: string
  createdAt: string
}

export type Collection = {
  id: string
  name: string
  slug: string
  coverPhotoId?: string
  coverLayout: CoverLayout
  coverFocal: { x: number; y: number }
  eventDate?: string
  status: CollectionStatus
  starred: boolean
  showOnHomepage: boolean
  category?: string
  categoryTags: string[]
  contactIds: string[]
  expiryDate?: string
  sets: PhotoSet[]
  createdAt: string
  updatedAt: string
  /** Gallery access password (Privacy) */
  password?: string
  clientExclusive: boolean
  downloadEnabled: boolean
  downloadHighRes: boolean
  downloadHighResSize: 'original' | '3600'
  downloadWebSize: boolean
  downloadWebSizePx: '2048' | '1024' | '640'
  downloadPinEnabled: boolean
  /** Separate 4-digit PIN for downloads */
  downloadPin: string
  favoritesEnabled: boolean
  favoriteNotesEnabled: boolean
  favoriteLists: FavoriteList[]
  storeEnabled: boolean
  shareToken: string
}

export type Campaign = {
  id: string
  name: string
  subject: string
  status: 'draft' | 'sent'
  body: string
  createdAt: string
}

export type Contact = {
  id: string
  email: string
  name: string
  optedIn: boolean
  createdAt: string
}

export type HomepageSettings = {
  enabled: boolean
  password: string
  biography: string
  brandName: string
}

export type BrandingSettings = {
  username: string
  customDomain: string
  logoUrl?: string
  faviconUrl?: string
  watermarkEnabled: boolean
  watermarkText: string
}

export type UserAccount = {
  id: string
  name: string
  email: string
  password: string
  initials: string
}

export type EmailShareRecord = {
  id: string
  collectionId: string
  collectionName: string
  to: string
  subject: string
  body: string
  includeDownload: boolean
  includePin: boolean
  status: 'sent' | 'scheduled'
  sentAt: string
  scheduledFor?: string
}

export type AppState = {
  user: UserAccount | null
  photos: Photo[]
  collections: Collection[]
  campaigns: Campaign[]
  contacts: Contact[]
  homepage: HomepageSettings
  branding: BrandingSettings
  storageLimitBytes: number
  notifications: { id: string; message: string; read: boolean; createdAt: string }[]
  emailHistory: EmailShareRecord[]
  galleryActivities: GalleryActivity[]
  presets: { id: string; name: string; coverLayout: CoverLayout }[]
}

export type ToastTone = 'success' | 'error' | 'info'

export const COVER_LAYOUTS: { id: CoverLayout; label: string }[] = [
  { id: 'center', label: 'Center' },
  { id: 'bottom-left', label: 'Bottom Left' },
  { id: 'novel', label: 'Novel' },
  { id: 'stamp', label: 'Stamp' },
  { id: 'outline', label: 'Outline' },
  { id: 'vintage', label: 'Vintage' },
  { id: 'frame', label: 'Frame' },
]
