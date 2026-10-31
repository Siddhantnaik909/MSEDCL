import { useEffect, useState } from 'react'
import { ApiError, requestJson } from '../lib/api/client'
import { AppShell } from '../components/AppShell'
import { AdminPage } from '../features/admin/AdminPage'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { LoginPage } from '../features/auth/LoginPage'
import type { SessionUser } from '../features/auth/types'
import './App.css'

const LEGACY_APP_URL =
  import.meta.env.VITE_LEGACY_APP_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin)

export default function App() {
  const [user, setUser] = useState<SessionUser | null>(null)
  const isLoginPage = window.location.pathname === '/login'
  const isAdminPage = window.location.pathname.startsWith('/admin/')
  const [loading, setLoading] = useState(!isLoginPage)

  useEffect(() => {
    if (isLoginPage) return

    let active = true
    requestJson<SessionUser>('/auth/me')
      .then((currentUser) => {
        if (!active) return
        if (currentUser.role === 'viewer' || currentUser.role === 'advisor') {
          window.location.replace(`${LEGACY_APP_URL}/my-profile`)
          return
        }
        setUser(currentUser)
      })
      .catch((error: unknown) => {
        if (!active) return
        if (error instanceof ApiError && error.status === 401) {
          window.location.replace('/login')
          return
        }
        setLoading(false)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [isLoginPage])

  if (isLoginPage) return <LoginPage />
  if (loading || !user) {
    return (
      <main className="react-loading" aria-live="polite">
        <span className="loading-mark" aria-hidden="true">⚡</span>
        <p>{loading ? 'Loading your quality workspace…' : 'The workspace could not be loaded.'}</p>
        {!loading && (
          <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>
            Try again
          </button>
        )}
      </main>
    )
  }

  return (
    <AppShell user={user}>
      {isAdminPage
        ? <AdminPage path={window.location.pathname} user={user} />
        : <DashboardPage user={user} />}
    </AppShell>
  )
}
