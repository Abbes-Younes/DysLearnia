import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// Get current user from browser session (checks cookies/localStorage)
export async function getMe() {
  const supabase = createClient()
  const { data: { session }, error } = await supabase.auth.getSession()
  
  if (error || !session) {
    return null
  }
  
  return {
    id: session.user.id,
    email: session.user.email || '',
    name: session.user.email?.split('@')[0] || 'User',
  }
}