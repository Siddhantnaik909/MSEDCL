export type UserRole = 'admin' | 'quality' | 'manager' | 'viewer' | 'advisor'

export interface AuthenticatedUser {
  id: number
  username: string
  fullName: string
  role: UserRole
  advisorId: string | null
}

export interface SessionUser {
  id: number
  username: string
  full_name: string
  role: UserRole
  advisor_id: string | null
}
