'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { STOCK_PHOTOS, createSeedState, formatBytes, slugify, uid } from '@/lib/seed'
import {
  DEFAULT_PLANS,
  effectiveGalleryLimit,
  getPlan,
  type PlanDefinition,
  type PlanId,
} from '@/lib/plans'
import type {
  AppState,
  BrandingSettings,
  Campaign,
  Collection,
  CollectionStatus,
  Contact,
  CoverLayout,
  EmailShareRecord,
  FavoriteList,
  GalleryActivity,
  HomepageSettings,
  Photo,
  UserAccount,
} from '@/lib/types'

const STORAGE_KEY = 'client-gallery-app-v5'

type LimitCheck = { ok: boolean; error?: string }

type GalleryContextValue = {
  ready: boolean
  state: AppState
  isAuthenticated: boolean
  isAdmin: boolean
  usedStorageBytes: number
  usedStorageLabel: string
  login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>
  register: (name: string, email: string, password: string, planId?: PlanId) => Promise<{ ok: boolean; error?: string }>
  logout: () => void
  updateUser: (patch: Partial<UserAccount>) => void
  changePlan: (planId: PlanId) => void
  updatePlans: (plans: PlanDefinition[]) => void
  updateAccount: (id: string, patch: Partial<UserAccount>) => void
  createPlatformAccount: (input: {
    name: string
    email: string
    password: string
    role: 'photographer' | 'platform_admin'
    planId?: PlanId
  }) => { ok: boolean; error?: string; account?: UserAccount }
  canCreateGallery: () => LimitCheck
  canUploadBytes: (bytes: number) => LimitCheck
  createCollection: (input?: { name?: string; eventDate?: string }) => Collection
  updateCollection: (id: string, patch: Partial<Collection>) => void
  deleteCollection: (id: string) => void
  toggleCollectionStar: (id: string) => void
  setCollectionStatus: (id: string, status: CollectionStatus) => void
  addSet: (collectionId: string, name?: string) => string
  updateSet: (
    collectionId: string,
    setId: string,
    patch: Partial<{ name: string; description: string; photoIds: string[] }>,
  ) => void
  renameSet: (collectionId: string, setId: string, name: string) => void
  deleteSet: (collectionId: string, setId: string) => void
  reorderSets: (collectionId: string, fromIndex: number, toIndex: number) => void
  addPhotosToCollection: (
    collectionId: string,
    files: { name: string; src: string; sizeBytes: number }[],
    setId?: string,
  ) => string[]
  addStockPhotos: (collectionId: string, count?: number, setId?: string) => void
  removePhotosFromCollection: (collectionId: string, photoIds: string[]) => void
  movePhotosToSet: (collectionId: string, photoIds: string[], targetSetId: string) => void
  updatePhoto: (photoId: string, patch: Partial<Photo>) => void
  replacePhoto: (photoId: string, file: { name: string; src: string; sizeBytes: number }) => void
  setCoverPhoto: (collectionId: string, photoId: string) => void
  togglePhotoStar: (photoId: string) => void
  deletePhotos: (photoIds: string[]) => void
  getCollectionPhotos: (collection: Collection, setId?: string) => Photo[]
  getCoverSrc: (collection: Collection) => string | undefined
  updateHomepage: (patch: Partial<HomepageSettings>) => void
  updateBranding: (patch: Partial<BrandingSettings>) => void
  createCampaign: (input?: Partial<Campaign>) => Campaign
  updateCampaign: (id: string, patch: Partial<Campaign>) => void
  deleteCampaign: (id: string) => void
  addContact: (input: { email: string; name: string }) => { ok: boolean; error?: string }
  deleteContact: (id: string) => void
  markNotificationsRead: () => void
  addNotification: (message: string) => void
  duplicateCollection: (id: string) => Collection | null
  recordEmailShare: (input: Omit<EmailShareRecord, 'id' | 'sentAt'>) => void
  savePreset: (name: string, coverLayout: CoverLayout) => void
  applyPreset: (collectionId: string, presetId: string) => void
  logGalleryActivity: (input: Omit<GalleryActivity, 'id' | 'createdAt' | 'visitorLabel'> & { visitorLabel?: string }) => void
  addFavoriteList: (collectionId: string, input: { name: string; selectionLimit: number }) => FavoriteList
  deleteFavoriteList: (collectionId: string, listId: string) => void
  resetDemoData: () => void
}

const GalleryContext = createContext<GalleryContextValue | null>(null)

function loadState(): AppState {
  if (typeof window === 'undefined') return createSeedState()
  try {
    const raw =
      window.localStorage.getItem(STORAGE_KEY) ||
      window.localStorage.getItem('client-gallery-app-v4') ||
      window.localStorage.getItem('client-gallery-app-v3') ||
      window.localStorage.getItem('client-gallery-app-v2') ||
      window.localStorage.getItem('client-gallery-app-v1')
    if (!raw) return createSeedState()
    const seed = createSeedState()
    const parsed = JSON.parse(raw) as Partial<AppState>
    return {
      ...seed,
      ...parsed,
      emailHistory: parsed.emailHistory ?? [],
      galleryActivities: parsed.galleryActivities ?? [],
      presets: parsed.presets?.length ? parsed.presets : seed.presets,
      homepage: { ...seed.homepage, ...parsed.homepage },
      branding: { ...seed.branding, ...parsed.branding },
      accounts: parsed.accounts?.length ? parsed.accounts : seed.accounts,
      plans: parsed.plans?.length ? parsed.plans : seed.plans,
      billingHistory: parsed.billingHistory ?? seed.billingHistory,
      collections: (parsed.collections ?? seed.collections).map((c) => ({
        ...seed.collections[0],
        ...c,
        coverLayout: c.coverLayout ?? 'center',
        coverFocal: c.coverFocal ?? { x: 50, y: 50 },
        categoryTags: c.categoryTags ?? [],
        contactIds: c.contactIds ?? [],
        clientExclusive: c.clientExclusive ?? false,
        downloadEnabled: c.downloadEnabled ?? true,
        downloadHighRes: c.downloadHighRes ?? true,
        downloadHighResSize: c.downloadHighResSize ?? '3600',
        downloadWebSize: c.downloadWebSize ?? true,
        downloadWebSizePx: c.downloadWebSizePx ?? '1024',
        downloadPinEnabled: c.downloadPinEnabled ?? false,
        downloadPin: c.downloadPin ?? Math.random().toString().slice(2, 6),
        favoritesEnabled: c.favoritesEnabled ?? true,
        favoriteNotesEnabled: c.favoriteNotesEnabled ?? true,
        favoriteLists: c.favoriteLists ?? [],
        storeEnabled: c.storeEnabled ?? false,
        sets: (c.sets ?? []).map((s) => ({ ...s, description: s.description ?? '' })),
      })),
    }
  } catch {
    return createSeedState()
  }
}

function persist(state: AppState) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

async function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export async function readImageFiles(fileList: FileList | File[]) {
  const files = Array.from(fileList).filter((f) => f.type.startsWith('image/'))
  const results: { name: string; src: string; sizeBytes: number }[] = []
  for (const file of files) {
    const src = await fileToDataUrl(file)
    results.push({ name: file.name, src, sizeBytes: file.size })
  }
  return results
}

export function GalleryProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false)
  const [state, setState] = useState<AppState>(createSeedState)

  useEffect(() => {
    setState(loadState())
    setReady(true)
  }, [])

  useEffect(() => {
    if (!ready) return
    persist(state)
  }, [state, ready])

  const usedStorageBytes = useMemo(
    () => state.photos.reduce((sum, photo) => sum + photo.sizeBytes, 0),
    [state.photos],
  )

  const commit = useCallback((updater: (prev: AppState) => AppState) => {
    setState((prev) => updater(prev))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const normalized = email.trim().toLowerCase()
    if (!normalized || !password) {
      return { ok: false, error: 'Email and password are required.' }
    }
    let result: { ok: boolean; error?: string } = { ok: false, error: 'Invalid credentials.' }
    setState((prev) => {
      const account = prev.accounts.find(
        (a) => a.email.toLowerCase() === normalized && a.password === password,
      )
      if (account) {
        if (account.status === 'suspended') {
          result = { ok: false, error: 'This account has been suspended.' }
          return prev
        }
        result = { ok: true }
        const plan = getPlan(account.planId, prev.plans)
        return { ...prev, user: account, storageLimitBytes: plan.storageLimitBytes }
      }
      if (prev.user && prev.user.email.toLowerCase() === normalized && prev.user.password === password) {
        result = { ok: true }
        return prev
      }
      return prev
    })
    await new Promise((r) => setTimeout(r, 450))
    return result
  }, [])

  const register = useCallback(async (name: string, email: string, password: string, planId: PlanId = 'free') => {
    const normalized = email.trim().toLowerCase()
    if (!name.trim() || !normalized || password.length < 6) {
      return { ok: false, error: 'Name, email and password (6+ chars) are required.' }
    }
    await new Promise((r) => setTimeout(r, 500))
    const plan = getPlan(planId, DEFAULT_PLANS)
    const now = new Date().toISOString()
    setState((prev) => {
      const user: UserAccount = {
        id: uid('user'),
        name: name.trim(),
        email: normalized,
        password,
        initials: name.trim().slice(0, 1).toUpperCase(),
        planId,
        role: 'photographer',
        status: 'active',
        createdAt: now,
      }
      return {
        ...prev,
        user,
        accounts: [...prev.accounts, user],
        storageLimitBytes: plan.storageLimitBytes,
        homepage: { ...prev.homepage, brandName: name.trim().toUpperCase() },
        branding: {
          ...prev.branding,
          username: slugify(name).replace(/-/g, '') || 'studio',
        },
        notifications: [
          {
            id: uid('n'),
            message: 'Account created — start with your first collection',
            read: false,
            createdAt: now,
          },
          ...prev.notifications,
        ],
      }
    })
    return { ok: true }
  }, [])

  const logout = useCallback(() => {
    window.sessionStorage.removeItem('gallery-session')
  }, [])

  const ensureSession = useCallback(() => {
    if (typeof window === 'undefined') return false
    return window.sessionStorage.getItem('gallery-session') === '1'
  }, [])

  const [sessionActive, setSessionActive] = useState(false)

  useEffect(() => {
    setSessionActive(ensureSession())
  }, [ensureSession])

  const loginWithSession: typeof login = useCallback(
    async (email, password) => {
      const res = await login(email, password)
      if (res.ok) {
        window.sessionStorage.setItem('gallery-session', '1')
        setSessionActive(true)
      }
      return res
    },
    [login],
  )

  const registerWithSession: typeof register = useCallback(
    async (name, email, password, planId) => {
      const res = await register(name, email, password, planId)
      if (res.ok) {
        window.sessionStorage.setItem('gallery-session', '1')
        setSessionActive(true)
      }
      return res
    },
    [register],
  )

  const logoutWithSession = useCallback(() => {
    window.sessionStorage.removeItem('gallery-session')
    setSessionActive(false)
  }, [])

  const value = useMemo<GalleryContextValue>(() => {
    const isAuthenticated = Boolean(state.user) && sessionActive
    const isAdmin = state.user?.role === 'platform_admin'

    const changePlan = (planId: PlanId) => {
      const plan = getPlan(planId, state.plans)
      commit((prev) => {
        if (!prev.user) return prev
        const updatedUser = { ...prev.user, planId }
        return {
          ...prev,
          user: updatedUser,
          storageLimitBytes: plan.storageLimitBytes,
          accounts: prev.accounts.map((a) => (a.id === updatedUser.id ? updatedUser : a)),
          billingHistory: [
            {
              id: uid('bill'),
              label: `${plan.name} plan — monthly`,
              amountFcfa: plan.priceMonthlyFcfa,
              createdAt: new Date().toISOString(),
              status: 'paid' as const,
            },
            ...prev.billingHistory,
          ],
        }
      })
    }

    const updatePlans = (plans: PlanDefinition[]) => {
      commit((prev) => ({ ...prev, plans }))
    }

    const updateAccount = (id: string, patch: Partial<UserAccount>) => {
      commit((prev) => ({
        ...prev,
        accounts: prev.accounts.map((a) => (a.id === id ? { ...a, ...patch } : a)),
        user: prev.user?.id === id ? { ...prev.user, ...patch } : prev.user,
      }))
    }

    const createPlatformAccount = (input: {
      name: string
      email: string
      password: string
      role: 'photographer' | 'platform_admin'
      planId?: PlanId
    }): { ok: boolean; error?: string; account?: UserAccount } => {
      const name = input.name.trim()
      const email = input.email.trim().toLowerCase()
      const password = input.password
      if (!name || !email || password.length < 6) {
        return { ok: false, error: 'Name, email and password (6+ chars) are required.' }
      }
      if (state.accounts.some((a) => a.email.toLowerCase() === email)) {
        return { ok: false, error: 'An account with this email already exists.' }
      }
      const now = new Date().toISOString()
      const planId = input.role === 'platform_admin' ? 'studio' : input.planId || 'free'
      const account: UserAccount = {
        id: uid('user'),
        name,
        email,
        password,
        initials: name.slice(0, 1).toUpperCase(),
        planId,
        role: input.role,
        status: 'active',
        createdAt: now,
      }
      commit((prev) => ({
        ...prev,
        accounts: [account, ...prev.accounts],
        notifications: [
          {
            id: uid('n'),
            message: `${input.role === 'platform_admin' ? 'Admin' : 'Photographer'} “${name}” created`,
            read: false,
            createdAt: now,
          },
          ...prev.notifications,
        ],
      }))
      return { ok: true, account }
    }

    const canCreateGallery = (): LimitCheck => {
      if (!state.user) return { ok: false, error: 'Sign in to create galleries.' }
      const plan = getPlan(state.user.planId, state.plans)
      const limit = effectiveGalleryLimit(plan)
      if (state.collections.length >= limit) {
        return { ok: false, error: `Gallery limit reached (${limit}). Upgrade your plan.` }
      }
      return { ok: true }
    }

    const canUploadBytes = (bytes: number): LimitCheck => {
      if (usedStorageBytes + bytes > state.storageLimitBytes) {
        return { ok: false, error: 'Storage limit exceeded. Upgrade your plan.' }
      }
      return { ok: true }
    }

    return {
      ready,
      state,
      isAuthenticated,
      isAdmin,
      usedStorageBytes,
      usedStorageLabel: `${formatBytes(usedStorageBytes)} of ${formatBytes(state.storageLimitBytes)} used`,
      login: loginWithSession,
      register: registerWithSession,
      logout: logoutWithSession,
      changePlan,
      updatePlans,
      updateAccount,
      createPlatformAccount,
      canCreateGallery,
      canUploadBytes,
      updateUser: (patch) =>
        commit((prev) => {
          if (!prev.user) return prev
          const user = { ...prev.user, ...patch }
          return {
            ...prev,
            user,
            accounts: prev.accounts.map((a) => (a.id === user.id ? user : a)),
          }
        }),
      createCollection: (input) => {
        const name = input?.name?.trim() || 'Untitled Collection'
        const now = new Date().toISOString()
        const collection: Collection = {
          id: uid('col'),
          name,
          slug: slugify(name) + '-' + uid('s').slice(-4),
          coverLayout: 'center',
          coverFocal: { x: 50, y: 50 },
          eventDate: input?.eventDate,
          status: 'draft',
          starred: false,
          showOnHomepage: false,
          categoryTags: [],
          contactIds: [],
          sets: [{ id: uid('set'), name: 'Highlights', description: '', photoIds: [] }],
          createdAt: now,
          updatedAt: now,
          password: '',
          clientExclusive: false,
          downloadEnabled: true,
          downloadHighRes: true,
          downloadHighResSize: '3600',
          downloadWebSize: true,
          downloadWebSizePx: '1024',
          downloadPinEnabled: false,
          downloadPin: Math.random().toString().slice(2, 6),
          favoritesEnabled: true,
          favoriteNotesEnabled: true,
          favoriteLists: [],
          storeEnabled: false,
          shareToken: uid('share'),
        }
        commit((prev) => ({
          ...prev,
          collections: [collection, ...prev.collections],
          notifications: [
            {
              id: uid('n'),
              message: `Collection “${name}” created`,
              read: false,
              createdAt: now,
            },
            ...prev.notifications,
          ],
        }))
        return collection
      },
      updateCollection: (id, patch) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === id
              ? {
                  ...c,
                  ...patch,
                  slug: patch.slug ?? (patch.name ? slugify(patch.name) : c.slug),
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        })),
      deleteCollection: (id) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.filter((c) => c.id !== id),
          photos: prev.photos.map((p) => ({
            ...p,
            collectionIds: p.collectionIds.filter((cid) => cid !== id),
          })),
        })),
      toggleCollectionStar: (id) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === id ? { ...c, starred: !c.starred, updatedAt: new Date().toISOString() } : c,
          ),
        })),
      setCollectionStatus: (id, status) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === id ? { ...c, status, updatedAt: new Date().toISOString() } : c,
          ),
        })),
      addSet: (collectionId, name = 'New Set') => {
        const setId = uid('set')
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  sets: [...c.sets, { id: setId, name, description: '', photoIds: [] }],
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        }))
        return setId
      },
      updateSet: (collectionId, setId, patch) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  sets: c.sets.map((s) => (s.id === setId ? { ...s, ...patch } : s)),
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        })),
      renameSet: (collectionId, setId, name) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  sets: c.sets.map((s) => (s.id === setId ? { ...s, name } : s)),
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        })),
      deleteSet: (collectionId, setId) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  sets: c.sets.length <= 1 ? c.sets : c.sets.filter((s) => s.id !== setId),
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        })),
      reorderSets: (collectionId, fromIndex, toIndex) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) => {
            if (c.id !== collectionId) return c
            const sets = [...c.sets]
            const [item] = sets.splice(fromIndex, 1)
            if (!item) return c
            sets.splice(toIndex, 0, item)
            return { ...c, sets, updatedAt: new Date().toISOString() }
          }),
        })),
      addPhotosToCollection: (collectionId, files, setId) => {
        const now = new Date().toISOString()
        const newPhotos: Photo[] = files.map((file) => ({
          id: uid('photo'),
          src: file.src,
          name: file.name,
          starred: false,
          createdAt: now,
          sizeBytes: file.sizeBytes,
          collectionIds: [collectionId],
        }))
        const newIds = newPhotos.map((p) => p.id)
        commit((prev) => {
          const collection = prev.collections.find((c) => c.id === collectionId)
          if (!collection) return prev
          const targetSetId = setId || collection.sets[0]?.id
          return {
            ...prev,
            photos: [...newPhotos, ...prev.photos],
            collections: prev.collections.map((c) => {
              if (c.id !== collectionId) return c
              return {
                ...c,
                coverPhotoId: c.coverPhotoId || newIds[0],
                sets: c.sets.map((s) =>
                  s.id === targetSetId ? { ...s, photoIds: [...s.photoIds, ...newIds] } : s,
                ),
                updatedAt: now,
              }
            }),
          }
        })
        return newIds
      },
      addStockPhotos: (collectionId, count = 4, setId) => {
        const files = STOCK_PHOTOS.slice(0, count).map((src, i) => ({
          name: `Stock ${i + 1}.jpg`,
          src,
          sizeBytes: 1_500_000,
        }))
        setState((prev) => {
          const collection = prev.collections.find((c) => c.id === collectionId)
          if (!collection) return prev
          const targetSetId = setId || collection.sets[0]?.id
          const now = new Date().toISOString()
          const newPhotos: Photo[] = files.map((file) => ({
            id: uid('photo'),
            src: file.src,
            name: file.name,
            starred: false,
            createdAt: now,
            sizeBytes: file.sizeBytes,
            collectionIds: [collectionId],
          }))
          const newIds = newPhotos.map((p) => p.id)
          return {
            ...prev,
            photos: [...newPhotos, ...prev.photos],
            collections: prev.collections.map((c) => {
              if (c.id !== collectionId) return c
              return {
                ...c,
                coverPhotoId: c.coverPhotoId || newIds[0],
                sets: c.sets.map((s) =>
                  s.id === targetSetId ? { ...s, photoIds: [...s.photoIds, ...newIds] } : s,
                ),
                updatedAt: now,
              }
            }),
          }
        })
      },
      removePhotosFromCollection: (collectionId, photoIds) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  sets: c.sets.map((s) => ({
                    ...s,
                    photoIds: s.photoIds.filter((id) => !photoIds.includes(id)),
                  })),
                  coverPhotoId:
                    c.coverPhotoId && photoIds.includes(c.coverPhotoId)
                      ? undefined
                      : c.coverPhotoId,
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
          photos: prev.photos.map((p) =>
            photoIds.includes(p.id)
              ? { ...p, collectionIds: p.collectionIds.filter((id) => id !== collectionId) }
              : p,
          ),
        })),
      movePhotosToSet: (collectionId, photoIds, targetSetId) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) => {
            if (c.id !== collectionId) return c
            return {
              ...c,
              sets: c.sets.map((s) => {
                const without = s.photoIds.filter((id) => !photoIds.includes(id))
                if (s.id === targetSetId) {
                  const merged = [...without]
                  photoIds.forEach((id) => {
                    if (!merged.includes(id)) merged.push(id)
                  })
                  return { ...s, photoIds: merged }
                }
                return { ...s, photoIds: without }
              }),
              updatedAt: new Date().toISOString(),
            }
          }),
        })),
      updatePhoto: (photoId, patch) =>
        commit((prev) => ({
          ...prev,
          photos: prev.photos.map((p) => (p.id === photoId ? { ...p, ...patch } : p)),
        })),
      replacePhoto: (photoId, file) =>
        commit((prev) => ({
          ...prev,
          photos: prev.photos.map((p) =>
            p.id === photoId
              ? { ...p, src: file.src, name: file.name, sizeBytes: file.sizeBytes }
              : p,
          ),
        })),
      setCoverPhoto: (collectionId, photoId) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? { ...c, coverPhotoId: photoId, updatedAt: new Date().toISOString() }
              : c,
          ),
        })),
      togglePhotoStar: (photoId) =>
        commit((prev) => ({
          ...prev,
          photos: prev.photos.map((p) =>
            p.id === photoId ? { ...p, starred: !p.starred } : p,
          ),
        })),
      deletePhotos: (photoIds) =>
        commit((prev) => ({
          ...prev,
          photos: prev.photos.filter((p) => !photoIds.includes(p.id)),
          collections: prev.collections.map((c) => ({
            ...c,
            sets: c.sets.map((s) => ({
              ...s,
              photoIds: s.photoIds.filter((id) => !photoIds.includes(id)),
            })),
            coverPhotoId:
              c.coverPhotoId && photoIds.includes(c.coverPhotoId) ? undefined : c.coverPhotoId,
          })),
        })),
      getCollectionPhotos: (collection, setId) => {
        const set = setId
          ? collection.sets.find((s) => s.id === setId)
          : collection.sets[0]
        const ids = set?.photoIds ?? []
        const map = new Map(state.photos.map((p) => [p.id, p]))
        return ids.map((id) => map.get(id)).filter(Boolean) as Photo[]
      },
      getCoverSrc: (collection) => {
        if (collection.coverPhotoId) {
          return state.photos.find((p) => p.id === collection.coverPhotoId)?.src
        }
        const firstId = collection.sets[0]?.photoIds[0]
        return firstId ? state.photos.find((p) => p.id === firstId)?.src : undefined
      },
      updateHomepage: (patch) =>
        commit((prev) => ({ ...prev, homepage: { ...prev.homepage, ...patch } })),
      updateBranding: (patch) =>
        commit((prev) => ({ ...prev, branding: { ...prev.branding, ...patch } })),
      createCampaign: (input) => {
        const campaign: Campaign = {
          id: uid('camp'),
          name: input?.name || 'Untitled campaign',
          subject: input?.subject || '',
          status: 'draft',
          body: input?.body || '',
          createdAt: new Date().toISOString(),
        }
        commit((prev) => ({ ...prev, campaigns: [campaign, ...prev.campaigns] }))
        return campaign
      },
      updateCampaign: (id, patch) =>
        commit((prev) => ({
          ...prev,
          campaigns: prev.campaigns.map((c) => (c.id === id ? { ...c, ...patch } : c)),
        })),
      deleteCampaign: (id) =>
        commit((prev) => ({
          ...prev,
          campaigns: prev.campaigns.filter((c) => c.id !== id),
        })),
      addContact: ({ email, name }) => {
        const normalized = email.trim().toLowerCase()
        if (!normalized.includes('@')) return { ok: false, error: 'Enter a valid email.' }
        let error: string | undefined
        commit((prev) => {
          if (prev.contacts.some((c) => c.email === normalized)) {
            error = 'Contact already exists.'
            return prev
          }
          const contact: Contact = {
            id: uid('contact'),
            email: normalized,
            name: name.trim() || normalized,
            optedIn: true,
            createdAt: new Date().toISOString(),
          }
          return { ...prev, contacts: [contact, ...prev.contacts] }
        })
        return error ? { ok: false, error } : { ok: true }
      },
      deleteContact: (id) =>
        commit((prev) => ({
          ...prev,
          contacts: prev.contacts.filter((c) => c.id !== id),
        })),
      markNotificationsRead: () =>
        commit((prev) => ({
          ...prev,
          notifications: prev.notifications.map((n) => ({ ...n, read: true })),
        })),
      addNotification: (message) =>
        commit((prev) => ({
          ...prev,
          notifications: [
            {
              id: uid('n'),
              message,
              read: false,
              createdAt: new Date().toISOString(),
            },
            ...prev.notifications,
          ],
        })),
      duplicateCollection: (id) => {
        let created: Collection | null = null
        commit((prev) => {
          const source = prev.collections.find((c) => c.id === id)
          if (!source) return prev
          const now = new Date().toISOString()
          created = {
            ...source,
            id: uid('col'),
            name: `${source.name} Copy`,
            slug: slugify(`${source.name}-copy`) + '-' + uid('s').slice(-4),
            status: 'draft',
            shareToken: uid('share'),
            createdAt: now,
            updatedAt: now,
            sets: source.sets.map((s) => ({
              ...s,
              id: uid('set'),
              photoIds: [...s.photoIds],
            })),
          }
          return {
            ...prev,
            collections: [created!, ...prev.collections],
          }
        })
        return created
      },
      recordEmailShare: (input) =>
        commit((prev) => ({
          ...prev,
          emailHistory: [
            {
              ...input,
              id: uid('email'),
              sentAt: new Date().toISOString(),
            },
            ...(prev.emailHistory ?? []),
          ],
          notifications: [
            {
              id: uid('n'),
              message:
                input.status === 'scheduled'
                  ? `Email to ${input.to} scheduled`
                  : `Gallery emailed to ${input.to}`,
              read: false,
              createdAt: new Date().toISOString(),
            },
            ...prev.notifications,
          ],
        })),
      savePreset: (name, coverLayout) =>
        commit((prev) => ({
          ...prev,
          presets: [{ id: uid('preset'), name, coverLayout }, ...prev.presets],
        })),
      applyPreset: (collectionId, presetId) =>
        commit((prev) => {
          const preset = prev.presets.find((p) => p.id === presetId)
          if (!preset) return prev
          return {
            ...prev,
            collections: prev.collections.map((c) =>
              c.id === collectionId
                ? { ...c, coverLayout: preset.coverLayout, updatedAt: new Date().toISOString() }
                : c,
            ),
          }
        }),
      logGalleryActivity: (input) =>
        commit((prev) => ({
          ...prev,
          galleryActivities: [
            {
              id: uid('act'),
              visitorLabel: input.visitorLabel || 'Client visitor',
              createdAt: new Date().toISOString(),
              collectionId: input.collectionId,
              type: input.type,
              photoId: input.photoId,
              photoName: input.photoName,
              note: input.note,
            },
            ...(prev.galleryActivities ?? []),
          ].slice(0, 200),
        })),
      addFavoriteList: (collectionId, input) => {
        const list: FavoriteList = {
          id: uid('flist'),
          name: input.name.trim() || 'Favorites',
          selectionLimit: Math.max(1, input.selectionLimit || 10),
          createdAt: new Date().toISOString(),
        }
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  favoriteLists: [...(c.favoriteLists ?? []), list],
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        }))
        return list
      },
      deleteFavoriteList: (collectionId, listId) =>
        commit((prev) => ({
          ...prev,
          collections: prev.collections.map((c) =>
            c.id === collectionId
              ? {
                  ...c,
                  favoriteLists: (c.favoriteLists ?? []).filter((l) => l.id !== listId),
                  updatedAt: new Date().toISOString(),
                }
              : c,
          ),
        })),
      resetDemoData: () => {
        const seed = createSeedState()
        setState(seed)
        persist(seed)
        window.sessionStorage.setItem('gallery-session', '1')
        setSessionActive(true)
      },
    }
  }, [
    ready,
    state,
    sessionActive,
    usedStorageBytes,
    commit,
    loginWithSession,
    registerWithSession,
    logoutWithSession,
  ])

  return <GalleryContext.Provider value={value}>{children}</GalleryContext.Provider>
}

export function useGallery() {
  const ctx = useContext(GalleryContext)
  if (!ctx) throw new Error('useGallery must be used within GalleryProvider')
  return ctx
}
