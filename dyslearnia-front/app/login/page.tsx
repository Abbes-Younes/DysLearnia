'use client'
import { useState, useEffect } from 'react'
import { createClient, getMe } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import * as queries from '@/lib/supabase/queries'

export default function LoginPage() {
  const router = useRouter()
  const supabase = createClient()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [checkLoading, setCheckLoading] = useState(true)

  // Check if already authenticated using getMe and redirect
  useEffect(() => {
    async function checkAuth() {
      const me = await getMe()
      setCheckLoading(false)
      if (me) {
        router.push('/workflows')
      }
    }
    checkAuth()
  }, [router])

  // Show loading while checking auth status
  if (checkLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-4 border-[var(--foreground)] mx-auto mb-4"></div>
          <p className="text-[var(--text-secondary)] font-bold">Checking authentication...</p>
        </div>
      </div>
    )
  }

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter both email and password')
      return
    }

    setLoading(true)
    setError('')

    try {
      const { error, data } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        setError(error.message)
        setLoading(false)
        return
      }

      if (data.user) {
        // Check if user exists in our database, create if not
        try {
          await queries.getUser(data.user.id)
        } catch {
          // User doesn't exist, create them
          try {
            await queries.createUser(data.user.id, email, email.split('@')[0])
          } catch (e) {
            console.error('Error creating user:', e)
          }
        }

        // Use window.location for a more reliable redirect
        setTimeout(() => {
          window.location.href = '/workflows'
        }, 500)
      }
    } catch (e) {
      setError('An unexpected error occurred')
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
      <div className="bg-white border-3 border-[var(--foreground)] rounded-xl shadow-[5px_5px_0px_0px_var(--foreground)] p-8 w-full max-w-md">
        <h1 className="text-3xl font-black text-center mb-2 text-[var(--accent)]">DysLearnia</h1>
        <p className="text-center text-[var(--text-secondary)] font-semibold mb-8">Sign in to your account</p>

        {error && (
          <div className="bg-[var(--error)]/10 text-[var(--error)] text-sm font-bold p-3 rounded-lg border-2 border-[var(--error)] mb-4">
            {error}
          </div>
        )}

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-bold text-[var(--foreground)] mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full border-2 border-[var(--foreground)] rounded-lg px-4 py-2.5 bg-white font-medium focus:outline-none focus:shadow-[3px_3px_0px_0px_var(--accent)] transition-shadow"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-[var(--foreground)] mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full border-2 border-[var(--foreground)] rounded-lg px-4 py-2.5 bg-white font-medium focus:outline-none focus:shadow-[3px_3px_0px_0px_var(--accent)] transition-shadow"
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-[var(--accent)] text-white py-3 rounded-lg font-black text-lg border-2 border-[var(--foreground)] shadow-[4px_4px_0px_0px_var(--foreground)] hover:shadow-[2px_2px_0px_0px_var(--foreground)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all disabled:opacity-50 disabled:hover:shadow-[4px_4px_0px_0px_var(--foreground)] disabled:hover:translate-x-0 disabled:hover:translate-y-0"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>

        <p className="text-center text-sm font-semibold text-[var(--text-secondary)] mt-6">
          Don{"'"}t have an account?{' '}
          <Link href="/signup" className="text-[var(--accent)] font-bold hover:underline decoration-2 underline-offset-2">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}