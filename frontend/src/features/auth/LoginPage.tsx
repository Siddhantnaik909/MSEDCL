import { useState, type FormEvent } from 'react'
import { ApiError, requestJson } from '../../lib/api/client'
import type { SessionUser } from './types'

const LEGACY_APP_URL =
  import.meta.env.VITE_LEGACY_APP_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin)

interface LoginResponse {
  user: SessionUser
  next: string
}

export function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [darkMode, setDarkMode] = useState(
    document.documentElement.getAttribute('data-theme') === 'dark',
  )

  function toggleTheme() {
    const next = !darkMode
    setDarkMode(next)
    document.documentElement.setAttribute('data-theme', next ? 'dark' : 'light')
    localStorage.setItem('msedcl_theme', next ? 'dark' : 'light')
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const response = await requestJson<LoginResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
      if (response.next === '/my-profile') {
        window.location.replace(`${LEGACY_APP_URL}${response.next}`)
      } else {
        window.location.replace('/')
      }
    } catch (requestError: unknown) {
      if (requestError instanceof ApiError) {
        setError(requestError.message)
      } else {
        setError('Sign-in could not be completed. Check your connection and try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <div className="login-layout">
        <section className="login-story" aria-label="MSEDCL quality assurance">
          <a className="login-brand" href="/" aria-label="MSEDCL Quality Audit home">
            <span className="login-brand-mark" aria-hidden="true">⚡</span>
            <span>
              <strong>MSEDCL</strong>
              <small>Quality Audit Portal</small>
            </span>
          </a>

          <div className="login-story-copy">
            <p className="login-story-kicker">Maharashtra State Electricity Distribution</p>
            <h1>Better quality.<br />Better service.</h1>
            <p>Review performance, learn from every interaction, and help deliver a better experience for every customer.</p>
          </div>

          <div className="login-grid-art" aria-hidden="true">
            <svg viewBox="0 0 640 260" role="presentation" focusable="false">
              <path className="grid-line" d="M0 224H640M0 184H640M0 144H640M0 104H640M0 64H640" />
              <path className="grid-line" d="M80 0V260M160 0V260M240 0V260M320 0V260M400 0V260M480 0V260M560 0V260" />
              <path className="power-line" d="M0 82C112 82 140 128 260 128S398 48 640 48" />
              <path className="power-line power-line-secondary" d="M0 114C132 114 154 157 270 157S435 78 640 78" />
              <g className="tower-lines">
                <path d="M484 61L454 223M484 61L516 223M440 100H528M448 133H521M455 165H515M455 100L514 133M514 100L455 133M450 133L512 165M512 133L450 165M455 165L516 223M515 165L454 223" />
                <path d="M432 100H536M442 133H526M449 165H519M447 223H523" />
              </g>
              <circle className="tower-beacon" cx="484" cy="58" r="4" />
            </svg>
            <div className="login-art-caption"><span />Reliable service starts with quality</div>
          </div>
          <p className="login-story-footer">Serving Maharashtra with care and accountability.</p>
        </section>

        <section className="login-container" aria-labelledby="loginHeading">
          <div className="login-panel-top">
            <span className="login-panel-label">Employee access</span>
            <button
              type="button"
              className="theme-corner-btn"
              onClick={toggleTheme}
              title="Toggle color theme"
              aria-label={darkMode ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {darkMode ? '☼' : '☾'}
            </button>
          </div>

          <div className="login-form-content">
            <p className="login-welcome">Welcome back</p>
            <h2 className="login-heading" id="loginHeading">Sign in to your account</h2>
            <p className="login-description">Enter your credentials to continue to the quality audit portal.</p>

            {error && <div className="alert alert-danger" role="alert">{error}</div>}

            <form className="login-form" onSubmit={submit}>
              <div className="login-field">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  name="username"
                  className="form-control"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                  autoFocus
                  autoComplete="username"
                />
              </div>
              <div className="login-field">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
              <button type="submit" className="btn btn-primary login-submit" disabled={submitting}>
                <span>{submitting ? 'Signing in…' : 'Sign in'}</span>
                <span aria-hidden="true">›</span>
              </button>
            </form>

            <div className="login-security-note">
              <span className="login-security-mark" aria-hidden="true">✓</span>
              <p>Secure, role-based access. Account activity is monitored.</p>
            </div>
          </div>
          <p className="login-panel-footer">Need access? Contact your system administrator.</p>
        </section>
      </div>
    </main>
  )
}
