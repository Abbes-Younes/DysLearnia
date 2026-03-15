'use client'
import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import * as queries from '@/lib/supabase/queries'

export default function SignupPage() {
  const router = useRouter()
  const supabase = createClient()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Check if already authenticated and redirect
  useEffect(() => {
    async function checkAuth() {
      const { data: { session } } = await supabase.auth.getSession()
      if (session) {
        router.push('/workflows')
        return
      }
    }
    checkAuth()
  }, [router, supabase])

  const handleSignup = async () => {
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    if (!name.trim()) {
      setError('Please enter your name')
      return
    }
    setLoading(true)
    setError('')
    
    const { error, data } = await supabase.auth.signUp({ 
      email, 
      password,
      options: {
        data: {
          name: name.trim(),
        }
      }
    })
    
    if (error) {
      setError(error.message)
      setLoading(false)
    } else if (data.user) {
      // Create user in our database
      try {
        await queries.createUser(data.user.id, email, name.trim())
        router.push('/workflows')
      } catch (e) {
        console.error('Error creating user:', e)
        // Continue anyway - user was created in auth
        router.push('/workflows')
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
      <div className="bg-white border-3 border-[var(--foreground)] rounded-xl shadow-[5px_5px_0px_0px_var(--foreground)] p-8 w-full max-w-md">
        <h1 className="text-3xl font-black text-center mb-2 text-[var(--accent)]">DysLearnia</h1>
        <p className="text-center text-[var(--text-secondary)] font-semibold mb-8">Create your account</p>

        {error && (
          <div className="bg-[var(--error)]/10 text-[var(--error)] text-sm font-bold p-3 rounded-lg border-2 border-[var(--error)] mb-4">
            {error}
          </div>
        )}

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-bold text-[var(--foreground)] mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              className="w-full border-2 border-[var(--foreground)] rounded-lg px-4 py-2.5 bg-white font-medium focus:outline-none focus:shadow-[3px_3px_0px_0px_var(--accent)] transition-shadow"
            />
          </div>
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
          <div>
            <label className="block text-sm font-bold text-[var(--foreground)] mb-1">Confirm Password</label>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="••••••••"
              className="w-full border-2 border-[var(--foreground)] rounded-lg px-4 py-2.5 bg-white font-medium focus:outline-none focus:shadow-[3px_3px_0px_0px_var(--accent)] transition-shadow"
            />
          </div>

          <button
            onClick={handleSignup}
            disabled={loading}
            className="w-full bg-[var(--accent)] text-white py-3 rounded-lg font-black text-lg border-2 border-[var(--foreground)] shadow-[4px_4px_0px_0px_var(--foreground)] hover:shadow-[2px_2px_0px_0px_var(--foreground)] hover:translate-x-[2px] hover:translate-y-[2px] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all disabled:opacity-50 disabled:hover:shadow-[4px_4px_0px_0px_var(--foreground)] disabled:hover:translate-x-0 disabled:hover:translate-y-0"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </div>

        <p className="text-center text-sm font-semibold text-[var(--text-secondary)] mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-[var(--accent)] font-bold hover:underline decoration-2 underline-offset-2">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
