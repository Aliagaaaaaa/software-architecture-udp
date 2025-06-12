"use client"

import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
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

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [response, setResponse] = useState("")
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:3001")
    socketRef.current = socket

    socket.onopen = () => console.log("🔌 WebSocket conectado con gateway")

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      setResponse(event.data)

      const prefixIndex = event.data.indexOf("AUTH_OK")
      if (prefixIndex !== -1) {
        try {
          const jsonStr = event.data.slice(prefixIndex + "AUTH_OK".length)
          const json = JSON.parse(jsonStr)
          if (json.token) {
            localStorage.setItem("token", json.token)
            navigate("/forums")
          }
        } catch (err) {
          console.error("❌ Error procesando AUTH_OK:", err)
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const fullMessage = `AUTH_login ${email} ${password}`

    const socket = socketRef.current
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(fullMessage)
    } else {
      console.warn("⏳ WebSocket aún no está listo. Esperando reconexión...")
      const waitInterval = setInterval(() => {
        if (socket?.readyState === WebSocket.OPEN) {
          clearInterval(waitInterval)
          socket.send(fullMessage)
        }
      }, 100)
    }
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
                required
              />
            </div>
            <Button type="submit" className="w-full">
              Ingresar
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