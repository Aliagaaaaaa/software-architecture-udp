import { useState, useCallback, useEffect, useRef } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { toast } from "sonner"
import { useNavigate } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

type Forum = {
  id_foro: number
  titulo: string
  descripcion: string
  categoria: string
  fecha_creacion: string
  autor_email: string
}

export function CrearPublicacion() {
  const navigate = useNavigate()
  const [selectedForumId, setSelectedForumId] = useState<string>("")
  const [content, setContent] = useState("")
  const [forums, setForums] = useState<Forum[]>([])
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<any>(null)
  const socketRef = useRef<WebSocket | null>(null)

  // Cargar lista de foros disponibles
  const loadForums = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `FORUMlist_forums ${token}`
      console.log("📤 Cargando foros:", message)
      socketRef.current.send(message)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    // Parse user info from token
    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      setUser({
        name: payload.name || payload.email,
        email: payload.email,
        avatar: payload.avatar || "",
        rol: payload.rol
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
      loadForums()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de lista de foros
      if (event.data.includes("FORUMOK")) {
        try {
          const forumOkIndex = event.data.indexOf("FORUMOK")
          const jsonString = event.data.slice(forumOkIndex + "FORUMOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.forums) {
            setForums(json.forums)
          }
        } catch (err) {
          console.error("Error al parsear foros:", err)
        }
      }
      
      // Respuesta de creación de post
      if (event.data.includes("POSTSOK") && event.data.includes("creado exitosamente")) {
        try {
          const postsOkIndex = event.data.indexOf("POSTSOK")
          const jsonString = event.data.slice(postsOkIndex + "POSTSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success) {
            toast.success("¡Post creado exitosamente!")
            setLoading(false)
            // Navegar al foro donde se creó el post
            setTimeout(() => navigate(`/forum/${selectedForumId}`), 1000)
          }
        } catch (err) {
          console.error("Error al parsear respuesta de creación:", err)
          setLoading(false)
        }
      } else if (event.data.includes("POSTSNK")) {
        toast.error("Error al crear el post")
        setLoading(false)
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate, selectedForumId])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedForumId) {
      toast.error("Debes seleccionar un foro")
      return
    }

    if (!content.trim()) {
      toast.error("El contenido no puede estar vacío")
      return
    }

    if (content.length > 5000) {
      toast.error("El contenido no puede exceder 5000 caracteres")
      return
    }

    setLoading(true)
    const token = localStorage.getItem("token")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `POSTScreate_post ${token} ${selectedForumId} '${content}'`
      console.log("📤 Creando post:", message)
      socketRef.current.send(message)
    } else {
      
      setLoading(false)
    }
  }

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" user={user} />
      <SidebarInset>
        <SiteHeader />
        <div className="container mx-auto p-6">
          <div className="flex items-center gap-4 mb-6">
            <Button 
              variant="outline" 
              size="icon"
              onClick={() => navigate("/forums")}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-2xl font-bold">Crear Nueva Publicación</h1>
          </div>

          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Nueva Publicación</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="forum">Foro *</Label>
                  <Select value={selectedForumId} onValueChange={setSelectedForumId} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona un foro" />
                    </SelectTrigger>
                    <SelectContent>
                      {forums.map((forum) => (
                        <SelectItem key={forum.id_foro} value={forum.id_foro.toString()}>
                          <div>
                            <div className="font-medium">{forum.titulo}</div>
                            <div className="text-sm text-muted-foreground">{forum.descripcion}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content">Contenido *</Label>
                  <Textarea
                    id="content"
                    placeholder="Escribe el contenido de tu publicación..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    rows={8}
                    required
                  />
                  <div className="text-sm text-muted-foreground text-right">
                    {content.length}/5000 caracteres
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => navigate("/forums")}
                  >
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={loading}>
                    {loading ? "Creando..." : "Crear Publicación"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}