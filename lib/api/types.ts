/**
 * API contract types for the future Pixeo backend.
 * Mirrors Supabase tables and REST/ RPC responses — not used by the demo frontend yet.
 */

import type { PlanId } from '@/lib/plans'
import type { CollectionStatus, CoverLayout } from '@/lib/types'

// ─── Shared ───────────────────────────────────────────────────────────────────

export type ApiSuccess<T> = { ok: true; data: T }
export type ApiError = { ok: false; error: string; code?: string }
export type ApiResponse<T> = ApiSuccess<T> | ApiError

export type Paginated<T> = {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// ─── users ────────────────────────────────────────────────────────────────────

export type ApiUserRole = 'photographer' | 'platform_admin'
export type ApiUserStatus = 'active' | 'suspended'

export type ApiUser = {
  id: string
  email: string
  name: string
  initials: string
  role: ApiUserRole
  status: ApiUserStatus
  planId: PlanId
  brandingUsername: string
  createdAt: string
  updatedAt: string
}

export type CreateUserRequest = {
  email: string
  password: string
  name: string
  planId?: PlanId
}

export type UpdateUserRequest = Partial<
  Pick<ApiUser, 'name' | 'email' | 'planId' | 'status' | 'brandingUsername'>
>

// ─── plans ────────────────────────────────────────────────────────────────────

export type ApiPlan = {
  id: PlanId
  name: string
  priceMonthlyFcfa: number
  storageLimitBytes: number
  galleryLimit: number | null
  features: string[]
  active: boolean
  sortOrder: number
}

// ─── subscriptions ────────────────────────────────────────────────────────────

export type ApiSubscriptionStatus =
  | 'active'
  | 'trialing'
  | 'past_due'
  | 'canceled'
  | 'incomplete'

export type ApiSubscription = {
  id: string
  userId: string
  planId: PlanId
  status: ApiSubscriptionStatus
  currentPeriodStart: string
  currentPeriodEnd: string
  cancelAtPeriodEnd: boolean
  stripeCustomerId?: string
  stripeSubscriptionId?: string
  createdAt: string
}

export type ChangePlanRequest = {
  planId: PlanId
}

// ─── galleries ────────────────────────────────────────────────────────────────

export type ApiGallery = {
  id: string
  userId: string
  name: string
  slug: string
  status: CollectionStatus
  coverPhotoId?: string
  coverLayout: CoverLayout
  coverFocal: { x: number; y: number }
  eventDate?: string
  passwordHash?: string
  clientExclusive: boolean
  downloadEnabled: boolean
  favoritesEnabled: boolean
  showOnHomepage: boolean
  shareToken: string
  photoCount: number
  storageBytes: number
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

export type CreateGalleryRequest = {
  name: string
  slug?: string
  eventDate?: string
}

export type UpdateGalleryRequest = Partial<
  Pick<
    ApiGallery,
    | 'name'
    | 'slug'
    | 'status'
    | 'coverPhotoId'
    | 'coverLayout'
    | 'coverFocal'
    | 'eventDate'
    | 'clientExclusive'
    | 'downloadEnabled'
    | 'favoritesEnabled'
    | 'showOnHomepage'
  >
> & {
  password?: string
}

export type ApiGallerySet = {
  id: string
  galleryId: string
  name: string
  description: string
  sortOrder: number
  photoIds: string[]
}

// ─── photos ───────────────────────────────────────────────────────────────────

export type ApiPhoto = {
  id: string
  galleryId: string
  userId: string
  name: string
  storageKey: string
  publicUrl: string
  thumbUrl?: string
  width?: number
  height?: number
  sizeBytes: number
  starred: boolean
  sortOrder: number
  createdAt: string
}

export type UploadPhotoRequest = {
  galleryId: string
  setId?: string
  filename: string
  contentType: string
  sizeBytes: number
}

export type UploadPhotoResponse = {
  photo: ApiPhoto
  uploadUrl: string
  uploadHeaders?: Record<string, string>
}

// ─── Public endpoints ─────────────────────────────────────────────────────────

export type ApiPublicGallery = Pick<
  ApiGallery,
  | 'id'
  | 'name'
  | 'slug'
  | 'coverLayout'
  | 'coverFocal'
  | 'eventDate'
  | 'clientExclusive'
  | 'downloadEnabled'
  | 'favoritesEnabled'
> & {
  brandName: string
  biography?: string
  sets: ApiGallerySet[]
  photos: ApiPhoto[]
  watermarkEnabled: boolean
}

export type ApiHealthResponse = {
  ok: true
  service: 'pixeo'
  version?: string
}

// ─── Activity / billing ─────────────────────────────────────────────────────────

export type ApiGalleryActivity = {
  id: string
  galleryId: string
  type: 'view' | 'download' | 'favorite' | 'note'
  photoId?: string
  note?: string
  visitorHash: string
  createdAt: string
}

export type ApiBillingEvent = {
  id: string
  userId: string
  label: string
  amountFcfa: number
  status: 'paid' | 'pending' | 'failed'
  createdAt: string
}
