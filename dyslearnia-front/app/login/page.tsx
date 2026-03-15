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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Checking authentication...</p>
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
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-2 text-indigo-600">LectureLens</h1>
        <p className="text-center text-gray-500 mb-8">Sign in to your account</p>

        {error && (
          <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Don{"'"}t have an account?{' '}
          <Link href="/signup" className="text-indigo-600 font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}