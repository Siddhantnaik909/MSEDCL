import { useEffect, useState, type ReactNode } from 'react'
import { ApiError, requestJson } from '../lib/api/client'
import type { SessionUser } from '../features/auth/types'

const LEGACY_APP_URL =
  import.meta.env.VITE_LEGACY_APP_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin)

interface AppShellProps {
  children: ReactNode
  user: SessionUser
}

type SidebarIconName =
  | 'dashboard'
  | 'inbound'
  | 'outbound'
  | 'fatal'
  | 'scores'
  | 'auditors'
  | 'advisor'
  | 'warnings'
  | 'email'
  | 'export'
  | 'import'
  | 'users'
  | 'settings'
  | 'logs'
  | 'sign-out'

interface NavigationItem {
  icon: SidebarIconName
  label: string
  href: string
}

const auditLinks: NavigationItem[] = [
  { icon: 'inbound', label: 'Inbound audits', href: '/audits/Inbound' },
  { icon: 'outbound', label: 'Outbound audits', href: '/audits/Outbound' },
  { icon: 'fatal', label: 'Fatal calls', href: '/fatal-calls' },
]

const insightLinks: NavigationItem[] = [
  { icon: 'scores', label: 'Score reports', href: '/score-reports' },
  { icon: 'auditors', label: 'Auditor reports', href: '/auditors' },
  { icon: 'advisor', label: 'Advisor search', href: '/advisor-search' },
]

const actionLinks: NavigationItem[] = [
  { icon: 'warnings', label: 'Warnings & PIP', href: '/warnings' },
  { icon: 'email', label: 'Email history', href: '/email-history' },
  { icon: 'export', label: 'Export center', href: '/export-center' },
  { icon: 'import', label: 'Import files', href: '/upload' },
]

const adminLinks: NavigationItem[] = [
  { icon: 'users', label: 'User management', href: '/admin/users' },
  { icon: 'settings', label: 'Settings', href: '/admin/settings' },
  { icon: 'logs', label: 'Audit activity', href: '/admin/audit-logs' },
]

function SidebarIcon({ name }: { name: SidebarIconName | 'dashboard' }) {
  const paths: Record<SidebarIconName | 'dashboard', ReactNode> = {
    dashboard: <><rect x="3.5" y="3.5" width="7" height="7" rx="1" /><rect x="13.5" y="3.5" width="7" height="7" rx="1" /><rect x="3.5" y="13.5" width="7" height="7" rx="1" /><rect x="13.5" y="13.5" width="7" height="7" rx="1" /></>,
    inbound: <><path d="M12 3v12" /><path d="m6 9 6 6 6-6" /><path d="M4 17v4h16v-4" /></>,
    outbound: <><path d="M12 15V3" /><path d="m6 9 6-6 6 6" /><path d="M4 17v4h16v-4" /></>,
    fatal: <><path d="m12 3 9 16H3L12 3Z" /><path d="M12 9v4" /><path d="M12 16h.01" /></>,
    scores: <><path d="M4 19V5" /><path d="M4 19h17" /><path d="m7 15 4-4 3 2 6-7" /></>,
    auditors: <><circle cx="9" cy="8" r="3" /><path d="M3.5 19a5.5 5.5 0 0 1 11 0" /><path d="M16 5.5a3 3 0 0 1 0 5.8" /><path d="M17 14a5 5 0 0 1 3.5 4.8" /></>,
    advisor: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 4 4" /><path d="M8.5 10.5h4" /><path d="M10.5 8.5v4" /></>,
    warnings: <><path d="M12 3 20 6v5c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6l8-3Z" /><path d="M12 8v4" /><path d="M12 15h.01" /></>,
    email: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m4 7 8 6 8-6" /></>,
    export: <><path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 17v3h14v-3" /></>,
    import: <><path d="M12 15V3" /><path d="m7 8 5-5 5 5" /><path d="M5 17v3h14v-3" /></>,
    users: <><circle cx="9" cy="8" r="3" /><path d="M3.5 20a5.5 5.5 0 0 1 11 0" /><path d="M16 5.5a3 3 0 0 1 0 5.8" /><path d="M17 14a5 5 0 0 1 3.5 4.8" /></>,
    settings: <><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" /><path d="m19.4 13.5 1.1.8-1.5 2.6-1.3-.5a7.7 7.7 0 0 1-1.5.9l-.2 1.4h-3l-.2-1.4a7.7 7.7 0 0 1-1.5-.9l-1.3.5-1.5-2.6 1.1-.8a7 7 0 0 1 0-1.8l-1.1-.8L8 8.3l1.3.5a7.7 7.7 0 0 1 1.5-.9l.2-1.4h3l.2 1.4a7.7 7.7 0 0 1 1.5.9l1.3-.5 1.5 2.6-1.1.8a7 7 0 0 1 0 1.8Z" /></>,
    logs: <><path d="M7 3h7l4 4v14H7z" /><path d="M14 3v5h5" /><path d="M10 13h5M10 17h5" /></>,
    'sign-out': <><path d="M10 17l5-5-5-5" /><path d="M15 12H3" /><path d="M12 4h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-6" /></>,
  }

  return (
    <svg
      className="sidebar-icon-svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {paths[name]}
    </svg>
  )
}

function NavigationLink({
  icon,
  label,
  href,
}: {
  icon: SidebarIconName
  label: string
  href: string
}) {
  const target = href.startsWith('/admin/') || href === '/'
    ? href
    : `${LEGACY_APP_URL}${href}`
  const pathname = window.location.pathname
  const active = pathname === href || (href !== '/' && pathname.startsWith(`${href}/`))

  return (
    <a
      className={`nav-item${active ? ' active' : ''}`}
      href={target}
      title={label}
      aria-current={active ? 'page' : undefined}
    >
      <span className="icon"><SidebarIcon name={icon} /></span>
      <span className="nav-label">{label}</span>
    </a>
  )
}

function NavigationGroup({
  title,
  items,
}: {
  title: string
  items: NavigationItem[]
}) {
  return (
    <div className="sidebar-nav-group">
      <p className="nav-section-title">{title}</p>
      {items.map((item) => <NavigationLink key={item.href} {...item} />)}
    </div>
  )
}

export function AppShell({ children, user }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pageTitle = window.location.pathname === '/admin/users'
    ? 'User management'
    : window.location.pathname === '/admin/settings'
      ? 'System settings'
      : window.location.pathname === '/admin/audit-logs'
        ? 'Audit activity'
        : 'MSEDCL Quality Audit & Performance Dashboard'
  const [darkMode, setDarkMode] = useState(
    document.documentElement.getAttribute('data-theme') === 'dark',
  )

  function toggleTheme() {
    const next = !darkMode
    setDarkMode(next)
    document.documentElement.setAttribute('data-theme', next ? 'dark' : 'light')
    localStorage.setItem('msedcl_theme', next ? 'dark' : 'light')
  }

  const [signOutError, setSignOutError] = useState('')

  async function signOut() {
    setSignOutError('')
    try {
      await requestJson<{ ok: boolean }>('/auth/logout', { method: 'POST' })
      window.location.replace('/login')
    } catch (error: unknown) {
      if (error instanceof ApiError && error.status === 401) {
        window.location.replace('/login')
      } else {
        setSignOutError(error instanceof Error ? error.message : 'Could not sign out.')
      }
    }
  }

  useEffect(() => {
    document.body.classList.toggle('mobile-sidebar-open', sidebarOpen)
    if (window.innerWidth > 768) {
      document.body.classList.toggle(
        'sidebar-collapsed',
        localStorage.getItem('msedcl_sidebar_collapsed') === 'true',
      )
    }
    return () => {
      document.body.classList.remove('mobile-sidebar-open')
      document.body.classList.remove('sidebar-collapsed')
    }
  }, [sidebarOpen])

  function toggleNavigation() {
    if (window.innerWidth <= 768) {
      setSidebarOpen(true)
      return
    }
    const collapsed = !document.body.classList.contains('sidebar-collapsed')
    document.body.classList.toggle('sidebar-collapsed', collapsed)
    localStorage.setItem('msedcl_sidebar_collapsed', String(collapsed))
  }

  return (
    <>
      <div
        className={`sidebar-overlay${sidebarOpen ? ' active' : ''}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />
      <aside className="app-sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <a href="/" className="brand-wrapper" aria-label="MSEDCL Quality Audit dashboard">
            <span className="sidebar-brand-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" focusable="false">
                <path d="m13.5 2-8 11h5l-.5 9 8.5-12h-5l.5-8Z" fill="currentColor" />
              </svg>
            </span>
            <span className="sidebar-brand-text">
              <strong>MSEDCL</strong>
              <span>Quality operations</span>
            </span>
          </a>
          <button
            type="button"
            className="sidebar-toggle-btn mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          >
            ×
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-nav-group">
            <p className="nav-section-title">Workspace</p>
            <NavigationLink icon="dashboard" label="Dashboard" href="/" />
          </div>
          <NavigationGroup title="Audit work" items={auditLinks} />
          <NavigationGroup title="Insights" items={insightLinks} />
          <NavigationGroup title="Follow-up & data" items={actionLinks} />
          {(user.role === 'admin' || user.role === 'manager') && (
            <NavigationGroup
              title="Administration"
              items={user.role === 'admin' ? adminLinks : adminLinks.slice(0, 1)}
            />
          )}
        </nav>

        <div className="sidebar-footer-brand">
          <div className="sidebar-footer-copy">
            <span className="sidebar-account-avatar" aria-hidden="true">
              {(user.full_name || user.username).slice(0, 1).toUpperCase()}
            </span>
            <span className="sidebar-account-details">
              <strong>{user.full_name || user.username}</strong>
              <small>{user.role} account</small>
            </span>
          </div>
          <button
            type="button"
            className="sign-out-button"
            onClick={signOut}
            title="Sign out"
            aria-label="Sign out"
          >
            <SidebarIcon name="sign-out" />
          </button>
        </div>
      </aside>

      <main className="app-main">
        <header className="app-topbar">
          <div className="topbar-left">
            <button
              type="button"
              className="sidebar-toggle-btn"
              onClick={toggleNavigation}
              aria-label="Toggle navigation"
            >
              ☰
            </button>
            <span className="topbar-header-badge" aria-hidden="true">⚡</span>
            <div className="topbar-title-block">
              <h1>{pageTitle}</h1>
              <p>Better Quality <span>|</span> Better Service <span>|</span> Brighter Maharashtra</p>
            </div>
          </div>
          <div className="topbar-right">
            <a className="user-profile-menu" href={`${LEGACY_APP_URL}/my-profile`}>
              <span className="user-avatar-circle">
                {(user.full_name || user.username).slice(0, 1).toUpperCase()}
              </span>
              <span className="user-profile-details hide-mobile">
                <strong>{user.full_name || user.username}</strong>
                <small>{user.role} QA</small>
              </span>
            </a>
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={darkMode ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              <span aria-hidden="true">{darkMode ? '☼' : '☾'}</span>
              <span className="hide-mobile">Mode</span>
            </button>
          </div>
        </header>
        <section className="content-body">
          {signOutError && <div className="alert alert-danger" role="alert">{signOutError}</div>}
          {children}
        </section>
      </main>
    </>
  )
}
