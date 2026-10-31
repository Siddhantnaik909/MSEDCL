import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { ApiError, requestJson } from '../../lib/api/client'
import type { SessionUser, UserRole } from '../auth/types'

const LEGACY_APP_URL =
  import.meta.env.VITE_LEGACY_APP_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin)

interface AdminUser {
  id: number
  username: string
  full_name: string | null
  email: string | null
  role: UserRole
  advisor_id: string | null
  active: number
  created_at: string | null
  last_login: string | null
}

interface AuditLog {
  id: number
  timestamp: string
  actor_username: string
  actor_role: string
  action: string
  target_entity: string | null
  details: string | null
  ip_address: string | null
}

interface SystemSettings {
  company_name?: string
  admin_email?: string
  default_date_range?: string
  enable_excel_import?: string
  email_provider?: string
  smtp_host?: string
  smtp_port?: string
  smtp_username?: string
  smtp_password?: string
  smtp_from?: string
  ms_client_id?: string
  ms_tenant_id?: string
  ms_client_secret?: string
  smtp_password_configured?: boolean
  ms_client_secret_configured?: boolean
}

interface AdminPageProps {
  path: string
  user: SessionUser
}

const userRoles: UserRole[] = ['quality', 'manager', 'viewer', 'advisor']

const pageDetails: Record<string, { title: string; description: string }> = {
  '/admin/users': {
    title: 'User management',
    description: 'Manage portal access, roles, and employee accounts.',
  },
  '/admin/settings': {
    title: 'System settings',
    description: 'Control audit imports, portal details, and email delivery.',
  },
  '/admin/audit-logs': {
    title: 'Audit activity',
    description: 'Review recent account and system actions.',
  },
}

function ErrorMessage({ children }: { children: string }) {
  return <div className="alert alert-danger" role="alert">{children}</div>
}

function Notice({ children }: { children: string }) {
  return <div className="admin-notice" role="status">{children}</div>
}

function useAdminAction() {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function run<T>(action: () => Promise<T>) {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      return await action()
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'The request could not be completed.')
      return undefined
    } finally {
      setBusy(false)
    }
  }

  return { busy, error, message, setError, setMessage, run }
}

function AdminPageHeading({ path, user }: { path: string; user: SessionUser }) {
  const page = pageDetails[path] ?? pageDetails['/admin/settings']
  return (
    <header className="admin-page-heading">
      <div>
        <p className="admin-breadcrumb">Administration / {page.title}</p>
        <h2>{page.title}</h2>
        <p>{page.description}</p>
      </div>
      <span className="admin-role-chip">{user.role} workspace</span>
    </header>
  )
}

function UserManagement({ user }: { user: SessionUser }) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [query, setQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [resetTarget, setResetTarget] = useState<AdminUser | null>(null)
  const { busy, error, message, setError, setMessage, run } = useAdminAction()
  const [newUser, setNewUser] = useState({
    username: '',
    full_name: '',
    email: '',
    role: 'quality' as UserRole,
    advisor_id: '',
    password: '',
  })

  async function refreshUsers() {
    try {
      const result = await requestJson<{ users: AdminUser[] }>('/admin/users')
      setUsers(result.users)
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Could not load user accounts.')
    }
  }

  useEffect(() => {
    let active = true
    requestJson<{ users: AdminUser[] }>('/admin/users')
      .then((result) => {
        if (active) setUsers(result.users)
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : 'Could not load user accounts.')
      })
    return () => {
      active = false
    }
  }, [setError])

  const visibleUsers = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    return users.filter((account) => {
      const matchesQuery = !normalizedQuery || [
        account.username,
        account.full_name ?? '',
        account.email ?? '',
      ].some((value) => value.toLowerCase().includes(normalizedQuery))
      const matchesRole = roleFilter === 'all' || account.role === roleFilter
      const matchesStatus = statusFilter === 'all'
        || (statusFilter === 'active' ? Boolean(account.active) : !account.active)
      return matchesQuery && matchesRole && matchesStatus
    })
  }, [users, query, roleFilter, statusFilter])

  async function createUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const result = await run(() => requestJson<{ message: string }>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(newUser),
    }))
    if (result) {
      setNewUser({
        username: '',
        full_name: '',
        email: '',
        role: 'quality',
        advisor_id: '',
        password: '',
      })
      await refreshUsers()
      setMessage(result.message)
    }
  }

  async function toggleUser(account: AdminUser) {
    const result = await run(() => requestJson<{ message: string }>(
      `/admin/users/${account.id}/status`,
      { method: 'PATCH' },
    ))
    if (result) {
      await refreshUsers()
      setMessage(result.message)
    }
  }

  async function deleteUser(account: AdminUser) {
    if (!window.confirm(`Delete the account for ${account.username}? This cannot be undone.`)) return
    const result = await run(() => requestJson<{ message: string }>(
      `/admin/users/${account.id}`,
      { method: 'DELETE' },
    ))
    if (result) {
      setMessage(result.message)
      setUsers((current) => current.filter((entry) => entry.id !== account.id))
    }
  }

  async function resetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!resetTarget) return
    const data = new FormData(event.currentTarget)
    const password = String(data.get('new_password') ?? '')
    const result = await run(() => requestJson<{ message: string }>(
      `/admin/users/${resetTarget.id}/password`,
      { method: 'POST', body: JSON.stringify({ password }) },
    ))
    if (result) {
      setMessage(result.message)
      setResetTarget(null)
    }
  }

  return (
    <>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {message && <Notice>{message}</Notice>}
      <section className="admin-card">
        <div className="admin-card-heading">
          <div>
            <h3>Create an account</h3>
            <p>Access is assigned by role. Passwords must be at least 8 characters.</p>
          </div>
        </div>
        <form className="admin-form-grid" onSubmit={createUser}>
          <label>
            Username
            <input className="form-control" value={newUser.username} onChange={(event) => setNewUser({ ...newUser, username: event.target.value })} required autoComplete="off" />
          </label>
          <label>
            Full name
            <input className="form-control" value={newUser.full_name} onChange={(event) => setNewUser({ ...newUser, full_name: event.target.value })} />
          </label>
          <label>
            Email
            <input className="form-control" type="email" value={newUser.email} onChange={(event) => setNewUser({ ...newUser, email: event.target.value })} />
          </label>
          <label>
            Role
            <select className="form-control" value={newUser.role} onChange={(event) => setNewUser({ ...newUser, role: event.target.value as UserRole })}>
              {userRoles.map((role) => <option key={role} value={role}>{role}</option>)}
              {user.role === 'admin' && <option value="admin">admin</option>}
            </select>
          </label>
          <label>
            Advisor ID
            <input className="form-control" value={newUser.advisor_id} onChange={(event) => setNewUser({ ...newUser, advisor_id: event.target.value })} />
          </label>
          <label>
            Temporary password
            <input className="form-control" type="password" value={newUser.password} onChange={(event) => setNewUser({ ...newUser, password: event.target.value })} minLength={8} required autoComplete="new-password" />
          </label>
          <div className="admin-form-actions">
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? 'Saving…' : 'Create account'}
            </button>
          </div>
        </form>
      </section>

      <section className="admin-card">
        <div className="admin-card-heading admin-user-toolbar">
          <div>
            <h3>Registered accounts <span className="admin-count">{visibleUsers.length}</span></h3>
            <p>Search and filter staff access. Password hashes are never shown.</p>
          </div>
          <div className="admin-filters">
            <input className="form-control" aria-label="Search users" placeholder="Search name or email" value={query} onChange={(event) => setQuery(event.target.value)} />
            <select className="form-control" aria-label="Filter by role" value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
              <option value="all">All roles</option>
              {['admin', ...userRoles].map((role) => <option key={role} value={role}>{role}</option>)}
            </select>
            <select className="form-control" aria-label="Filter by status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="all">All statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Account</th><th>Role</th><th>Advisor ID</th><th>Status</th><th>Last sign-in</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {visibleUsers.map((account) => (
                <tr key={account.id}>
                  <td><strong>{account.full_name || account.username}</strong><small>{account.username}{account.email ? ` · ${account.email}` : ''}</small></td>
                  <td><span className="admin-role-chip">{account.role}</span></td>
                  <td>{account.advisor_id || '—'}</td>
                  <td><span className={`admin-status ${account.active ? 'is-active' : 'is-inactive'}`}>{account.active ? 'Active' : 'Inactive'}</span></td>
                  <td>{account.last_login || 'Never'}</td>
                  <td>
                    <div className="admin-row-actions">
                      <button type="button" className="admin-text-button" disabled={busy || account.id === user.id} onClick={() => void toggleUser(account)}>{account.active ? 'Deactivate' : 'Activate'}</button>
                      {user.role === 'admin' && (
                        <>
                          <button type="button" className="admin-text-button" onClick={() => setResetTarget(account)}>Reset password</button>
                          <button type="button" className="admin-text-button is-danger" disabled={busy || account.id === user.id} onClick={() => void deleteUser(account)}>Delete</button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {visibleUsers.length === 0 && <tr><td colSpan={6} className="admin-empty">No accounts match these filters.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {resetTarget && (
        <div className="admin-dialog-backdrop" role="presentation">
          <section className="admin-dialog" role="dialog" aria-modal="true" aria-labelledby="reset-title">
            <h3 id="reset-title">Reset password</h3>
            <p>Set a new temporary password for <strong>{resetTarget.username}</strong>.</p>
            <form onSubmit={resetPassword}>
              <label>
                New password
                <input className="form-control" name="new_password" type="password" minLength={8} required autoComplete="new-password" autoFocus />
              </label>
              <div className="admin-form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setResetTarget(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? 'Updating…' : 'Update password'}</button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  )
}

function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [savedSettings, setSavedSettings] = useState<SystemSettings | null>(null)
  const [testRecipient, setTestRecipient] = useState('')
  const { busy, error, message, setError, setMessage, run } = useAdminAction()
  const hasChanges = useMemo(
    () => Boolean(settings && savedSettings && JSON.stringify(settings) !== JSON.stringify(savedSettings)),
    [settings, savedSettings],
  )

  useEffect(() => {
    let active = true
    requestJson<{
        settings: SystemSettings
        smtp_password_configured: boolean
        ms_client_secret_configured: boolean
      }>('/admin/settings')
      .then((response) => {
        if (active) {
          const loadedSettings = {
            ...response.settings,
            smtp_password_configured: response.smtp_password_configured,
            ms_client_secret_configured: response.ms_client_secret_configured,
          }
          setSettings(loadedSettings)
          setSavedSettings(loadedSettings)
        }
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : 'Could not load system settings.')
      })
    return () => {
      active = false
    }
  }, [setError])

  function update(key: keyof SystemSettings, value: string) {
    setSettings((current) => current ? { ...current, [key]: value } : current)
  }

  async function saveSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!settings) return
    const payload = Object.fromEntries(
      Object.entries(settings).filter(([key]) => !key.endsWith('_configured')),
    )
    const result = await run(() => requestJson<{ message: string }>('/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }))
    if (result) {
      const saved = settings ? {
        ...settings,
        smtp_password_configured: Boolean(settings.smtp_password || settings.smtp_password_configured),
        ms_client_secret_configured: Boolean(settings.ms_client_secret || settings.ms_client_secret_configured),
        smtp_password: '',
        ms_client_secret: '',
      } : null
      setSettings(saved)
      setSavedSettings(saved)
      setMessage(result.message)
    }
  }

  async function testEmail(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const result = await run(() => requestJson<{ message: string }>('/admin/settings/test-email', {
      method: 'POST',
      body: JSON.stringify({ recipient: testRecipient }),
    }))
    if (result) setMessage(result.message)
  }

  async function downloadBackup() {
    const base = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'
    const response = await fetch(`${base.replace(/\/$/, '')}/admin/backup`, {
      credentials: 'same-origin',
    })
    if (!response.ok) {
      const body = await response.json().catch(() => null) as { error?: { message?: string } } | null
      throw new ApiError(body?.error?.message ?? 'Could not download the database backup.', response.status)
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'quality_audit_backup.db'
    anchor.click()
    URL.revokeObjectURL(url)
    setMessage('Database backup downloaded.')
  }

  async function purgeAudits() {
    const confirmation = window.prompt('This permanently deletes audit and import-batch records. Type PURGE to continue.')
    if (confirmation !== 'PURGE') return
    const result = await run(() => requestJson<{ message: string }>('/admin/audits/purge', {
      method: 'POST',
      body: JSON.stringify({ confirmation }),
    }))
    if (result) setMessage(result.message)
  }

  if (!settings) {
    return (
      <>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {!error && (
          <div className="admin-card settings-loading">
            <span className="settings-loading-mark" aria-hidden="true">⚡</span>
            Loading system settings…
          </div>
        )}
      </>
    )
  }

  return (
    <>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {message && <Notice>{message}</Notice>}
      <section className="settings-overview" aria-label="Settings status">
        <div className="settings-overview-mark" aria-hidden="true">⚡</div>
        <div className="settings-overview-copy">
          <strong>Control room settings</strong>
          <span>Portal access, email delivery, and data safeguards</span>
        </div>
        <div className={`settings-save-status${hasChanges ? ' is-dirty' : ''}`} role="status">
          <span aria-hidden="true">{hasChanges ? '●' : '✓'}</span>
          {hasChanges ? 'Unsaved changes' : 'All changes saved'}
        </div>
      </section>

      <nav className="settings-jump-nav" aria-label="Settings sections">
        <a href="#portal-settings">Portal</a>
        <a href="#email-settings">Email delivery</a>
        <a href="#maintenance-settings">Data &amp; maintenance</a>
      </nav>

      <form className="settings-form" onSubmit={saveSettings}>
        <section className="admin-card settings-section" id="portal-settings">
          <div className="settings-section-heading">
            <span className="settings-section-icon" aria-hidden="true">⌂</span>
            <div><h3>Portal profile</h3><p>Set the organization details and defaults staff see when they sign in.</p></div>
          </div>
          <div className="admin-form-grid">
            <label>Organization name<input className="form-control" value={settings.company_name ?? ''} onChange={(event) => update('company_name', event.target.value)} required /></label>
            <label>Administrator email<input className="form-control" type="email" value={settings.admin_email ?? ''} onChange={(event) => update('admin_email', event.target.value)} required /></label>
            <label>Default dashboard range<input className="form-control" type="number" min="1" max="3650" value={settings.default_date_range ?? '30'} onChange={(event) => update('default_date_range', event.target.value)} required /><small>Days of audit activity shown by default.</small></label>
            <label className="settings-import-toggle">Workbook imports
              <select className="form-control" value={settings.enable_excel_import ?? 'true'} onChange={(event) => update('enable_excel_import', event.target.value)}><option value="true">Enabled</option><option value="false">Disabled</option></select>
              <small>When disabled, new spreadsheet uploads are blocked.</small>
            </label>
          </div>
        </section>

        <section className="admin-card settings-section" id="email-settings">
          <div className="settings-section-heading">
            <span className="settings-section-icon" aria-hidden="true">✉</span>
            <div><h3>Email delivery</h3><p>Configure how the portal sends messages to employees and advisors.</p></div>
            <span className="settings-provider-chip">{settings.email_provider === 'ms_graph' ? 'Microsoft Graph' : 'Organization SMTP'}</span>
          </div>
          <div className="settings-provider-select">
            <label htmlFor="settings-provider">Email provider</label>
            <select id="settings-provider" className="form-control" value={settings.email_provider ?? 'smtp'} onChange={(event) => update('email_provider', event.target.value)}>
              <option value="smtp">Organization SMTP</option>
              <option value="ms_graph">Microsoft Graph</option>
            </select>
            <p>The provider choice is saved with the portal configuration.</p>
          </div>
          <div className="admin-form-grid settings-email-grid">
            <label>Sender email<input className="form-control" type="email" value={settings.smtp_from ?? ''} onChange={(event) => update('smtp_from', event.target.value)} /></label>
            {settings.email_provider === 'ms_graph' ? (
              <>
                <label>Microsoft client ID<input className="form-control" value={settings.ms_client_id ?? ''} onChange={(event) => update('ms_client_id', event.target.value)} autoComplete="off" /></label>
                <label>Microsoft tenant ID<input className="form-control" value={settings.ms_tenant_id ?? ''} onChange={(event) => update('ms_tenant_id', event.target.value)} autoComplete="off" /></label>
                <label>Microsoft client secret<input className="form-control" type="password" placeholder={settings.ms_client_secret_configured ? 'Saved securely — leave blank to keep' : 'Not configured'} value={settings.ms_client_secret ?? ''} onChange={(event) => update('ms_client_secret', event.target.value)} autoComplete="new-password" /><small>Secrets are never displayed after saving.</small></label>
              </>
            ) : (
              <>
                <label>SMTP host<input className="form-control" value={settings.smtp_host ?? ''} onChange={(event) => update('smtp_host', event.target.value)} placeholder="mail.example.org" /></label>
                <label>SMTP port<input className="form-control" type="number" min="1" max="65535" value={settings.smtp_port ?? '587'} onChange={(event) => update('smtp_port', event.target.value)} /></label>
                <label>SMTP username<input className="form-control" value={settings.smtp_username ?? ''} onChange={(event) => update('smtp_username', event.target.value)} autoComplete="off" /></label>
                <label>SMTP password<input className="form-control" type="password" placeholder={settings.smtp_password_configured ? 'Saved securely — leave blank to keep' : 'Not configured'} value={settings.smtp_password ?? ''} onChange={(event) => update('smtp_password', event.target.value)} autoComplete="new-password" /><small>Secrets are never displayed after saving.</small></label>
              </>
            )}
          </div>
          <div className="settings-inline-diagnostic">
            <div><strong>Check delivery</strong><span>Send a test using the configured SMTP connection.</span></div>
            <div className="admin-inline-form">
              <input
                form="settings-email-test"
                className="form-control"
                type="email"
                aria-label="Test recipient email"
                placeholder="Recipient email"
                value={testRecipient}
                onChange={(event) => setTestRecipient(event.target.value)}
                required
              />
              <button form="settings-email-test" type="submit" className="btn btn-secondary" disabled={busy}>{busy ? 'Sending…' : 'Send test'}</button>
            </div>
          </div>
        </section>

        <section className="admin-card settings-section" id="maintenance-settings">
          <div className="settings-section-heading">
            <span className="settings-section-icon" aria-hidden="true">▤</span>
            <div><h3>Data &amp; maintenance</h3><p>Protect a copy of your database or manage historical audit records.</p></div>
          </div>
          <div className="settings-maintenance-grid">
            <article className="settings-maintenance-item">
              <span className="settings-maintenance-symbol" aria-hidden="true">↓</span>
              <div><h4>Database backup</h4><p>Download a copy of the active SQLite database.</p></div>
              <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => void run(downloadBackup)}>Download backup</button>
            </article>
            <article className="settings-maintenance-item settings-maintenance-danger">
              <span className="settings-maintenance-symbol" aria-hidden="true">!</span>
              <div><h4>Remove audit data</h4><p>Deletes audit records and import history. Accounts and settings remain.</p></div>
              <button type="button" className="btn btn-danger" disabled={busy} onClick={() => void purgeAudits()}>Purge audit data</button>
            </article>
          </div>
        </section>

        <div className="settings-savebar">
          <div className="settings-savebar-copy">
            <span className={`settings-save-dot${hasChanges ? ' is-dirty' : ''}`} aria-hidden="true" />
            <span>{hasChanges ? 'You have unsaved changes' : 'Settings are up to date'}</span>
          </div>
          <button type="submit" className="btn btn-primary" disabled={busy || !hasChanges}>
            {busy ? 'Saving settings…' : hasChanges ? 'Save changes' : 'Saved'}
          </button>
        </div>
      </form>

      <form id="settings-email-test" onSubmit={testEmail} hidden />

      <section className="admin-card">
        <div className="admin-card-heading">
          <div><h3>Restart service</h3><p>Restart remains in the existing Flask settings page and requires your administrator password.</p></div>
        </div>
        <a className="btn btn-secondary" href={`${LEGACY_APP_URL}/admin/settings`}>Open restart controls</a>
      </section>
    </>
  )
}

function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    requestJson<{ logs: AuditLog[] }>('/admin/audit-logs')
      .then((response) => setLogs(response.logs))
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load audit activity.'))
  }, [])

  return (
    <>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      <section className="admin-card">
        <div className="admin-card-heading">
          <div><h3>Recent activity <span className="admin-count">{logs.length}</span></h3><p>The latest 500 events are shown, newest first.</p></div>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Time</th><th>Account</th><th>Action</th><th>Target</th><th>Details</th><th>IP address</th></tr></thead>
            <tbody>
              {logs.map((entry) => <tr key={entry.id}><td>{entry.timestamp}</td><td><strong>{entry.actor_username}</strong><small>{entry.actor_role}</small></td><td><span className="admin-action-chip">{entry.action}</span></td><td>{entry.target_entity || '—'}</td><td>{entry.details || '—'}</td><td>{entry.ip_address || '—'}</td></tr>)}
              {!error && logs.length === 0 && <tr><td colSpan={6} className="admin-empty">No activity has been recorded yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}

export function AdminPage({ path, user }: AdminPageProps) {
  return (
    <div className="admin-page">
      <AdminPageHeading path={path} user={user} />
      {path === '/admin/users'
        ? <UserManagement user={user} />
        : path === '/admin/audit-logs'
          ? <AuditLogs />
          : <SettingsPage />}
    </div>
  )
}
