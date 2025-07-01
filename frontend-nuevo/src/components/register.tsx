"use client"

import { useRef, useState, useEffect } from "react"
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

export function Register({ className, ...props }: React.ComponentProps<"div">) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [response, setResponse] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket

    socket.onopen = () => {
      console.log("🔌 WebSocket conectado con gateway")
    }
    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      setResponse(event.data)
      setIsLoading(false)
      
      if (event.data.includes("AUTH_OK")) {
        try {
          const prefixIndex = event.data.indexOf("AUTH_OK")
          const jsonStr = event.data.slice(prefixIndex + "AUTH_OK".length)
          const json = JSON.parse(jsonStr)
          toast.success(json.message || "Usuario registrado exitosamente")
        } catch {
          toast.success("Usuario registrado exitosamente")
        }
      } else if (event.data.includes("AUTH_NK")) {
        try {
          const nkIdx = event.data.indexOf("AUTH_NK")
          const jsonStr = event.data.slice(nkIdx + "AUTH_NK".length)
          const json = JSON.parse(jsonStr)
          toast.error(json.message || "Error al registrar usuario")
        } catch {
          toast.error("Error al registrar usuario")
        }
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
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password) {
      toast.error("Por favor completa todos los campos")
      return
    }
    
    if (password.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres")
      return
    }
    
    if (!email.includes("@")) {
      toast.error("Por favor ingresa un email válido")
      return
    }
    
    setIsLoading(true)
    toast.info("Registrando usuario...")
    const fullMessage = `AUTH_register ${email} ${password}`
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(fullMessage)
    } else {
      console.warn("⏳ WebSocket aún no está listo. Esperando reconexión...")
      setIsLoading(false)
    }
  }

  return (
    <div className={cn("flex flex-col items-center justify-center mt-10", className)} {...props}>
      <Card className="w-full max-w-md shadow-lg border border-border">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Crear cuenta</CardTitle>
          <CardDescription>Regístrate con tu correo institucional</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="email">Correo institucional</Label>
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
              {isLoading ? "Registrando..." : "Registrarse"}
            </Button>
            <div className="text-center">
              <span className="text-sm text-muted-foreground">
                ¿Ya tienes una cuenta?{" "}
              </span>
              <Button
                type="button"
                variant="link"
                className="p-0 h-auto text-sm"
                onClick={() => navigate("/login")}
              >
                Iniciar sesión
              </Button>
            </div>
            {response && (
              <div className="text-sm text-muted-foreground text-center">
                {(() => {
                  const idx = response.indexOf("AUTH_OK")
                  if (idx !== -1) {
                    try {
                      const data = JSON.parse(response.slice(idx + "AUTH_OK".length))
                      return data.message || "Usuario registrado"
                    } catch {
                      return "Usuario registrado exitosamente"
                    }
                  }
                  const nkIdx = response.indexOf("AUTH_NK")
                  if (nkIdx !== -1) {
                    try {
                      const data = JSON.parse(response.slice(nkIdx + "AUTH_NK".length))
                      return data.message || "Error de registro"
                    } catch {
                      return "Error de registro"
                    }
                  }
                  return response
                })()}
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}