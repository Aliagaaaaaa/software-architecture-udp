import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from "react"
import { 
  isTokenExpired, 
  parseUserFromToken, 
  storeAuthState, 
  getStoredAuthState, 
  clearAuthState,
  getTokenExpiration
} from "@/lib/utils"

export interface User {
  email: string
  rol: string
  id_usuario: number
  name: string
  avatar: string
  isProfileComplete: boolean
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  isTokenValid: boolean
  logout: () => void
  updateToken: (token: string) => void
  verifyToken: (token: string) => Promise<boolean>
  refreshToken: (token: string) => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isTokenValid, setIsTokenValid] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const initializeRef = useRef(false)
  const verificationInProgress = useRef(false)
  const lastVerificationTime = useRef<number>(0)

  const connectWebSocket = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return socketRef.current
    }

    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket
    return socket
  }, [])

  const verifyToken = useCallback(async (token: string, retries = 2): Promise<boolean> => {
    // Evitar verificaciones múltiples simultáneas
    if (verificationInProgress.current) {
      return isTokenValid
    }

    // Verificar si ya verificamos recientemente (últimos 5 minutos)
    const now = Date.now()
    if (now - lastVerificationTime.current < 5 * 60 * 1000) {
      return isTokenValid
    }

    verificationInProgress.current = true
    lastVerificationTime.current = now

    return new Promise((resolve) => {
      const socket = connectWebSocket()
      
      const handleMessage = (event: MessageEvent) => {
        console.log("📨 Token verification response:", event.data)
        
        if (event.data.includes("AUTH_OK")) {
          try {
            const authOkIndex = event.data.indexOf("AUTH_OK")
            const jsonString = event.data.slice(authOkIndex + "AUTH_OK".length)
            const json = JSON.parse(jsonString)
            
            if (json.success && json.payload) {
              setIsTokenValid(true)
              verificationInProgress.current = false
              resolve(true)
            } else {
              setIsTokenValid(false)
              verificationInProgress.current = false
              resolve(false)
            }
          } catch (err) {
            console.error("Error parsing token verification:", err)
            setIsTokenValid(false)
            verificationInProgress.current = false
            resolve(false)
          }
        } else if (event.data.includes("AUTH_NK")) {
          setIsTokenValid(false)
          verificationInProgress.current = false
          resolve(false)
        }
        
        socket.removeEventListener('message', handleMessage)
      }

      const handleError = () => {
        console.warn("WebSocket error during token verification")
        verificationInProgress.current = false
        if (retries > 0) {
          console.log(`Retrying token verification... (${retries} attempts left)`)
          setTimeout(() => {
            verifyToken(token, retries - 1).then(resolve)
          }, 1000)
        } else {
          // En caso de error de conexión, asumir que el token es válido si no está expirado
          const isExpired = isTokenExpired(token)
          setIsTokenValid(!isExpired)
          resolve(!isExpired)
        }
      }

      socket.addEventListener('message', handleMessage)
      socket.addEventListener('error', handleError)
      
      const sendVerification = () => {
        if (socket.readyState === WebSocket.OPEN) {
          const message = `AUTH_verify ${token}`
          console.log("📤 Verifying token:", message)
          socket.send(message)
        } else {
          socket.addEventListener('open', () => {
            const message = `AUTH_verify ${token}`
            console.log("📤 Verifying token:", message)
            socket.send(message)
          })
        }
      }

      sendVerification()

      // Timeout más largo para verificación
      setTimeout(() => {
        socket.removeEventListener('message', handleMessage)
        socket.removeEventListener('error', handleError)
        verificationInProgress.current = false
        
        // Si no hay respuesta, asumir válido si no está expirado
        const isExpired = isTokenExpired(token)
        setIsTokenValid(!isExpired)
        resolve(!isExpired)
      }, 10000) // 10 segundos en lugar de 5
    })
  }, [connectWebSocket, isTokenValid])

  const refreshToken = useCallback(async (token: string, retries = 2): Promise<string | null> => {
    return new Promise((resolve) => {
      const socket = connectWebSocket()
      
      const handleMessage = (event: MessageEvent) => {
        console.log("📨 Token refresh response:", event.data)
        
        if (event.data.includes("AUTH_OK")) {
          try {
            const authOkIndex = event.data.indexOf("AUTH_OK")
            const jsonString = event.data.slice(authOkIndex + "AUTH_OK".length)
            const json = JSON.parse(jsonString)
            
            if (json.success && json.token) {
              resolve(json.token)
            } else {
              resolve(null)
            }
          } catch (err) {
            console.error("Error parsing token refresh:", err)
            resolve(null)
          }
        } else if (event.data.includes("AUTH_NK")) {
          resolve(null)
        }
        
        socket.removeEventListener('message', handleMessage)
      }

      const handleError = () => {
        console.warn("WebSocket error during token refresh")
        if (retries > 0) {
          console.log(`Retrying token refresh... (${retries} attempts left)`)
          setTimeout(() => {
            refreshToken(token, retries - 1).then(resolve)
          }, 1000)
        } else {
          resolve(null)
        }
      }

      socket.addEventListener('message', handleMessage)
      socket.addEventListener('error', handleError)
      
      const sendRefresh = () => {
        if (socket.readyState === WebSocket.OPEN) {
          const message = `AUTH_refresh ${token}`
          console.log("📤 Refreshing token:", message)
          socket.send(message)
        } else {
          socket.addEventListener('open', () => {
            const message = `AUTH_refresh ${token}`
            console.log("📤 Refreshing token:", message)
            socket.send(message)
          })
        }
      }

      sendRefresh()

      setTimeout(() => {
        socket.removeEventListener('message', handleMessage)
        socket.removeEventListener('error', handleError)
        resolve(null)
      }, 10000) // 10 segundos en lugar de 5
    })
  }, [connectWebSocket])

  // Usar las utilidades importadas

  const logout = useCallback(() => {
    console.log("🔓 Logging out...")
    localStorage.removeItem("token")
    clearAuthState()
    setUser(null)
    setIsTokenValid(false)
    verificationInProgress.current = false
    lastVerificationTime.current = 0
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [])

  const updateToken = useCallback((newToken: string) => {
    console.log("🔄 Updating token...")
    localStorage.setItem("token", newToken)
    const userData = parseUserFromToken(newToken)
    if (userData) {
      setUser(userData)
      setIsTokenValid(true)
      storeAuthState(userData)
      lastVerificationTime.current = Date.now()
      console.log(`✅ Token updated, expires: ${getTokenExpiration(newToken)}`)
    }
  }, [])

  useEffect(() => {
    if (initializeRef.current) return
    initializeRef.current = true

    const initializeAuth = async () => {
      console.log("🔐 Initializing auth...")
      setIsLoading(true)
      const token = localStorage.getItem("token")
      
      if (!token) {
        // Intentar recuperar estado de sesión
        const storedState = getStoredAuthState()
        if (storedState) {
          console.log("📦 Recovered user state from session storage")
          setUser(storedState)
          setIsTokenValid(true)
        } else {
          console.log("❌ No token found")
        }
        setIsLoading(false)
        return
      }

      // Primero parsear el usuario del token sin verificar
      const userData = parseUserFromToken(token)
      if (userData) {
        setUser(userData)
        setIsTokenValid(true)
        storeAuthState(userData)
        console.log(`📅 Token expires: ${getTokenExpiration(token)}`)
      }

      // Verificar si el token está muy cerca de expirar
      if (isTokenExpired(token)) {
        console.log("🔄 Token expired or expiring soon, attempting refresh...")
        const newToken = await refreshToken(token)
        
        if (newToken) {
          localStorage.setItem("token", newToken)
          const newUserData = parseUserFromToken(newToken)
          if (newUserData) {
            setUser(newUserData)
            setIsTokenValid(true)
            storeAuthState(newUserData)
            console.log(`✅ Token refreshed successfully, new expiration: ${getTokenExpiration(newToken)}`)
          }
        } else {
          console.log("❌ Token refresh failed, but keeping user logged in temporarily")
          // No deslogear inmediatamente, dar oportunidad de que funcione
        }
      } else {
        // Token no expirado, verificar en segundo plano sin bloquear
        console.log("✅ Token appears valid, verifying in background...")
        verifyToken(token).catch(() => {
          console.warn("Background token verification failed, but keeping user logged in")
        })
      }
      
      setIsLoading(false)
    }

    initializeAuth()

    // Configurar verificación periódica cada 30 minutos
    const interval = setInterval(() => {
      const token = localStorage.getItem("token")
      if (token && !isTokenExpired(token)) {
        verifyToken(token).catch(() => {
          console.warn("Periodic token verification failed")
        })
      }
    }, 30 * 60 * 1000) // 30 minutos

    return () => {
      clearInterval(interval)
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [verifyToken, refreshToken])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user && isTokenValid,
    isLoading,
    isTokenValid,
    logout,
    updateToken,
    verifyToken,
    refreshToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
} 