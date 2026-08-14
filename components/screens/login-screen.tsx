'use client'

import { FormEvent, useState } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function LoginScreen() {
  const { login } = useGallery()
  const { notify } = useToast()
  const router = useRouter()
  const params = useSearchParams()
  const [email, setEmail] = useState('demo@pixeo.app')
  const [password, setPassword] = useState('demo1234')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await login(email, password)
    setLoading(false)
    if (!result.ok) {
      setError(result.error || 'Login failed')
      notify(result.error || 'Login failed', 'error')
      return
    }
    notify('Welcome back')
    const next = params.get('next')
    const normalized = email.trim().toLowerCase()
    if (next) {
      router.replace(next)
    } else if (normalized === 'admin@pixeo.app') {
      router.replace('/admin')
    } else {
      router.replace('/collections')
    }
  }

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={onSubmit}>
        <div className="brand auth-brand">
          <span className="brand-mark">◒</span>
          <b>Pixeo</b>
        </div>
        <h1>Sign in</h1>
        <p className="auth-sub">
          Demo: demo@pixeo.app / demo1234<br />
          Admin: admin@pixeo.app / admin1234
        </p>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <AppButton type="submit" loading={loading}>
          Sign in
        </AppButton>
        <p className="auth-foot">
          New here? <Link href="/register">Create an account</Link>
        </p>
        <p className="auth-foot">
          <Link href="/">Back to homepage</Link>
        </p>
      </form>
    </div>
  )
}
