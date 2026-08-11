'use client'

import { FormEvent, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { AppButton } from '@/components/app-button'
import { useGallery } from '@/lib/gallery-context'
import { useToast } from '@/components/toast-provider'

export function RegisterScreen() {
  const { register } = useGallery()
  const { notify } = useToast()
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await register(name, email, password)
    setLoading(false)
    if (!result.ok) {
      setError(result.error || 'Registration failed')
      notify(result.error || 'Registration failed', 'error')
      return
    }
    notify('Account created')
    router.replace('/collections')
  }

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={onSubmit}>
        <div className="brand auth-brand">
          <span className="brand-mark">◒</span>
          <b>Client Gallery</b>
        </div>
        <h1>Create account</h1>
        <label>
          Studio name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
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
            minLength={6}
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <AppButton type="submit" loading={loading}>
          Create account
        </AppButton>
        <p className="auth-foot">
          Already have an account? <Link href="/login">Sign in</Link>
        </p>
      </form>
    </div>
  )
}
