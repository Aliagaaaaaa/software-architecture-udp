import { useEffect, useState } from "react"

export interface User {
  email: string
  rol: string
  id_usuario: number
  name: string
  avatar: string
  isProfileComplete: boolean
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]))

        const userData: User = {
          email: payload.email,
          rol: payload.rol,
          id_usuario: payload.id_usuario,
          name: payload.name ?? "",
          avatar: payload.avatar ?? "",
          isProfileComplete: !!(payload.name && payload.avatar)
        }

        setUser(userData)
      } catch (err) {
        console.error("❌ Error al decodificar el token:", err)
        setUser(null)
      }
    }
  }, [])

  const logout = () => {
    localStorage.removeItem("token")
    setUser(null)
  }

  return {
    user,
    isAuthenticated: !!user,
    logout,
  }
}