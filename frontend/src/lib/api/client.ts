const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

interface ApiErrorBody {
  error?: {
    code?: string
    message?: string
    details?: unknown
  }
}

interface CsrfResponse {
  csrf_token: string
}

export class ApiError extends Error {
  readonly status: number
  readonly code?: string
  readonly details?: unknown

  constructor(
    message: string,
    status: number,
    code?: string,
    details?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

let csrfToken: string | null = null

function apiUrl(path: string) {
  return `${API_BASE.replace(/\/$/, '')}/${path.replace(/^\//, '')}`
}

async function getCsrfToken() {
  if (csrfToken) return csrfToken

  const response = await fetch(apiUrl('/auth/csrf'), {
    credentials: 'same-origin',
  })
  if (!response.ok) {
    throw new ApiError('Could not establish a secure session.', response.status)
  }

  const body = (await response.json()) as CsrfResponse
  if (!body.csrf_token) {
    throw new ApiError('The server did not return a CSRF token.', response.status)
  }
  csrfToken = body.csrf_token
  return csrfToken
}

async function toApiError(response: Response) {
  const contentType = response.headers.get('content-type') ?? ''
  if (contentType.includes('application/json')) {
    const body = (await response.json()) as ApiErrorBody
    return new ApiError(
      body.error?.message ?? `Request failed with status ${response.status}.`,
      response.status,
      body.error?.code,
      body.error?.details,
    )
  }

  const message = await response.text()
  return new ApiError(
    message || `Request failed with status ${response.status}.`,
    response.status,
  )
}

export async function requestJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase()
  const headers = new Headers(init.headers)
  const isMutating = !['GET', 'HEAD', 'OPTIONS'].includes(method)

  if (isMutating) {
    headers.set('X-CSRF-Token', await getCsrfToken())
  }

  if (
    init.body &&
    typeof init.body === 'string' &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(apiUrl(path), {
    ...init,
    method,
    headers,
    credentials: 'same-origin',
  })

  if (!response.ok) {
    throw await toApiError(response)
  }

  if (path.includes('/auth/login') || path.includes('/auth/logout')) {
    csrfToken = null
  }

  return (await response.json()) as T
}
