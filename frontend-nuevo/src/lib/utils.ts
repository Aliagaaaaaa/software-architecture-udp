import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Get the current authentication token from localStorage
 * @returns The token string or null if not found
 */
export function getAuthToken(): string | null {
  return localStorage.getItem("token")
}

/**
 * Check if a token is expired with a buffer
 * @param token - JWT token string
 * @param bufferMinutes - Minutes before actual expiration to consider expired (default: 5)
 * @returns true if token is expired or invalid
 */
export function isTokenExpired(token: string, bufferMinutes: number = 5): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    const bufferSeconds = bufferMinutes * 60
    return payload.exp < (currentTime + bufferSeconds)
  } catch {
    return true
  }
}

/**
 * Get token expiration time in a human-readable format
 * @param token - JWT token string
 * @returns Expiration date string or null if invalid
 */
export function getTokenExpiration(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    return new Date(payload.exp * 1000).toLocaleString()
  } catch {
    return null
  }
}

/**
 * Check if token will expire soon (within specified minutes)
 * @param token - JWT token string
 * @param minutesThreshold - Minutes threshold (default: 30)
 * @returns true if token expires soon
 */
export function isTokenExpiringSoon(token: string, minutesThreshold: number = 30): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    const thresholdSeconds = minutesThreshold * 60
    return payload.exp < (currentTime + thresholdSeconds)
  } catch {
    return true
  }
}

/**
 * Parse user data from JWT token
 * @param token - JWT token string
 * @returns User data or null if invalid
 */
export function parseUserFromToken(token: string): any | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    return {
      name: payload.name || payload.email,
      email: payload.email,
      avatar: payload.avatar || "",
      rol: payload.rol,
      id_usuario: payload.id_usuario,
      exp: payload.exp,
      iat: payload.iat
    }
  } catch (err) {
    console.error("❌ Error al decodificar el token:", err)
    return null
  }
}

/**
 * Build a service message with token
 * @param service - Service name (e.g., "MSGES", "FORUM")
 * @param command - Command name (e.g., "list_messages", "create_forum")
 * @param params - Additional parameters
 * @returns Formatted message string
 */
export function buildServiceMessage(service: string, command: string, ...params: string[]): string {
  const token = getAuthToken()
  if (!token) {
    throw new Error("No authentication token found")
  }
  
  const allParams = [token, ...params].join(" ")
  return `${service}${command} ${allParams}`.trim()
}

/**
 * Store authentication state in sessionStorage for tab persistence
 * @param user - User data
 */
export function storeAuthState(user: any): void {
  try {
    sessionStorage.setItem("authState", JSON.stringify({
      user,
      timestamp: Date.now()
    }))
  } catch (err) {
    console.warn("Could not store auth state:", err)
  }
}

/**
 * Retrieve authentication state from sessionStorage
 * @param maxAgeMinutes - Maximum age in minutes (default: 30)
 * @returns User data or null if expired/invalid
 */
export function getStoredAuthState(maxAgeMinutes: number = 30): any | null {
  try {
    const stored = sessionStorage.getItem("authState")
    if (!stored) return null
    
    const { user, timestamp } = JSON.parse(stored)
    const now = Date.now()
    const maxAge = maxAgeMinutes * 60 * 1000
    
    if (now - timestamp > maxAge) {
      sessionStorage.removeItem("authState")
      return null
    }
    
    return user
  } catch (err) {
    console.warn("Could not retrieve auth state:", err)
    sessionStorage.removeItem("authState")
    return null
  }
}

/**
 * Clear stored authentication state
 */
export function clearAuthState(): void {
  try {
    sessionStorage.removeItem("authState")
  } catch (err) {
    console.warn("Could not clear auth state:", err)
  }
}
