'use client'

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { Check, Info, X } from 'lucide-react'
import type { ToastTone } from '@/lib/types'

type ToastItem = {
  id: string
  message: string
  tone: ToastTone
}

type ToastContextValue = {
  notify: (message: string, tone?: ToastTone) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const notify = useCallback((message: string, tone: ToastTone = 'success') => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
    setToasts((prev) => [...prev, { id, message, tone }])
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 2800)
  }, [])

  const value = useMemo(() => ({ notify }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-stack" aria-live="polite">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast ${toast.tone}`} role="status">
            {toast.tone === 'error' ? <X size={17} /> : toast.tone === 'info' ? <Info size={17} /> : <Check size={17} />}
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
