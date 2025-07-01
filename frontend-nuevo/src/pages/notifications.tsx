"use client"

import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bell, BellOff, CheckCircle, Trash2, RefreshCw, MessageCircle, FileText, Users, Settings } from "lucide-react"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Notification = {
  id_notificacion: number
  titulo: string
  mensaje: string
  tipo: string
  referencia_id: number
  referencia_tipo: string
  leido: boolean
  fecha: string
  creador_id?: number
}

type Subscription = {
  id_suscripcion: number
  foro_id?: number
  post_id?: number
  fecha_suscripcion: string
  titulo_foro?: string
  titulo_post?: string
  categoria?: string
}

export function NotificationsPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [forumSubscriptions, setForumSubscriptions] = useState<Subscription[]>([])
  const [postSubscriptions, setPostSubscriptions] = useState<Subscription[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      toast.error("Sesión expirada. Por favor inicia sesión nuevamente.")
      navigate("/login")
      return
    }

    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      setUser({
        name: payload.name || payload.email,
        email: payload.email,
        avatar: payload.avatar || "",
        rol: payload.rol
      })

      // Conectar WebSocket
      const socket = new WebSocket("ws://4.228.228.99:3001")
      socketRef.current = socket

      socket.onopen = () => {
        console.log("🔌 WebSocket conectado")
        loadNotifications()
        loadSubscriptions()
      }

      socket.onmessage = (event) => {
        console.log("📨 Respuesta del backend:", event.data)
        
        if (event.data.includes("NOTIFOK")) {
          try {
            const notifOkIndex = event.data.indexOf("NOTIFOK")
            const jsonString = event.data.slice(notifOkIndex + "NOTIFOK".length)
            const response = JSON.parse(jsonString)

                          if (response.success) {
                // Manejar diferentes tipos de respuestas
                if (response.notifications) {
                  setNotifications(response.notifications)
                } else if (response.subscriptions) {
                  // Determinar si son suscripciones de foro o post basado en el contenido
                  if (response.subscriptions.length > 0 && 'titulo_foro' in response.subscriptions[0]) {
                    setForumSubscriptions(response.subscriptions)
                  } else if (response.subscriptions.length > 0 && 'titulo_post' in response.subscriptions[0]) {
                    setPostSubscriptions(response.subscriptions)
                  }
                } else if (response.unread_count !== undefined) {
                  setUnreadCount(response.unread_count)
                }

              if (response.message && !response.message.includes("encontraron")) {
                toast.success(response.message)
              }
            } else {
              toast.error(response.message || "Error en la operación")
            }
          } catch (err) {
            console.error("Error al parsear respuesta:", err)
          }
        }
        
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

    } catch (err) {
      console.error("Error parsing token:", err)
      toast.error("Error al verificar la sesión")
      navigate("/login")
    }
  }, [navigate])

  const loadNotifications = () => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFlist_notifications ${token} 50`)
      socketRef.current.send(`NOTIFget_unread_count ${token}`)
    }
  }

  const loadSubscriptions = () => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      socketRef.current.send(`NOTIFlist_forum_subscriptions ${token}`)
      socketRef.current.send(`NOTIFlist_post_subscriptions ${token}`)
    }
  }

  const markAsRead = (notificationId: number) => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFmark_as_read ${token} ${notificationId}`)
      // Actualizar el estado local inmediatamente
      setNotifications(prev => 
        prev.map(notif => 
          notif.id_notificacion === notificationId 
            ? { ...notif, leido: true }
            : notif
        )
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    }
  }

  const markAllAsRead = () => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFmark_all_as_read ${token}`)
      // Actualizar estado local
      setNotifications(prev => prev.map(notif => ({ ...notif, leido: true })))
      setUnreadCount(0)
    }
  }

  const deleteNotification = (notificationId: number) => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFdelete_notification ${token} ${notificationId}`)
      // Actualizar estado local
      setNotifications(prev => prev.filter(notif => notif.id_notificacion !== notificationId))
    }
  }

  const unsubscribeForum = (forumId: number) => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFunsubscribe_forum ${token} ${forumId}`)
      // Actualizar estado local
      setForumSubscriptions(prev => prev.filter(sub => sub.foro_id !== forumId))
    }
  }

  const unsubscribePost = (postId: number) => {
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && token) {
      setLoading(true)
      socketRef.current.send(`NOTIFunsubscribe_post ${token} ${postId}`)
      // Actualizar estado local
      setPostSubscriptions(prev => prev.filter(sub => sub.post_id !== postId))
    }
  }

  const getNotificationIcon = (tipo: string) => {
    switch (tipo) {
      case 'mensaje': return <MessageCircle className="h-4 w-4" />
      case 'foro': case 'post': return <FileText className="h-4 w-4" />
      case 'comentario': return <MessageCircle className="h-4 w-4" />
      default: return <Bell className="h-4 w-4" />
    }
  }

  const getNotificationColor = (tipo: string) => {
    switch (tipo) {
      case 'mensaje': return 'bg-blue-500'
      case 'foro': return 'bg-green-500'
      case 'post': return 'bg-purple-500'
      case 'comentario': return 'bg-orange-500'
      default: return 'bg-gray-500'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    // Marcar como leída si no lo está
    if (!notification.leido) {
      markAsRead(notification.id_notificacion)
    }

    // Navegar según el tipo de notificación
    if (notification.referencia_tipo === 'post' && notification.referencia_id) {
      navigate(`/post/${notification.referencia_id}`)
    } else if (notification.referencia_tipo === 'comentario' && notification.referencia_id) {
      // Para comentarios, navegar al post que contiene el comentario
      // Aquí necesitaríamos el post_id, pero podemos usar referencia_id si apunta al post
      navigate(`/post/${notification.referencia_id}`)
    } else if (notification.tipo === 'mensaje') {
      navigate('/messages')
    } else if (notification.tipo === 'evento' || notification.referencia_tipo === 'evento') {
      navigate('/crear-evento')
    }
  }

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" user={user} />
      <SidebarInset>
        <SiteHeader user={user} />
    <div className="flex flex-col gap-6 p-6">
          
          {/* Header con contadores */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Bell className="h-8 w-8" />
                Notificaciones
              </h1>
              <p className="text-muted-foreground">
                Gestiona tus notificaciones y suscripciones
              </p>
            </div>
            <div className="flex items-center gap-4">
              {unreadCount > 0 && (
                <Badge variant="destructive" className="text-sm">
                  {unreadCount} sin leer
                </Badge>
              )}
              <Button onClick={loadNotifications} disabled={loading} variant="outline">
                <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Actualizar
              </Button>
            </div>
          </div>

          <Tabs defaultValue="notifications" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="notifications" className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                Notificaciones
              </TabsTrigger>
              <TabsTrigger value="forum-subs" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Foros ({forumSubscriptions.length})
              </TabsTrigger>
              <TabsTrigger value="post-subs" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Posts ({postSubscriptions.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="notifications" className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Mis Notificaciones</h2>
                {notifications.filter(n => !n.leido).length > 0 && (
                  <Button onClick={markAllAsRead} variant="outline" size="sm">
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Marcar todas como leídas
                  </Button>
                )}
              </div>

              {notifications.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <Bell className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No tienes notificaciones</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-2">
                  {notifications.map((notification) => (
                    <Card 
                      key={notification.id_notificacion} 
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        !notification.leido ? 'border-l-4 border-l-blue-500 bg-blue-50/50' : ''
                      }`}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            <div className={`p-2 rounded-full ${getNotificationColor(notification.tipo)} text-white`}>
                              {getNotificationIcon(notification.tipo)}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium mb-1">
                                {notification.titulo}
                                {!notification.leido && (
                                  <Badge variant="secondary" className="ml-2 text-xs">
                                    Nuevo
                                  </Badge>
                                )}
                              </h4>
                              <p className="text-sm text-muted-foreground mb-2">
                                {notification.mensaje}
                              </p>
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <Badge variant="outline" className="text-xs">
                                  {notification.tipo}
                                </Badge>
                                <span>{formatDate(notification.fecha)}</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {!notification.leido && (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  markAsRead(notification.id_notificacion)
                                }}
                              >
                                <CheckCircle className="h-4 w-4" />
                              </Button>
                            )}
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteNotification(notification.id_notificacion)
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="forum-subs" className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Suscripciones a Foros</h2>
                <p className="text-sm text-muted-foreground">
                  Recibes notificaciones cuando se publican nuevos posts
                </p>
              </div>

              {forumSubscriptions.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-8">
                    <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No estás suscrito a ningún foro</p>
                    <Button className="mt-4" onClick={() => navigate('/forums')}>
                      Explorar Foros
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {forumSubscriptions.map((subscription) => (
                    <Card key={subscription.id_suscripcion}>
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg">{subscription.titulo_foro}</CardTitle>
                            <Badge variant="secondary" className="mt-1">
                              {subscription.categoria}
                            </Badge>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => unsubscribeForum(subscription.foro_id!)}
                          >
                            <BellOff className="h-4 w-4 mr-2" />
                            Desuscribirse
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-muted-foreground">
                          Suscrito desde: {formatDate(subscription.fecha_suscripcion)}
                        </p>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="mt-2 p-0 h-auto"
                          onClick={() => navigate(`/forum/${subscription.foro_id}`)}
                        >
                          Ver foro →
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="post-subs" className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Suscripciones a Posts</h2>
                <p className="text-sm text-muted-foreground">
                  Recibes notificaciones cuando se agregan nuevos comentarios
                </p>
              </div>

              {postSubscriptions.length === 0 ? (
      <Card>
                  <CardContent className="text-center py-8">
                    <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No estás suscrito a ningún post</p>
                    <Button className="mt-4" onClick={() => navigate('/forums')}>
                      Explorar Posts
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {postSubscriptions.map((subscription) => (
                    <Card key={subscription.id_suscripcion}>
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <CardTitle className="text-lg line-clamp-2">
                              {subscription.titulo_post}
                            </CardTitle>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => unsubscribePost(subscription.post_id!)}
                          >
                            <BellOff className="h-4 w-4 mr-2" />
                            Desuscribirse
                          </Button>
                        </div>
        </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-muted-foreground">
                          Suscrito desde: {formatDate(subscription.fecha_suscripcion)}
                        </p>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="mt-2 p-0 h-auto"
                          onClick={() => navigate(`/post/${subscription.post_id}`)}
                        >
                          Ver post →
                        </Button>
        </CardContent>
      </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
    </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
