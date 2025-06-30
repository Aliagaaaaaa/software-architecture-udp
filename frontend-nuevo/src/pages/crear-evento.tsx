"use client"

import { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Plus, Calendar, User, Clock, MoreVertical, Edit, Trash2, CalendarDays, Users } from "lucide-react"
import { toast } from "sonner"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Event = {
  id_evento: number
  nombre: string
  descripcion: string
  fecha: string
  creador_id: number
  creador_email: string
  created_at: string
  updated_at?: string
}

export function CrearEvento() {
  const [user, setUser] = useState<any>(null)
  const [allEvents, setAllEvents] = useState<Event[]>([])
  const [myEvents, setMyEvents] = useState<Event[]>([])
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingEvent, setEditingEvent] = useState<Event | null>(null)
  const [newEventName, setNewEventName] = useState("")
  const [newEventDescription, setNewEventDescription] = useState("")
  const [newEventDate, setNewEventDate] = useState("")
  const [editEventName, setEditEventName] = useState("")
  const [editEventDescription, setEditEventDescription] = useState("")
  const [editEventDate, setEditEventDate] = useState("")
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  const loadAllEvents = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `EVNTSlist_events ${token}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }
  }

  const loadMyEvents = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `EVNTSlist_my_events ${token}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
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
      loadAllEvents()
      loadMyEvents()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de listar todos los eventos
      if (event.data.includes("EVNTSOK") && event.data.includes("Se encontraron")) {
        try {
          const evntsOkIndex = event.data.indexOf("EVNTSOK")
          const jsonString = event.data.slice(evntsOkIndex + "EVNTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.events) {
            setAllEvents(json.events)
          }
        } catch (err) {
          console.error("Error al parsear todos los eventos:", err)
        }
      }
      
      // Respuesta de listar mis eventos
      if (event.data.includes("EVNTSOK") && event.data.includes("eventos creados")) {
        try {
          const evntsOkIndex = event.data.indexOf("EVNTSOK")
          const jsonString = event.data.slice(evntsOkIndex + "EVNTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.events) {
            setMyEvents(json.events)
          }
        } catch (err) {
          console.error("Error al parsear mis eventos:", err)
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  const handleCreateEvent = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newEventName.trim() || !newEventDescription.trim() || !newEventDate) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `EVNTScreate_event ${token} '${newEventName}' '${newEventDescription}' ${newEventDate}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de creación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("EVNTSOK") && event.data.includes("creado exitosamente")) {
          try {
            // Extraer el ID del evento de la respuesta
            const evntsOkIndex = event.data.indexOf("EVNTSOK")
            const jsonString = event.data.slice(evntsOkIndex + "EVNTSOK".length)
            const json = JSON.parse(jsonString)
            
            if (json.success && json.event && json.event.id_evento) {
              // Crear notificación de evento para todos los usuarios
              const token = localStorage.getItem("token")
              const notificationMessage = `NOTIFcreate_event_notification ${token} ${json.event.id_evento} '${newEventName}' '${newEventDescription}'`
              console.log("📤 Enviando notificación de evento:", notificationMessage)
              if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
                socketRef.current.send(notificationMessage)
              }
            }
          } catch (err) {
            console.error("Error enviando notificación de evento:", err)
          }
          
          setIsCreateDialogOpen(false)
          setNewEventName("")
          setNewEventDescription("")
          setNewEventDate("")
          setLoading(false)
          toast.success("Evento creado exitosamente")
          loadAllEvents()
          loadMyEvents()
        } else if (event.data.includes("EVNTSNK")) {
          setLoading(false)
          toast.error("Error creando evento")
          console.error("Error creando evento")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleEditEvent = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingEvent || !editEventName.trim() || !editEventDescription.trim() || !editEventDate) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `EVNTSupdate_event ${token} ${editingEvent.id_evento} '${editEventName}' '${editEventDescription}' ${editEventDate}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de actualización
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("EVNTSOK") && event.data.includes("actualizado exitosamente")) {
          setIsEditDialogOpen(false)
          setEditingEvent(null)
          setEditEventName("")
          setEditEventDescription("")
          setEditEventDate("")
          setLoading(false)
          toast.success("Evento actualizado exitosamente")
          loadAllEvents()
          loadMyEvents()
        } else if (event.data.includes("EVNTSNK")) {
          setLoading(false)
          toast.error("Error actualizando evento")
          console.error("Error actualizando evento")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleDeleteEvent = (eventId: number, isAdmin = false) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este evento?")) return

    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = isAdmin 
        ? `EVNTSadmin_delete_event ${token} ${eventId}`
        : `EVNTSdelete_event ${token} ${eventId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de eliminación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("EVNTSOK") && event.data.includes("eliminado exitosamente")) {
          loadAllEvents()
          loadMyEvents()
        } else if (event.data.includes("EVNTSNK")) {
          console.error("Error eliminando evento")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const openEditDialog = (event: Event) => {
    setEditingEvent(event)
    setEditEventName(event.nombre)
    setEditEventDescription(event.descripcion)
    setEditEventDate(event.fecha)
    setIsEditDialogOpen(true)
  }

  const canEditOrDelete = (event: Event) => {
    return user && (user.email === event.creador_email || user.rol === "moderador")
  }

  const canAdminDelete = (event: Event) => {
    return user && user.rol === "moderador" && user.email !== event.creador_email
  }

  const isEventPast = (eventDate: string) => {
    return new Date(eventDate) < new Date()
  }

  const isEventToday = (eventDate: string) => {
    const today = new Date()
    const event = new Date(eventDate)
    return today.toDateString() === event.toDateString()
  }

  const isEventSoon = (eventDate: string) => {
    const today = new Date()
    const event = new Date(eventDate)
    const diffTime = event.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays <= 7 && diffDays > 0
  }

  const getEventBadge = (eventDate: string) => {
    if (isEventPast(eventDate)) {
      return <Badge variant="secondary">Pasado</Badge>
    } else if (isEventToday(eventDate)) {
      return <Badge variant="default" className="bg-red-500 hover:bg-red-600">¡Hoy!</Badge>
    } else if (isEventSoon(eventDate)) {
      return <Badge variant="default" className="bg-orange-500 hover:bg-orange-600">Próximo</Badge>
    } else {
      return <Badge variant="outline">Futuro</Badge>
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
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Gestión de Eventos</h1>
                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Crear Evento
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Crear Nuevo Evento</DialogTitle>
                      <DialogDescription>
                        Programa un evento para compartir con la comunidad.
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleCreateEvent} className="space-y-4">
                      <div>
                        <Label htmlFor="name">Nombre del evento</Label>
                        <Input
                          id="name"
                          value={newEventName}
                          onChange={(e) => setNewEventName(e.target.value)}
                          placeholder="Ej: Conferencia de Tecnología"
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="description">Descripción</Label>
                        <Textarea
                          id="description"
                          value={newEventDescription}
                          onChange={(e) => setNewEventDescription(e.target.value)}
                          placeholder="Describe el evento, objetivos, agenda, etc."
                          rows={4}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="date">Fecha del evento</Label>
                        <Input
                          id="date"
                          type="date"
                          value={newEventDate}
                          onChange={(e) => setNewEventDate(e.target.value)}
                          min={new Date().toISOString().split('T')[0]}
                          required
                        />
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setIsCreateDialogOpen(false)}
                        >
                          Cancelar
                        </Button>
                        <Button type="submit" disabled={loading}>
                          {loading ? "Creando..." : "Crear Evento"}
                        </Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              {/* Dialog para editar evento */}
              <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Editar Evento</DialogTitle>
                    <DialogDescription>
                      Modifica la información del evento.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleEditEvent} className="space-y-4">
                    <div>
                      <Label htmlFor="edit-name">Nombre del evento</Label>
                      <Input
                        id="edit-name"
                        value={editEventName}
                        onChange={(e) => setEditEventName(e.target.value)}
                        placeholder="Ej: Conferencia de Tecnología"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit-description">Descripción</Label>
                      <Textarea
                        id="edit-description"
                        value={editEventDescription}
                        onChange={(e) => setEditEventDescription(e.target.value)}
                        placeholder="Describe el evento, objetivos, agenda, etc."
                        rows={4}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit-date">Fecha del evento</Label>
                      <Input
                        id="edit-date"
                        type="date"
                        value={editEventDate}
                        onChange={(e) => setEditEventDate(e.target.value)}
                        required
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setIsEditDialogOpen(false)}
                      >
                        Cancelar
                      </Button>
                      <Button type="submit" disabled={loading}>
                        {loading ? "Guardando..." : "Guardar Cambios"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>

              <Tabs defaultValue="all" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="all">
                    <CalendarDays className="mr-2 h-4 w-4" />
                    Todos los Eventos ({allEvents.length})
                  </TabsTrigger>
                  <TabsTrigger value="my">
                    <Users className="mr-2 h-4 w-4" />
                    Mis Eventos ({myEvents.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CalendarDays className="h-5 w-5" />
                        Todos los Eventos
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {allEvents.length > 0 ? (
                        <div className="space-y-3">
                          {allEvents.map((event) => (
                            <Card key={event.id_evento} className={`border-l-4 ${
                              isEventPast(event.fecha) ? 'border-l-gray-400' :
                              isEventToday(event.fecha) ? 'border-l-red-500' :
                              isEventSoon(event.fecha) ? 'border-l-orange-500' :
                              'border-l-blue-500'
                            }`}>
                              <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                  <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                      <h3 className="font-semibold text-lg">{event.nombre}</h3>
                                      {getEventBadge(event.fecha)}
                                    </div>
                                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                      <div className="flex items-center gap-1">
                                        <User className="h-3 w-3" />
                                        <span>Creado por: {event.creador_email}</span>
                                      </div>
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3" />
                                        <span>{new Date(event.fecha).toLocaleDateString('es-ES', {
                                          weekday: 'long',
                                          year: 'numeric',
                                          month: 'long',
                                          day: 'numeric'
                                        })}</span>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  {canEditOrDelete(event) && (
                                    <DropdownMenu>
                                      <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                          <MoreVertical className="h-4 w-4" />
                                        </Button>
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent align="end">
                                        {user.email === event.creador_email && (
                                          <DropdownMenuItem onClick={() => openEditDialog(event)}>
                                            <Edit className="mr-2 h-4 w-4" />
                                            Editar
                                          </DropdownMenuItem>
                                        )}
                                        <DropdownMenuItem 
                                          onClick={() => handleDeleteEvent(event.id_evento, canAdminDelete(event))}
                                          className="text-red-600"
                                        >
                                          <Trash2 className="mr-2 h-4 w-4" />
                                          Eliminar
                                        </DropdownMenuItem>
                                      </DropdownMenuContent>
                                    </DropdownMenu>
                                  )}
                                </div>
                              </CardHeader>
                              <CardContent className="pt-0">
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                  {event.descripcion}
                                </p>
                                {event.updated_at && (
                                  <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                                    <Clock className="h-3 w-3" />
                                    <span>Actualizado: {new Date(event.updated_at).toLocaleDateString()}</span>
                                  </div>
                                )}
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No hay eventos programados.</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            ¡Sé el primero en crear un evento!
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="my" className="space-y-4">
      <Card>
        <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5" />
                        Mis Eventos Creados
                      </CardTitle>
        </CardHeader>
        <CardContent>
                      {myEvents.length > 0 ? (
                        <div className="space-y-3">
                          {myEvents.map((event) => (
                            <Card key={event.id_evento} className={`border-l-4 ${
                              isEventPast(event.fecha) ? 'border-l-gray-400' :
                              isEventToday(event.fecha) ? 'border-l-red-500' :
                              isEventSoon(event.fecha) ? 'border-l-orange-500' :
                              'border-l-green-500'
                            }`}>
                              <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                  <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                      <h3 className="font-semibold text-lg">{event.nombre}</h3>
                                      {getEventBadge(event.fecha)}
                                    </div>
                                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                      <div className="flex items-center gap-1">
                                        <Calendar className="h-3 w-3" />
                                        <span>{new Date(event.fecha).toLocaleDateString('es-ES', {
                                          weekday: 'long',
                                          year: 'numeric',
                                          month: 'long',
                                          day: 'numeric'
                                        })}</span>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                        <MoreVertical className="h-4 w-4" />
                                      </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                      <DropdownMenuItem onClick={() => openEditDialog(event)}>
                                        <Edit className="mr-2 h-4 w-4" />
                                        Editar
                                      </DropdownMenuItem>
                                      <DropdownMenuItem 
                                        onClick={() => handleDeleteEvent(event.id_evento)}
                                        className="text-red-600"
                                      >
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Eliminar
                                      </DropdownMenuItem>
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                </div>
                              </CardHeader>
                              <CardContent className="pt-0">
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                  {event.descripcion}
                                </p>
                                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    <span>Creado: {new Date(event.created_at).toLocaleDateString()}</span>
                                  </div>
                                  {event.updated_at && (
                                    <div className="flex items-center gap-1">
                                      <Clock className="h-3 w-3" />
                                      <span>Actualizado: {new Date(event.updated_at).toLocaleDateString()}</span>
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No has creado eventos aún.</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            ¡Crea tu primer evento para compartir con la comunidad!
                          </p>
                        </div>
                      )}
        </CardContent>
      </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
    </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
