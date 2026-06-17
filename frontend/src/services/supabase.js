import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://byczmezlfqzlubegjdow.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5Y3ptZXpsZnF6bHViZWdqZG93Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2NjkxNjMsImV4cCI6MjA5NzI0NTE2M30.FrtV77q3WLz8BYnM9_Fbl7jzDTIPUQ3bu2J2SfyA8Tk'

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
})

export default supabase
