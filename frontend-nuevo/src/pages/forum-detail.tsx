"use client"

import { useEffect, useState, useRef } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ArrowLeft, Plus, MessageSquare, User, Calendar, Bell, BellOff } from "lucide-react"
import { toast } from "sonner"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Forum = {
  id_foro: number
  titulo: string
  categoria: string
  creador_email: string
}

type Post = {
  id_post: number
  contenido: string
  fecha: string
  autor_email: string
  id_foro: number
}

export default function ForumDetail() {
  const { forumId } = useParams<{ forumId: string }>()
  const [forum, setForum] = useState<Forum | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [user, setUser] = useState<any>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newPostContent, setNewPostContent] = useState("")
  const [loading, setLoading] = useState(false)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [subscriptionLoading, setSubscriptionLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  const loadForum = () => {
    const token = localStorage.getItem("token")
    if (token && forumId && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMget_forum ${token} ${forumId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }
  }

  const loadPosts = () => {
    const token = localStorage.getItem("token")
    if (token && forumId && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTSlist_posts ${token} ${forumId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }
  }

  const checkSubscription = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(`NOTIFlist_forum_subscriptions ${token}`)
    }
  }

  const toggleSubscription = () => {
    const token = localStorage.getItem("token")
    if (token && forumId && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setSubscriptionLoading(true)
      const action = isSubscribed ? 'unsubscribe_forum' : 'subscribe_forum'
      const message = `NOTIF${action} ${token} ${forumId}`
      console.log("📤 Enviando mensaje de suscripción:", message)
      socketRef.current.send(message)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    if (!forumId) {
      navigate("/forums")
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
      loadForum()
      loadPosts()
      checkSubscription()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de obtener foro
      if (event.data.includes("FORUMOK") && event.data.includes("encontrado")) {
        try {
          const forumOkIndex = event.data.indexOf("FORUMOK")
          const jsonString = event.data.slice(forumOkIndex + "FORUMOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.forum) {
            setForum(json.forum)
          }
        } catch (err) {
          console.error("Error al parsear foro:", err)
          toast.error("Error cargando información del foro")
        }
      }
      
      // Respuesta de listar posts
      if (event.data.includes("POSTSOK")) {
        try {
          const postsOkIndex = event.data.indexOf("POSTSOK")
          const jsonString = event.data.slice(postsOkIndex + "POSTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.posts) {
            setPosts(json.posts)
          }
        } catch (err) {
          console.error("Error al parsear posts:", err)
          toast.error("Error cargando posts")
        }
      }

      // Respuesta de notificaciones
      if (event.data.includes("NOTIFOK")) {
        try {
          const notifOkIndex = event.data.indexOf("NOTIFOK")
          const jsonString = event.data.slice(notifOkIndex + "NOTIFOK".length)
          const response = JSON.parse(jsonString)

          if (response.success) {
            // Verificar si estamos suscritos a este foro
            if (response.subscriptions && forumId) {
              const subscribed = response.subscriptions.some((sub: any) => 
                sub.foro_id === parseInt(forumId)
              )
              setIsSubscribed(subscribed)
            }

            // Mensajes de suscripción/desuscripción
            if (response.message && (response.message.includes("suscrito") || response.message.includes("desuscrito"))) {
              toast.success(response.message)
              setIsSubscribed(!isSubscribed)
              setSubscriptionLoading(false)
            }
          } else {
            if (response.message && subscriptionLoading) {
              toast.error(response.message)
              setSubscriptionLoading(false)
            }
          }
        } catch (err) {
          console.error("Error al parsear respuesta de notificaciones:", err)
          setSubscriptionLoading(false)
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate, forumId])

  const handleCreatePost = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newPostContent.trim()) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTScreate_post ${token} ${forumId} '${newPostContent}'`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de creación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("POSTSOK") && event.data.includes("creado exitosamente")) {
          // Extraer el ID del post de la respuesta para crear notificación
          try {
            const postsOkIndex = event.data.indexOf("POSTSOK")
            const jsonString = event.data.slice(postsOkIndex + "POSTSOK".length)
            const response = JSON.parse(jsonString)
            
            if (response.success && response.post && response.post.id_post && forum) {
              // Crear notificación para suscriptores del foro
              const token = localStorage.getItem("token")
              if (token) {
                const notificationMessage = `NOTIFcreate_post_notification ${token} ${forumId} ${response.post.id_post} '${newPostContent.substring(0, 50)}...'`
                socketRef.current?.send(notificationMessage)
              }
            }
          } catch (err) {
            console.error("Error procesando respuesta de post:", err)
          }
          
          setIsCreateDialogOpen(false)
          setNewPostContent("")
          setLoading(false)
          toast.success("Post creado exitosamente")
          loadPosts() // Recargar la lista
        } else if (event.data.includes("POSTSNK")) {
          setLoading(false)
          toast.error("Error creando post")
          console.error("Error creando post")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handlePostClick = (postId: number) => {
    navigate(`/post/${postId}`)
  }

  const handleBackToForums = () => {
    navigate("/forums")
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
              <div className="flex items-center gap-4">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleBackToForums}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Volver a Foros
                </Button>
              </div>

              {forum && (
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h1 className="text-3xl font-bold">{forum.titulo}</h1>
                      <p className="text-muted-foreground mt-1">
                        Categoría: {forum.categoria} • Creado por: {forum.creador_email}
                      </p>
                    </div>
                    <Button
                      variant={isSubscribed ? "outline" : "default"}
                      onClick={toggleSubscription}
                      disabled={subscriptionLoading}
                      className="min-w-[140px]"
                    >
                      {subscriptionLoading ? (
                        "Procesando..."
                      ) : isSubscribed ? (
                        <>
                          <BellOff className="mr-2 h-4 w-4" />
                          Desuscribirse
                        </>
                      ) : (
                        <>
                          <Bell className="mr-2 h-4 w-4" />
                          Suscribirse
                        </>
                      )}
                    </Button>
                  </div>

                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold">Posts del Foro</h2>
                    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="mr-2 h-4 w-4" />
                          Nuevo Post
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Crear Nuevo Post</DialogTitle>
                          <DialogDescription>
                            Comparte tus ideas en el foro "{forum.titulo}".
                          </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleCreatePost} className="space-y-4">
                          <div>
                            <Label htmlFor="content">Contenido del Post</Label>
                            <Textarea
                              id="content"
                              value={newPostContent}
                              onChange={(e) => setNewPostContent(e.target.value)}
                              placeholder="Escribe tu post aquí..."
                              rows={6}
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
                              {loading ? "Publicando..." : "Publicar Post"}
                            </Button>
                          </div>
                        </form>
                      </DialogContent>
                    </Dialog>
                  </div>

                  <div className="space-y-4">
                    {posts.map((post) => (
                      <Card 
                        key={post.id_post} 
                        className="cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => handlePostClick(post.id_post)}
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <User className="h-3 w-3" />
                                {post.autor_email}
                                <Calendar className="h-3 w-3 ml-2" />
                                {new Date(post.fecha).toLocaleDateString()}
                              </div>
                            </div>
                            <MessageSquare className="h-4 w-4 text-muted-foreground" />
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm leading-relaxed">
                            {post.contenido.length > 200 
                              ? `${post.contenido.substring(0, 200)}...` 
                              : post.contenido
                            }
                          </p>
                          <div className="mt-3 text-xs text-muted-foreground">
                            Click para ver comentarios
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {posts.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No hay posts en este foro.</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        ¡Sé el primero en crear uno!
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
} 