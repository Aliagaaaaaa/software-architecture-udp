"use client"

import { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Plus, MessageSquare, Users, MoreVertical, Edit, Trash2 } from "lucide-react"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Foro = {
  id_foro: number
  titulo: string
  categoria: string
  creador_email: string
  created_at: string
  creador_id?: number
}

export default function Forums() {
  const [allForos, setAllForos] = useState<Foro[]>([])
  const [myForos, setMyForos] = useState<Foro[]>([])
  const [user, setUser] = useState<any>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingForum, setEditingForum] = useState<Foro | null>(null)
  const [newForumTitle, setNewForumTitle] = useState("")
  const [newForumCategory, setNewForumCategory] = useState("")
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("all")
  const socketRef = useRef<WebSocket | null>(null)
  const navigate = useNavigate()

  const loadAllForums = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMlist_forums ${token}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }
  }

  const loadMyForums = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMlist_my_forums ${token}`
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
      loadAllForums()
      loadMyForums()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de listar todos los foros
      if (event.data.includes("FORUMOK") && event.data.includes("Se encontraron")) {
        try {
          const forumOkIndex = event.data.indexOf("FORUMOK")
          const jsonString = event.data.slice(forumOkIndex + "FORUMOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.forums) {
            setAllForos(json.forums)
          }
        } catch (err) {
          console.error("Error al parsear foros:", err)
          toast.error("Error cargando foros")
        }
      }
      
      // Respuesta de listar mis foros
      if (event.data.includes("FORUMOK") && event.data.includes("Tienes")) {
        try {
          const forumOkIndex = event.data.indexOf("FORUMOK")
          const jsonString = event.data.slice(forumOkIndex + "FORUMOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.forums) {
            setMyForos(json.forums)
          }
        } catch (err) {
          console.error("Error al parsear mis foros:", err)
          toast.error("Error cargando tus foros")
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  const handleCreateForum = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newForumTitle.trim() || !newForumCategory.trim()) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMcreate_forum ${token} '${newForumTitle}' '${newForumCategory}'`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de creación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("FORUMOK") && event.data.includes("creado exitosamente")) {
          setIsCreateDialogOpen(false)
          setNewForumTitle("")
          setNewForumCategory("")
          setLoading(false)
          loadAllForums()
          loadMyForums()
          toast.success("Foro creado exitosamente")
        } else if (event.data.includes("FORUMNK")) {
          setLoading(false)
          console.error("Error creando foro")
          toast.error("Error al crear el foro")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleEditForum = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingForum || !newForumTitle.trim() || !newForumCategory.trim()) return

    setLoading(true)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMupdate_forum ${token} ${editingForum.id_foro} '${newForumTitle}' '${newForumCategory}'`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de actualización
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("FORUMOK") && event.data.includes("actualizado exitosamente")) {
          setIsEditDialogOpen(false)
          setEditingForum(null)
          setNewForumTitle("")
          setNewForumCategory("")
          setLoading(false)
          loadAllForums()
          loadMyForums()
          toast.success("Foro actualizado exitosamente")
        } else if (event.data.includes("FORUMNK")) {
          setLoading(false)
          console.error("Error actualizando foro")
          toast.error("Error al actualizar el foro")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleDeleteForum = (forumId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este foro?")) return

    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMdelete_forum ${token} ${forumId}`
      console.log("📤 Enviando mensaje:", message)
      socketRef.current.send(message)
    }

    // Escuchar respuesta de eliminación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("FORUMOK") && event.data.includes("eliminado exitosamente")) {
          loadAllForums()
          loadMyForums()
          toast.success("Foro eliminado exitosamente")
        } else if (event.data.includes("FORUMNK")) {
          console.error("Error eliminando foro")
          toast.error("Error al eliminar el foro")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const openEditDialog = (forum: Foro) => {
    setEditingForum(forum)
    setNewForumTitle(forum.titulo)
    setNewForumCategory(forum.categoria)
    setIsEditDialogOpen(true)
  }

  const handleForumClick = (forumId: number) => {
    navigate(`/forum/${forumId}`)
  }

  const canEditOrDelete = (forum: Foro) => {
    return user && (user.email === forum.creador_email || user.rol === "moderador")
  }

  const ForumCard = ({ foro }: { foro: Foro }) => (
    <Card className="cursor-pointer hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1" onClick={() => handleForumClick(foro.id_foro)}>
            <CardTitle className="text-lg">{foro.titulo}</CardTitle>
            <CardDescription>
              <span className="inline-flex items-center gap-1">
                <Users className="h-3 w-3" />
                {foro.categoria}
              </span>
            </CardDescription>
          </div>
          {canEditOrDelete(foro) && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => openEditDialog(foro)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Editar
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => handleDeleteForum(foro.id_foro)}
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
      <CardContent onClick={() => handleForumClick(foro.id_foro)}>
        <div className="text-sm text-muted-foreground">
          <p>Creado por: {foro.creador_email}</p>
          <p>Fecha: {new Date(foro.created_at).toLocaleDateString()}</p>
        </div>
        <div className="mt-2 flex items-center text-sm text-muted-foreground">
          <MessageSquare className="mr-1 h-3 w-3" />
          Ver posts
        </div>
      </CardContent>
    </Card>
  )

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
                <h2 className="text-2xl font-semibold">Foros</h2>
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Foro
                </Button>
              </div>

              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                  <TabsTrigger value="all">Todos los Foros</TabsTrigger>
                  <TabsTrigger value="my">Mis Foros</TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="mt-4">
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {allForos.map((foro) => (
                      <ForumCard key={foro.id_foro} foro={foro} />
                    ))}
                  </div>
                  {allForos.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No hay foros disponibles.</p>
                </div>
                  )}
                </TabsContent>

                <TabsContent value="my" className="mt-4">
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {myForos.map((foro) => (
                      <ForumCard key={foro.id_foro} foro={foro} />
                    ))}
                  </div>
                  {myForos.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No has creado ningún foro aún.</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        ¡Crea tu primer foro!
                      </p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>

              {/* Dialog para crear foro */}
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Crear Nuevo Foro</DialogTitle>
                    <DialogDescription>
                      Crea un nuevo foro de discusión para la comunidad.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateForum} className="space-y-4">
                    <div>
                      <Label htmlFor="title">Título del Foro</Label>
                      <Input
                        id="title"
                        value={newForumTitle}
                        onChange={(e) => setNewForumTitle(e.target.value)}
                        placeholder="Ej: Discusión General"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Categoría</Label>
                      <Input
                        id="category"
                        value={newForumCategory}
                        onChange={(e) => setNewForumCategory(e.target.value)}
                        placeholder="Ej: Académico, Social, Tecnología"
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
                        {loading ? "Creando..." : "Crear Foro"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>

              {/* Dialog para editar foro */}
              <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Editar Foro</DialogTitle>
                    <DialogDescription>
                      Modifica el título y categoría del foro.
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleEditForum} className="space-y-4">
                    <div>
                      <Label htmlFor="edit-title">Título del Foro</Label>
                      <Input
                        id="edit-title"
                        value={newForumTitle}
                        onChange={(e) => setNewForumTitle(e.target.value)}
                        placeholder="Ej: Discusión General"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit-category">Categoría</Label>
                      <Input
                        id="edit-category"
                        value={newForumCategory}
                        onChange={(e) => setNewForumCategory(e.target.value)}
                        placeholder="Ej: Académico, Social, Tecnología"
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
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}