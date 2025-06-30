// src/pages/profile.tsx
import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { toast } from "sonner"
import { User, Calendar, MessageSquare, MoreVertical, Edit, Trash2, Eye, Plus, Camera, Save, UserPlus, UserCheck, Users, Shield } from "lucide-react"

type Post = {
  id_post: number
  contenido: string
  fecha: string
  autor_email: string
  id_foro: number
  foro_titulo: string
  created_at: string
  updated_at: string
}

type Profile = {
  id_perfil: number
  avatar?: string
  biografia?: string
  id_usuario: number
  email: string
  created_at: string
  updated_at?: string
}

export function Profile() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [hasProfile, setHasProfile] = useState(false)
  
  // Estados del perfil
  const [avatar, setAvatar] = useState("")
  const [biografia, setBiografia] = useState("")
  const [isEditingProfile, setIsEditingProfile] = useState(false)
  const [isCreatingProfile, setIsCreatingProfile] = useState(false)
  
  // Estados de posts
  const [myPosts, setMyPosts] = useState<Post[]>([])
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  const [editContent, setEditContent] = useState("")
  const [isEditPostDialogOpen, setIsEditPostDialogOpen] = useState(false)
  
  // Estados de administración (para moderadores)
  const [allProfiles, setAllProfiles] = useState<Profile[]>([])
  const [showAdminProfiles, setShowAdminProfiles] = useState(false)
  
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)

  const loadProfile = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFSget_profile ${token}`
      console.log("📤 Cargando perfil:", message)
      socketRef.current.send(message)
    }
  }

  const loadMyPosts = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTSlist_my_posts ${token}`
      console.log("📤 Cargando mis posts:", message)
      socketRef.current.send(message)
    }
  }

  const loadAllProfiles = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN && user?.rol === 'moderador') {
      const message = `PROFSlist_profiles ${token}`
      console.log("📤 Cargando todos los perfiles:", message)
      socketRef.current.send(message)
    }
  }

  useEffect(() => {
  const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      setUser({
        name: payload.name || payload.email,
        email: payload.email,
        avatar: payload.avatar || "",
        rol: payload.rol,
        id_usuario: payload.id_usuario
      })
    } catch (err) {
      console.error("Error parsing token:", err)
      navigate("/login")
      return
    }

    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket

    socket.onopen = () => {
      console.log("🔌 WebSocket conectado")
      loadProfile()
      loadMyPosts()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta del perfil
      if (event.data.includes("PROFSOK")) {
        try {
          const profsOkIndex = event.data.indexOf("PROFSOK")
          const jsonString = event.data.slice(profsOkIndex + "PROFSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.profile) {
            setProfile(json.profile)
            setHasProfile(true)
            setAvatar(json.profile.avatar || "")
            setBiografia(json.profile.biografia || "")
          } else if (json.success && json.profiles) {
            // Lista de todos los perfiles (para moderadores)
            setAllProfiles(json.profiles)
          }
        } catch (err) {
          console.error("Error al parsear perfil:", err)
        }
      }

      // Perfil no encontrado
      if (event.data.includes("PROFSNK") && event.data.includes("No se encontró perfil")) {
        setHasProfile(false)
        setProfile(null)
        setAvatar("")
        setBiografia("")
      }

      // Respuesta de creación de perfil
      if (event.data.includes("PROFSOK") && event.data.includes("creado exitosamente")) {
        try {
          const profsOkIndex = event.data.indexOf("PROFSOK")
          const jsonString = event.data.slice(profsOkIndex + "PROFSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.profile) {
            setProfile(json.profile)
            setHasProfile(true)
            setIsCreatingProfile(false)
            setLoading(false)
            toast.success("Perfil creado exitosamente")
          }
        } catch (err) {
          console.error("Error al parsear creación de perfil:", err)
          setLoading(false)
        }
      }

      // Respuesta de actualización de perfil
      if (event.data.includes("PROFSOK") && event.data.includes("actualizado exitosamente")) {
        try {
          const profsOkIndex = event.data.indexOf("PROFSOK")
          const jsonString = event.data.slice(profsOkIndex + "PROFSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.profile) {
            setProfile(json.profile)
            setAvatar(json.profile.avatar || "")
            setBiografia(json.profile.biografia || "")
            setIsEditingProfile(false)
            setLoading(false)
            toast.success("Perfil actualizado exitosamente")
          }
        } catch (err) {
          console.error("Error al parsear actualización de perfil:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de perfil
      if (event.data.includes("PROFSOK") && event.data.includes("eliminado exitosamente")) {
        try {
          setProfile(null)
          setHasProfile(false)
          setAvatar("")
          setBiografia("")
          setLoading(false)
          toast.success("Perfil eliminado exitosamente")
          if (showAdminProfiles) {
            loadAllProfiles() // Recargar lista si es admin
          }
        } catch (err) {
          console.error("Error al parsear eliminación de perfil:", err)
          setLoading(false)
        }
      }

      // Respuesta de lista de mis posts
      if (event.data.includes("POSTSOK")) {
        try {
          const postsOkIndex = event.data.indexOf("POSTSOK")
          const jsonString = event.data.slice(postsOkIndex + "POSTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.posts) {
            setMyPosts(json.posts)
          }
        } catch (err) {
          console.error("Error al parsear posts:", err)
        }
      }

      // Respuesta de actualización de post
      if (event.data.includes("POSTSOK") && event.data.includes("Post actualizado exitosamente")) {
        try {
          toast.success("Post actualizado exitosamente")
          setIsEditPostDialogOpen(false)
          setEditingPost(null)
          setEditContent("")
          setLoading(false)
          loadMyPosts() // Recargar la lista
        } catch (err) {
          console.error("Error al parsear actualización de post:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de post
      if (event.data.includes("POSTSOK") && event.data.includes("Post eliminado exitosamente")) {
        try {
          toast.success("Post eliminado exitosamente")
          setLoading(false)
          loadMyPosts() // Recargar la lista
        } catch (err) {
          console.error("Error al parsear eliminación de post:", err)
          setLoading(false)
        }
      }

      if (event.data.includes("POSTSNK") || event.data.includes("PROFSNK")) {
        toast.error("Error en la operación")
        setLoading(false)
        setIsCreatingProfile(false)
        setIsEditingProfile(false)
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate, showAdminProfiles])

  // Funciones del perfil
  const handleCreateProfile = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFScreate_profile ${token} "${avatar}" "${biografia}"`
      console.log("📤 Creando perfil:", message)
      socketRef.current.send(message)
    }
  }

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFSupdate_profile ${token} "${avatar}" "${biografia}"`
      console.log("📤 Actualizando perfil:", message)
      socketRef.current.send(message)
    }
  }

  const handleDeleteProfile = () => {
    if (confirm("¿Estás seguro de que quieres eliminar tu perfil? Esta acción no se puede deshacer.")) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `PROFSdelete_profile ${token}`
        console.log("📤 Eliminando perfil:", message)
        socketRef.current.send(message)
      }
    }
  }

  const handleAdminDeleteProfile = (email: string) => {
    if (confirm(`¿Estás seguro de que quieres eliminar el perfil de ${email}? Esta acción no se puede deshacer.`)) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `PROFSadmin_delete_profile ${token} ${email}`
        console.log("📤 Eliminando perfil (admin):", message)
        socketRef.current.send(message)
      }
    }
  }

  // Funciones de posts
  const handleEditPost = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingPost || !editContent.trim()) return

    if (editContent.length > 5000) {
      toast.error("El contenido no puede exceder 5000 caracteres")
      return
    }

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTSupdate_post ${token} ${editingPost.id_post} '${editContent}'`
      console.log("📤 Actualizando post:", message)
      socketRef.current.send(message)
    }
  }

  const handleDeletePost = (postId: number) => {
    if (confirm("¿Estás seguro de que quieres eliminar este post?")) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `POSTSdelete_post ${token} ${postId}`
        console.log("📤 Eliminando post:", message)
        socketRef.current.send(message)
      }
    }
  }

  const openEditPostDialog = (post: Post) => {
    setEditingPost(post)
    setEditContent(post.contenido)
    setIsEditPostDialogOpen(true)
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
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

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + "..."
  }

  const getUserInitials = (email: string) => {
    return email.charAt(0).toUpperCase()
  }

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" user={user} />
      <SidebarInset>
        <SiteHeader />
        <div className="container mx-auto p-6">
          <h1 className="text-2xl font-bold mb-6">Mi Perfil</h1>

          <Tabs defaultValue="profile" className="w-full">
            <TabsList className={`grid w-full ${user?.rol === 'moderador' ? 'grid-cols-4' : 'grid-cols-3'}`}>
              <TabsTrigger value="profile">Perfil</TabsTrigger>
              <TabsTrigger value="info">Información</TabsTrigger>
              <TabsTrigger value="posts">Mis Publicaciones</TabsTrigger>
              {user?.rol === 'moderador' && (
                <TabsTrigger value="admin">Administrar Perfiles</TabsTrigger>
              )}
            </TabsList>

            {/* Tab de Perfil */}
            <TabsContent value="profile" className="space-y-4">
              <Card>
        <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5" />
                      Mi Perfil
                    </CardTitle>
                    {hasProfile && (
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setIsEditingProfile(true)}
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Editar
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={handleDeleteProfile}
                          disabled={loading}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Eliminar
                        </Button>
                      </div>
                    )}
                  </div>
        </CardHeader>
                <CardContent>
                  {hasProfile && profile ? (
                    // Mostrar perfil existente
                    <div className="space-y-6">
                      <div className="flex items-start gap-6">
                        <Avatar className="h-24 w-24">
                          <AvatarImage src={profile.avatar} alt={user?.email} />
                          <AvatarFallback className="text-2xl">
                            {getUserInitials(user?.email || "")}
              </AvatarFallback>
            </Avatar>
                        <div className="flex-1 space-y-2">
                          <h3 className="text-xl font-semibold">{user?.email}</h3>
                          <Badge variant={user?.rol === 'moderador' ? 'default' : 'secondary'}>
                            {user?.rol}
                          </Badge>
                          <p className="text-sm text-muted-foreground">
                            Perfil creado: {formatDate(profile.created_at)}
                          </p>
                          {profile.updated_at && profile.updated_at !== profile.created_at && (
                            <p className="text-sm text-muted-foreground">
                              Última actualización: {formatDate(profile.updated_at)}
                            </p>
                          )}
            </div>
          </div>

                      {profile.biografia && (
            <div>
                          <Label className="text-sm font-medium">Biografía</Label>
                          <p className="mt-1 text-sm leading-relaxed whitespace-pre-wrap">
                            {profile.biografia}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    // No tiene perfil - mostrar opción de crear
                    <div className="text-center py-8">
                      <User className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">¡Crea tu perfil!</h3>
                      <p className="text-muted-foreground mb-6">
                        Personaliza tu perfil con un avatar y una biografía para que otros usuarios puedan conocerte mejor.
                      </p>
                      <Button onClick={() => setIsCreatingProfile(true)}>
                        <UserPlus className="h-4 w-4 mr-2" />
                        Crear Perfil
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Dialog para crear perfil */}
              <Dialog open={isCreatingProfile} onOpenChange={setIsCreatingProfile}>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Crear Tu Perfil</DialogTitle>
                    <DialogDescription>
                      Personaliza tu perfil con un avatar y una biografía
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateProfile} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="avatar">URL del Avatar (opcional)</Label>
                      <Input
                        id="avatar"
                        type="url"
                        value={avatar}
                        onChange={(e) => setAvatar(e.target.value)}
                        placeholder="https://ejemplo.com/mi-avatar.jpg"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="biografia">Biografía (opcional)</Label>
                      <Textarea
                        id="biografia"
                        value={biografia}
                        onChange={(e) => setBiografia(e.target.value)}
                        placeholder="Cuéntanos un poco sobre ti..."
                        rows={4}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setIsCreatingProfile(false)}
                        disabled={loading}
                      >
                        Cancelar
                      </Button>
                      <Button type="submit" disabled={loading}>
                        {loading ? "Creando..." : "Crear Perfil"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>

              {/* Dialog para editar perfil */}
              <Dialog open={isEditingProfile} onOpenChange={setIsEditingProfile}>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Editar Perfil</DialogTitle>
                    <DialogDescription>
                      Actualiza tu avatar y biografía
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="edit-avatar">URL del Avatar</Label>
                      <Input
                        id="edit-avatar"
                        type="url"
                        value={avatar}
                        onChange={(e) => setAvatar(e.target.value)}
                        placeholder="https://ejemplo.com/mi-avatar.jpg"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-biografia">Biografía</Label>
                      <Textarea
                        id="edit-biografia"
                        value={biografia}
                        onChange={(e) => setBiografia(e.target.value)}
                        placeholder="Cuéntanos un poco sobre ti..."
                        rows={4}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setIsEditingProfile(false)}
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
            </TabsContent>

            {/* Tab de Información Personal */}
            <TabsContent value="info" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Información Personal
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input 
                      value={user?.email || ""} 
                      readOnly
                      className="bg-muted"
                    />
            </div>
                  <div className="space-y-2">
              <Label>Rol</Label>
                    <div className="flex items-center gap-2">
                      <Badge variant={user?.rol === 'moderador' ? 'default' : 'secondary'}>
                        {user?.rol}
                      </Badge>
            </div>
          </div>
                  {user?.id_usuario && (
                    <div className="space-y-2">
                      <Label>ID de Usuario</Label>
                      <Input 
                        value={user.id_usuario} 
                        readOnly
                        className="bg-muted"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tab de Mis Publicaciones */}
            <TabsContent value="posts" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5" />
                      Mis Publicaciones ({myPosts.length})
                    </CardTitle>
                    <Button onClick={() => navigate("/crear-publicacion")} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Nueva Publicación
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {myPosts.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Aún no has creado ninguna publicación</p>
                      <Button onClick={() => navigate("/crear-publicacion")} className="mt-4">
                        Crear tu primera publicación
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {myPosts.map((post) => (
                        <Card key={post.id_post} className="border-l-4 border-l-primary">
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="outline">{post.foro_titulo}</Badge>
                                  <span className="text-sm text-muted-foreground flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {formatDate(post.fecha)}
                                  </span>
                                  {post.updated_at !== post.created_at && (
                                    <Badge variant="secondary" className="text-xs">
                                      Editado
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-sm">{truncateContent(post.contenido)}</p>
                              </div>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem onClick={() => navigate(`/post/${post.id_post}`)}>
                                    <Eye className="h-4 w-4 mr-2" />
                                    Ver Completo
                                  </DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => navigate(`/forum/${post.id_foro}`)}>
                                    <MessageSquare className="h-4 w-4 mr-2" />
                                    Ver Foro
                                  </DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => openEditPostDialog(post)}>
                                    <Edit className="h-4 w-4 mr-2" />
                                    Editar
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    onClick={() => handleDeletePost(post.id_post)}
                                    className="text-destructive"
                                  >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Eliminar
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tab de Administración (solo moderadores) */}
            {user?.rol === 'moderador' && (
              <TabsContent value="admin" className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Administrar Perfiles ({allProfiles.length})
                      </CardTitle>
                      <Button 
                        onClick={() => {
                          setShowAdminProfiles(true)
                          loadAllProfiles()
                        }} 
                        size="sm"
                        disabled={loading}
                      >
                        <Users className="h-4 w-4 mr-2" />
                        Cargar Perfiles
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {allProfiles.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No hay perfiles cargados</p>
                        <p className="text-sm">Haz clic en "Cargar Perfiles" para ver todos los perfiles del sistema</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {allProfiles.map((profile) => (
                          <Card key={profile.id_perfil} className="border-l-4 border-l-blue-500">
                            <CardContent className="pt-4">
                              <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4 flex-1">
                                  <Avatar className="h-12 w-12">
                                    <AvatarImage src={profile.avatar} alt={profile.email} />
                                    <AvatarFallback>
                                      {getUserInitials(profile.email)}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <h4 className="font-medium">{profile.email}</h4>
                                      <Badge variant="outline" className="text-xs">
                                        ID: {profile.id_perfil}
                                      </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground mb-2">
                                      Creado: {formatDate(profile.created_at)}
                                    </p>
                                    {profile.biografia && (
                                      <p className="text-sm">{truncateContent(profile.biografia, 100)}</p>
                                    )}
                                  </div>
                                </div>
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => handleAdminDeleteProfile(profile.email)}
                                  disabled={loading}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
          </div>
        </CardContent>
      </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>

          {/* Dialog para editar post */}
          <Dialog open={isEditPostDialogOpen} onOpenChange={setIsEditPostDialogOpen}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Editar Publicación</DialogTitle>
                <DialogDescription>
                  Modifica el contenido de tu publicación en el foro "{editingPost?.foro_titulo}"
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleEditPost} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-content">Contenido</Label>
                  <Textarea
                    id="edit-content"
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={8}
                    placeholder="Contenido de la publicación..."
                    required
                  />
                  <div className="text-sm text-muted-foreground text-right">
                    {editContent.length}/5000 caracteres
                  </div>
                </div>
                <div className="flex gap-2">
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
    </div>
      </SidebarInset>
    </SidebarProvider>
  )
}