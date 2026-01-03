/**
 * Supabase Client Configuration
 *
 * This module initializes the Supabase client for authentication and database operations.
 * Environment variables must be configured in .env.local
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Validate configuration
if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('⚠️ Supabase credentials not configured')
  console.warn('Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local')
}

// Create Supabase client
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-key'
)

// Helper function to get auth token for API calls
export const getAuthToken = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || null
}

// Helper function to check if user is authenticated
export const isAuthenticated = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  return !!session
}

// Helper to make authenticated API calls to backend
export const apiCall = async (endpoint, options = {}) => {
  const token = await getAuthToken()

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}${endpoint}`,
    {
      ...options,
      headers,
    }
  )

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(error.detail || error.error || `HTTP ${response.status}`)
  }

  return response.json()
}
