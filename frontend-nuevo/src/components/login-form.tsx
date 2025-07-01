"use client"

import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/hooks/useAuth"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [response, setResponse] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()
  const { isAuthenticated, isLoading: authLoading, updateToken } = useAuth()

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      navigate("/forums")
    }
  }, [isAuthenticated, authLoading, navigate])

  useEffect(() => {
    if (authLoading) return // Don't create socket while auth is loading

    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket

    socket.onopen = () => {
      console.log("🔌 WebSocket conectado con gateway")
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      setResponse(event.data)
      setIsLoading(false)

      const prefixIndex = event.data.indexOf("AUTH_OK")
      if (prefixIndex !== -1) {
        try {
          const jsonStr = event.data.slice(prefixIndex + "AUTH_OK".length)
          const json = JSON.parse(jsonStr)
          if (json.token) {
            toast.success(`¡Bienvenido! ${json.user?.email || email}`)
            updateToken(json.token)
            navigate("/forums")
          }
        } catch (err) {
          console.error("❌ Error procesando AUTH_OK:", err)
          toast.error("Error procesando respuesta del servidor")
        }
      } else if (event.data.includes("AUTH_NK")) {
        try {
          const nkIdx = event.data.indexOf("AUTH_NK")
          const jsonStr = event.data.slice(nkIdx + "AUTH_NK".length)
          const json = JSON.parse(jsonStr)
          toast.error(json.message || "Credenciales inválidas")
        } catch {
          toast.error("Credenciales inválidas")
        }
        setIsLoading(false)
      }
    }

    socket.onerror = (err) => {
      console.error("❌ WebSocket error:", err)
      
      setIsLoading(false)
    }
    socket.onclose = () => {
      console.log("🔒 WebSocket cerrado")
    }

    return () => socket.close()
  }, [navigate, updateToken, authLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password) {
      toast.error("Por favor completa todos los campos")
      return
    }
    
    setIsLoading(true)
    toast.info("Iniciando sesión...")
    const fullMessage = `AUTH_login ${email} ${password}`

    const socket = socketRef.current
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(fullMessage)
    } else {
      toast.error("Conexión no disponible. Intentando reconectar...")
      console.warn("⏳ WebSocket aún no está listo. Esperando reconexión...")
      const waitInterval = setInterval(() => {
        if (socket?.readyState === WebSocket.OPEN) {
          clearInterval(waitInterval)
          socket.send(fullMessage)
        }
      }, 100)
      
      // Timeout after 5 seconds
      setTimeout(() => {
        clearInterval(waitInterval)
        if (isLoading) {
          setIsLoading(false)
          
        }
      }, 5000)
    }
  }

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        "flex min-h-screen items-center justify-center p-6 bg-background",
        className
      )}
      {...props}
    >
      <Card className="w-full max-w-md shadow-lg border border-border">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Iniciar Sesión</CardTitle>
          <CardDescription>
            Accede con tu correo institucional
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="email">Correo</Label>
              <Input
                id="email"
                type="email"
                placeholder="usuario@udp.cl"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Iniciando sesión..." : "Ingresar"}
            </Button>
            {response && (
              <div className="text-sm text-muted-foreground text-center">
                {(() => {
                  const idx = response.indexOf("AUTH_OK")
                  if (idx !== -1) {
                    try {
                      const data = JSON.parse(
                        response.slice(idx + "AUTH_OK".length)
                      )
                      return data.message || "Sesión iniciada"
                    } catch {
                      return response
                    }
                  }
                  const nkIdx = response.indexOf("AUTH_NK")
                  if (nkIdx !== -1) {
                    try {
                      const data = JSON.parse(
                        response.slice(nkIdx + "AUTH_NK".length)
                      )
                      return data.message || "Error de autenticación"
                    } catch {
                      return "Error de autenticación"
                    }
                  }
                  return response
                })()}
              </div>
            )}
            <div className="text-center text-sm mt-2">
              ¿No tienes cuenta?{" "}
              <button
                type="button"
                onClick={() => navigate("/register")}
                className="text-primary hover:underline underline-offset-4"
                disabled={isLoading}
              >
                Regístrate aquí
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}