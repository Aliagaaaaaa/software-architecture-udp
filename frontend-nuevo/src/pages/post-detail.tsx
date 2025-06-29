"use client"

import { useEffect, useState, useRef } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { ArrowLeft, Plus, MessageSquare, User, Calendar, MoreVertical, Edit, Trash2, Shield, Flag } from "lucide-react"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Post = {
  id_post: number
  contenido: string
  fecha: string
  autor_email: string
  autor_id: number
  id_foro: number
  foro_titulo: string
  created_at: string
  updated_at: string
}

type Comment = {
  id_comentario: number
  contenido: string
  fecha: string
  autor_email: string
  id_post: number
}

export default function PostDetail() {
  const { postId } = useParams()
  const [post, setPost] = useState<Post | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [user, setUser] = useState<any>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isEditPostDialogOpen, setIsEditPostDialogOpen] = useState(false)
  const [editingComment, setEditingComment] = useState<Comment | null>(null)
  const [newCommentContent, setNewCommentContent] = useState("")
  const [editCommentContent, setEditCommentContent] = useState("")
  const [editPostContent, setEditPostContent] = useState("")
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  const loadPost = () => {
    const token = localStorage.getItem("token")
    if (token && postId && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTSget_post ${token} ${postId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }
  }

  const loadComments = () => {
    const token = localStorage.getItem("token")
    if (token && postId && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `COMMSlist_comments ${token} ${postId}`
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

    if (!postId) {
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
      loadPost()
      loadComments()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de obtener post
      if (event.data.includes("POSTSOK") && event.data.includes("encontrado")) {
        try {
          const postsOkIndex = event.data.indexOf("POSTSOK")
          const jsonString = event.data.slice(postsOkIndex + "POSTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.post) {
            setPost(json.post)
          }
        } catch (err) {
          console.error("Error al parsear post:", err)
        }
      }

      // Respuesta de actualización de post
      if (event.data.includes("POSTSOK") && event.data.includes("actualizado exitosamente")) {
        try {
          toast.success("Post actualizado exitosamente")
          setIsEditPostDialogOpen(false)
          setEditPostContent("")
          setLoading(false)
          loadPost() // Recargar el post
        } catch (err) {
          console.error("Error al parsear actualización de post:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de post
      if (event.data.includes("POSTSOK") && event.data.includes("eliminado exitosamente")) {
        try {
          toast.success("Post eliminado exitosamente")
          setLoading(false)
          // Navegar de vuelta al foro
          if (post) {
            navigate(`/forum/${post.id_foro}`)
          } else {
            navigate("/forums")
          }
        } catch (err) {
          console.error("Error al parsear eliminación de post:", err)
          setLoading(false)
        }
      }
      
      // Respuesta de listar comentarios
      if (event.data.includes("COMMSOK")) {
        try {
          const commsOkIndex = event.data.indexOf("COMMSOK")
          const jsonString = event.data.slice(commsOkIndex + "COMMSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.comments) {
            setComments(json.comments)
          }
        } catch (err) {
          console.error("Error al parsear comentarios:", err)
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate, postId])

  const handleCreateComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newCommentContent.trim()) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `COMMScreate_comment ${token} ${postId} '${newCommentContent}'`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de creación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("COMMSOK") && event.data.includes("creado exitosamente")) {
          setIsCreateDialogOpen(false)
          setNewCommentContent("")
          setLoading(false)
          loadComments() // Recargar la lista
        } else if (event.data.includes("COMMSNK")) {
          setLoading(false)
          console.error("Error creando comentario")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleEditComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingComment || !editCommentContent.trim()) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `COMMSupdate_comment ${token} ${editingComment.id_comentario} '${editCommentContent}'`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de actualización
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("COMMSOK") && event.data.includes("actualizado exitosamente")) {
          setIsEditDialogOpen(false)
          setEditingComment(null)
          setEditCommentContent("")
          setLoading(false)
          loadComments() // Recargar la lista
        } else if (event.data.includes("COMMSNK")) {
          setLoading(false)
          console.error("Error actualizando comentario")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleDeleteComment = (commentId: number, isAdmin = false) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este comentario?")) return

    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = isAdmin 
        ? `COMMSadmin_delete_comment ${token} ${commentId}`
        : `COMMSdelete_comment ${token} ${commentId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de eliminación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("COMMSOK") && event.data.includes("eliminado exitosamente")) {
          loadComments() // Recargar la lista
        } else if (event.data.includes("COMMSNK")) {
          console.error("Error eliminando comentario")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const openEditDialog = (comment: Comment) => {
    setEditingComment(comment)
    setEditCommentContent(comment.contenido)
    setIsEditDialogOpen(true)
  }

  const canEditOrDelete = (comment: Comment) => {
    return user && (user.email === comment.autor_email || user.rol === "moderador")
  }

  const canAdminDelete = (comment: Comment) => {
    return user && user.rol === "moderador" && user.email !== comment.autor_email
  }

  const canEditOrDeletePost = () => {
    return post && user && (user.email === post.autor_email || user.rol === 'moderador')
  }

  const handleEditPost = (e: React.FormEvent) => {
    e.preventDefault()
    if (!post || !editPostContent.trim()) return

    if (editPostContent.length > 5000) {
      toast.error("El contenido no puede exceder 5000 caracteres")
      return
    }

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTSupdate_post ${token} ${post.id_post} '${editPostContent}'`
      console.log("📤 Actualizando post:", message)
      socketRef.current.send(message)
    }
  }

  const handleDeletePost = () => {
    if (!post) return
    
    if (confirm("¿Estás seguro de que quieres eliminar este post?")) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `POSTSdelete_post ${token} ${post.id_post}`
        console.log("📤 Eliminando post:", message)
        socketRef.current.send(message)
      }
    }
  }

  const handleAdminDeletePost = () => {
    if (!post) return
    
    if (confirm("¿Estás seguro de que quieres eliminar este post como moderador?")) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `POSTSadmin_delete_post ${token} ${post.id_post}`
        console.log("📤 Eliminando post (admin):", message)
        socketRef.current.send(message)
      }
    }
  }

  const openEditPostDialog = () => {
    if (post) {
      setEditPostContent(post.contenido)
      setIsEditPostDialogOpen(true)
    }
  }

  const handleBackToForum = () => {
    if (post) {
      navigate(`/forum/${post.id_foro}`)
    } else {
      navigate("/forums")
    }
  }

  const handleReportPost = () => {
    if (!post) return
    
    const reason = prompt("¿Por qué quieres reportar este post?\n\nDescribe brevemente la razón:")
    if (!reason || !reason.trim()) return
    
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtcreate_report ${token} ${post.id_post} post '${reason.trim()}'`
      console.log("📤 Reportando post:", message)
      socketRef.current.send(message)
      
      // Escuchar respuesta
      const originalOnMessage = socketRef.current?.onmessage
      if (socketRef.current) {
        socketRef.current.onmessage = (event) => {
          if (event.data.includes("reprtOK") && event.data.includes("creado exitosamente")) {
            toast.success("Post reportado exitosamente")
          } else if (event.data.includes("reprtNK")) {
            toast.error("Error al reportar el post")
          }
          
          // Restaurar el handler original
          if (originalOnMessage && socketRef.current) {
            socketRef.current.onmessage = originalOnMessage
          }
        }
      }
    } else {
      toast.error("Error de conexión")
    }
  }

  const handleReportComment = (comment: Comment) => {
    const reason = prompt("¿Por qué quieres reportar este comentario?\n\nDescribe brevemente la razón:")
    if (!reason || !reason.trim()) return
    
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtcreate_report ${token} ${comment.id_comentario} comentario '${reason.trim()}'`
      console.log("📤 Reportando comentario:", message)
      socketRef.current.send(message)
      
      // Escuchar respuesta
      const originalOnMessage = socketRef.current?.onmessage
      if (socketRef.current) {
        socketRef.current.onmessage = (event) => {
          if (event.data.includes("reprtOK") && event.data.includes("creado exitosamente")) {
            toast.success("Comentario reportado exitosamente")
          } else if (event.data.includes("reprtNK")) {
            toast.error("Error al reportar el comentario")
          }
          
          // Restaurar el handler original
          if (originalOnMessage && socketRef.current) {
            socketRef.current.onmessage = originalOnMessage
          }
        }
      }
    } else {
      toast.error("Error de conexión")
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
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
              <div className="flex items-center gap-4">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleBackToForum}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Volver al Foro
                </Button>
              </div>

              {post && (
                <div className="space-y-6">
                  {/* Post Principal */}
                  <Card>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span className="font-medium">Foro:</span>
                            <Badge variant="outline">{post.foro_titulo}</Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {post.autor_email}
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatDate(post.fecha)}
                            </div>
                            {post.updated_at !== post.created_at && (
                              <Badge variant="secondary" className="text-xs">
                                Editado: {formatDate(post.updated_at)}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {canEditOrDeletePost() && (
                              <>
                                <DropdownMenuItem onClick={openEditPostDialog}>
                                  <Edit className="h-4 w-4 mr-2" />
                                  Editar Post
                                </DropdownMenuItem>
                                {user?.email === post.autor_email ? (
                                  <DropdownMenuItem 
                                    onClick={handleDeletePost}
                                    className="text-destructive"
                                  >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Eliminar Post
                                  </DropdownMenuItem>
                                ) : (
                                  <DropdownMenuItem 
                                    onClick={handleAdminDeletePost}
                                    className="text-destructive"
                                  >
                                    <Shield className="h-4 w-4 mr-2" />
                                    Eliminar (Moderador)
                                  </DropdownMenuItem>
                                )}
                              </>
                            )}
                            {user?.email !== post.autor_email && (
                              <DropdownMenuItem onClick={handleReportPost} className="text-orange-600">
                                <Flag className="h-4 w-4 mr-2" />
                                Reportar Post
                              </DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-sm max-w-none">
                        <p className="whitespace-pre-wrap leading-relaxed">
                          {post.contenido}
                        </p>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Sección de Comentarios */}
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-semibold flex items-center gap-2">
                        <MessageSquare className="h-5 w-5" />
                        Comentarios ({comments.length})
                      </h2>
                      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                        <DialogTrigger asChild>
                          <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Comentar
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Nuevo Comentario</DialogTitle>
                            <DialogDescription>
                              Comparte tu opinión sobre este post.
                            </DialogDescription>
                          </DialogHeader>
                          <form onSubmit={handleCreateComment} className="space-y-4">
                            <div>
                              <Label htmlFor="content">Tu comentario</Label>
                              <Textarea
                                id="content"
                                value={newCommentContent}
                                onChange={(e) => setNewCommentContent(e.target.value)}
                                placeholder="Escribe tu comentario aquí..."
                                rows={4}
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
                                {loading ? "Enviando..." : "Enviar Comentario"}
                              </Button>
                            </div>
                          </form>
                        </DialogContent>
                      </Dialog>
                    </div>

                    {/* Dialog para editar comentario */}
                    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Editar Comentario</DialogTitle>
                          <DialogDescription>
                            Modifica tu comentario.
                          </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleEditComment} className="space-y-4">
                          <div>
                            <Label htmlFor="edit-content">Contenido del comentario</Label>
                            <Textarea
                              id="edit-content"
                              value={editCommentContent}
                              onChange={(e) => setEditCommentContent(e.target.value)}
                              placeholder="Escribe tu comentario aquí..."
                              rows={4}
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

                    {/* Dialog para editar post */}
                    <Dialog open={isEditPostDialogOpen} onOpenChange={setIsEditPostDialogOpen}>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Editar Post</DialogTitle>
                          <DialogDescription>
                            Modifica el contenido de tu publicación en el foro "{post?.foro_titulo}"
                          </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleEditPost} className="space-y-4">
                          <div>
                            <Label htmlFor="edit-post-content">Contenido del post</Label>
                            <Textarea
                              id="edit-post-content"
                              value={editPostContent}
                              onChange={(e) => setEditPostContent(e.target.value)}
                              placeholder="Contenido de la publicación..."
                              rows={8}
                              required
                            />
                            <div className="text-sm text-muted-foreground text-right mt-1">
                              {editPostContent.length}/5000 caracteres
                            </div>
                          </div>
                          <div className="flex justify-end gap-2">
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => setIsEditPostDialogOpen(false)}
                              disabled={loading}
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

                    {/* Lista de Comentarios */}
                    <div className="space-y-3">
                      {comments.map((comment) => (
                        <Card key={comment.id_comentario} className="border-l-4 border-l-blue-500">
                          <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <User className="h-3 w-3" />
                                  <span className="font-medium">{comment.autor_email}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  {new Date(comment.fecha).toLocaleDateString()}
                                </div>
                              </div>
                              
                              {/* Menú de acciones */}
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  {canEditOrDelete(comment) && (
                                    <>
                                      {user.email === comment.autor_email && (
                                        <DropdownMenuItem onClick={() => openEditDialog(comment)}>
                                          <Edit className="mr-2 h-4 w-4" />
                                          Editar
                                        </DropdownMenuItem>
                                      )}
                                      <DropdownMenuItem 
                                        onClick={() => handleDeleteComment(comment.id_comentario, canAdminDelete(comment))}
                                        className="text-red-600"
                                      >
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        Eliminar
                                      </DropdownMenuItem>
                                    </>
                                  )}
                                  {user?.email !== comment.autor_email && (
                                    <DropdownMenuItem 
                                      onClick={() => handleReportComment(comment)}
                                      className="text-orange-600"
                                    >
                                      <Flag className="mr-2 h-4 w-4" />
                                      Reportar Comentario
                                    </DropdownMenuItem>
                                  )}
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">
                              {comment.contenido}
                            </p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>

                    {comments.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-muted-foreground">No hay comentarios aún.</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          ¡Sé el primero en comentar!
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
} 