"use client"

import { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Info, Server, RefreshCw, CheckCircle, XCircle } from "lucide-react"
import { toast } from "sonner"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type ServiceInfo = {
  service_name: string
  description: string
  version: string
  methods: string[]
  status: string
  [key: string]: any
}

export default function SystemInfo() {
  const [services, setServices] = useState<ServiceInfo[]>([])
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  const serviceNames = [
    { name: "AUTH_", label: "Autenticación" },
    { name: "FORUM", label: "Foros" },
    { name: "POSTS", label: "Posts" },
    { name: "COMMS", label: "Comentarios" },
    { name: "EVNTS", label: "Eventos" },
    { name: "MSGES", label: "Mensajes" },
    { name: "NOTIF", label: "Notificaciones" },
    { name: "PROFS", label: "Perfiles" },
    { name: "reprt", label: "Reportes" }
  ]

  const loadServiceInfo = () => {
    setLoading(true)
    setServices([])
    toast.info("Actualizando información de servicios...")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      serviceNames.forEach(service => {
        const message = `${service.name}info`
        console.log("📤 Enviando mensaje:", message)
        socketRef.current?.send(message)
      })
    } else {
      setLoading(false)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    const payload = JSON.parse(atob(token.split(".")[1]))
    setUser({
      name: payload.name || payload.email,
      email: payload.email,
      avatar: payload.avatar || "",
      rol: payload.rol
    })

    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket

    socket.onopen = () => {
      console.log("🔌 WebSocket conectado")
      loadServiceInfo()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Buscar respuestas de información de servicios
      serviceNames.forEach(service => {
        if (event.data.includes(`${service.name}OK`)) {
          try {
            const serviceOkIndex = event.data.indexOf(`${service.name}OK`)
            const jsonString = event.data.slice(serviceOkIndex + `${service.name}OK`.length)
            console.log(`📝 Respuesta cruda de ${service.name}:`, jsonString)
            const json = JSON.parse(jsonString)
            
            const serviceInfo: ServiceInfo = {
              service_name: json.service_name || json.service || service.name.toLowerCase(),
              description: json.description || "Sin descripción",
              version: json.version || "1.0.0",
              methods: Array.isArray(json.methods) ? json.methods : Object.keys(json.methods || {}),
              status: json.status || "running",
              label: service.label,
              ...json
            }
            
            setServices(prev => {
              const filtered = prev.filter(s => s.service_name !== serviceInfo.service_name)
              return [...filtered, serviceInfo]
            })
          } catch (err) {
            console.error(`Error al parsear info de ${service.name}:`, err)
            console.log("Respuesta completa:", event.data)
          }
        }
      })
      
      setLoading(false)
    }

    socket.onerror = (err) => {
      console.error("❌ WebSocket error:", err)
      setLoading(false)
    }
    socket.onclose = () => {
      console.log("🔒 WebSocket cerrado")
    }

    return () => socket.close()
  }, [navigate])

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "running":
        return <Badge variant="default" className="flex items-center gap-1"><CheckCircle className="h-3 w-3" />Activo</Badge>
      case "stopped":
        return <Badge variant="destructive" className="flex items-center gap-1"><XCircle className="h-3 w-3" />Detenido</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" user={user} />
      <SidebarInset>
        <SiteHeader user={user} />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6 px-4 lg:px-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-semibold flex items-center gap-2">
                    <Info className="h-6 w-6" />
                    Información del Sistema
                  </h2>
                  <p className="text-muted-foreground">
                    Estado y configuración de todos los servicios
                  </p>
                </div>
                <Button 
                  onClick={loadServiceInfo} 
                  disabled={loading}
                  variant="outline"
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? "Actualizando..." : "Actualizar"}
                </Button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {services.map((service) => (
                  <Card key={service.service_name} className="h-fit">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <Server className="h-5 w-5" />
                          {service.label || service.service_name}
                        </CardTitle>
                        {getStatusBadge(service.status)}
                      </div>
                      <CardDescription>
                        {service.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Versión:</span>
                          <span className="font-mono">{service.version}</span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Métodos:</span>
                          <span className="font-mono">{service.methods.length}</span>
                        </div>

                        {service.total_users !== undefined && (
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Usuarios:</span>
                            <span className="font-mono">{service.total_users}</span>
                          </div>
                        )}

                        {service.total_profiles !== undefined && (
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Perfiles:</span>
                            <span className="font-mono">{service.total_profiles}</span>
                          </div>
                        )}


                      </div>

                      {service.methods.length > 0 && (
                        <div className="space-y-2">
                          <Separator />
                          <div>
                            <div className="text-sm font-medium mb-2">Métodos disponibles:</div>
                            <div className="flex flex-wrap gap-1">
                              {service.methods.slice(0, 6).map((method) => (
                                <Badge key={method} variant="secondary" className="text-xs">
                                  {method}
                                </Badge>
                              ))}
                              {service.methods.length > 6 && (
                                <Badge variant="outline" className="text-xs">
                                  +{service.methods.length - 6} más
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>

              {services.length === 0 && !loading && (
                <div className="text-center py-8">
                  <Server className="mx-auto h-12 w-12 text-muted-foreground" />
                  <p className="text-muted-foreground mt-2">
                    No se pudo obtener información de los servicios
                  </p>
                </div>
              )}

              {loading && (
                <div className="text-center py-8">
                  <RefreshCw className="mx-auto h-12 w-12 text-muted-foreground animate-spin" />
                  <p className="text-muted-foreground mt-2">
                    Cargando información de los servicios...
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
} 