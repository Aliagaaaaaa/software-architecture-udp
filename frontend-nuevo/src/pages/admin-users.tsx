"use client"

import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { 
  Users, 
  Shield, 
  UserPlus, 
  Trash2, 
  RefreshCw, 
  Search,
  User,
  Calendar,
  Eye,
  UserCheck,
  UserX
} from "lucide-react"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { useAuth } from "@/hooks/useAuth"

type User = {
  email: string
  rol: string
  created_at: string
  updated_at?: string
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

export default function AdminUsers() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)
  const [users, setUsers] = useState<User[]>([])
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  
  // Nuevo usuario
  const [isCreateUserDialogOpen, setIsCreateUserDialogOpen] = useState(false)
  const [newUserEmail, setNewUserEmail] = useState("")
  const [newUserPassword, setNewUserPassword] = useState("")
  const [newUserRole, setNewUserRole] = useState("estudiante")
  
  // Obtener perfil específico
  const [isGetProfileDialogOpen, setIsGetProfileDialogOpen] = useState(false)
  const [profileSearchEmail, setProfileSearchEmail] = useState("")
  const [foundProfile, setFoundProfile] = useState<Profile | null>(null)
  
  const socketRef = useRef<WebSocket | null>(null)

  const loadUsers = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `AUTH_users`
      console.log("📤 Cargando usuarios:", message)
      socketRef.current.send(message)
    }
  }

  const loadProfiles = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFSlist_profiles ${token}`
      console.log("📤 Cargando perfiles:", message)
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
      if (payload.rol !== "moderador") {
        navigate("/forums")
        toast.error("Acceso denegado. Solo moderadores pueden acceder a esta página.")
        return
      }
      
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
      loadUsers()
      loadProfiles()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de lista de usuarios
      const isAuthOk = event.data.includes("AUTH_OK") || event.data.includes("AUTHOK")
      if (isAuthOk) {
        try {
          const authOkPrefix = event.data.includes("AUTH_OK") ? "AUTH_OK" : "AUTHOK"
          const authOkIndex = event.data.indexOf(authOkPrefix)
          const jsonString = event.data.slice(authOkIndex + authOkPrefix.length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.users) {
            setUsers(json.users)
            toast.success(`${json.users.length} usuarios cargados`)
          }
        } catch (err) {
          console.error("Error al parsear usuarios:", err)
        }
      }

      // Respuesta de lista de perfiles
      if (event.data.includes("PROFSOK")) {
        try {
          const profsOkIndex = event.data.indexOf("PROFSOK")
          const jsonString = event.data.slice(profsOkIndex + "PROFSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.profiles) {
            setProfiles(json.profiles)
            toast.success(`${json.profiles.length} perfiles cargados`)
          } else if (json.success && json.profile) {
            // Perfil específico encontrado
            setFoundProfile(json.profile)
            toast.success(`Perfil encontrado para ${json.profile.email}`)
          }
        } catch (err) {
          console.error("Error al parsear perfiles:", err)
        }
      }

      // Respuesta de creación de usuario
      if ((event.data.includes("AUTH_OK") || event.data.includes("AUTHOK")) && event.data.includes("Usuario registrado exitosamente")) {
        try {
          setIsCreateUserDialogOpen(false)
          setNewUserEmail("")
          setNewUserPassword("")
          setNewUserRole("estudiante")
          setLoading(false)
          toast.success("Usuario creado exitosamente")
          loadUsers() // Recargar lista
        } catch (err) {
          console.error("Error al parsear creación de usuario:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de usuario
      if ((event.data.includes("AUTH_OK") || event.data.includes("AUTHOK")) && event.data.includes("eliminado exitosamente")) {
        try {
          setLoading(false)
          toast.success("Usuario eliminado exitosamente")
          loadUsers() // Recargar lista
        } catch (err) {
          console.error("Error al parsear eliminación de usuario:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de perfil
      if (event.data.includes("PROFSOK") && event.data.includes("eliminado exitosamente")) {
        try {
          setLoading(false)
          toast.success("Perfil eliminado exitosamente")
          loadProfiles() // Recargar lista
        } catch (err) {
          console.error("Error al parsear eliminación de perfil:", err)
          setLoading(false)
        }
      }

      if (event.data.includes("AUTH_NK") || event.data.includes("AUTHNK") || event.data.includes("PROFS_NK") || event.data.includes("PROFSNK")) {
        toast.error("Error en la operación")
        setLoading(false)
        setIsCreateUserDialogOpen(false)
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUserEmail.trim() || !newUserPassword.trim()) {
      toast.error("Email y contraseña son requeridos")
      return
    }

    setLoading(true)
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `AUTH_register ${newUserEmail} ${newUserPassword} ${newUserRole}`
      console.log("📤 Creando usuario:", message)
      socketRef.current.send(message)
    }
  }

  const handleDeleteUser = (email: string) => {
    if (confirm(`¿Estás seguro de que quieres eliminar al usuario ${email}? Esta acción no se puede deshacer.`)) {
      setLoading(true)
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `AUTH_delete_user ${email}`
        console.log("📤 Eliminando usuario:", message)
        socketRef.current.send(message)
      }
    }
  }

  const handleDeleteProfile = (email: string) => {
    if (confirm(`¿Estás seguro de que quieres eliminar el perfil de ${email}? Esta acción no se puede deshacer.`)) {
      setLoading(true)
      const token = localStorage.getItem("token")
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const message = `PROFSadmin_delete_profile ${token} ${email}`
        console.log("📤 Eliminando perfil:", message)
        socketRef.current.send(message)
      }
    }
  }

  const handleGetProfile = (e: React.FormEvent) => {
    e.preventDefault()
    if (!profileSearchEmail.trim()) {
      toast.error("Email es requerido")
      return
    }

    setLoading(true)
    setFoundProfile(null)
    const token = localStorage.getItem("token")
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFSadmin_get_profile ${token} ${profileSearchEmail}`
      console.log("📤 Buscando perfil:", message)
      socketRef.current.send(message)
      setLoading(false) // Reset loading state since this is a query
    }
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

  const getUserInitials = (email: string) => {
    return email.charAt(0).toUpperCase()
  }

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const filteredProfiles = profiles.filter(profile =>
    profile.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getUsersWithoutProfile = () => {
    const profileEmails = new Set(profiles.map(p => p.email))
    return users.filter(user => !profileEmails.has(user.email))
  }

  const usersWithoutProfile = getUsersWithoutProfile()

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
                    <Shield className="h-6 w-6" />
                    Administración de Usuarios y Perfiles
                  </h2>
                  <p className="text-muted-foreground">
                    Gestiona usuarios del sistema y sus perfiles
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button 
                    onClick={() => {
                      loadUsers()
                      loadProfiles()
                    }} 
                    disabled={loading}
                    variant="outline"
                  >
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    Actualizar
                  </Button>
                  <Dialog open={isCreateUserDialogOpen} onOpenChange={setIsCreateUserDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <UserPlus className="mr-2 h-4 w-4" />
                        Crear Usuario
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                      <DialogHeader>
                        <DialogTitle>Crear Nuevo Usuario</DialogTitle>
                        <DialogDescription>
                          Crea una nueva cuenta de usuario en el sistema
                        </DialogDescription>
                      </DialogHeader>
                      <form onSubmit={handleCreateUser} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="email">Email *</Label>
                          <Input
                            id="email"
                            type="email"
                            value={newUserEmail}
                            onChange={(e) => setNewUserEmail(e.target.value)}
                            placeholder="usuario@ejemplo.com"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="password">Contraseña *</Label>
                          <Input
                            id="password"
                            type="password"
                            value={newUserPassword}
                            onChange={(e) => setNewUserPassword(e.target.value)}
                            placeholder="Contraseña segura"
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="role">Rol</Label>
                          <select
                            id="role"
                            value={newUserRole}
                            onChange={(e) => setNewUserRole(e.target.value)}
                            className="w-full p-2 border rounded-md"
                          >
                            <option value="estudiante">Estudiante</option>
                            <option value="moderador">Moderador</option>
                          </select>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => setIsCreateUserDialogOpen(false)}
                            disabled={loading}
                          >
                            Cancelar
                          </Button>
                          <Button type="submit" disabled={loading}>
                            {loading ? "Creando..." : "Crear Usuario"}
                          </Button>
                        </div>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              {/* Búsqueda */}
              <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar por email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Dialog open={isGetProfileDialogOpen} onOpenChange={setIsGetProfileDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-2" />
                      Buscar Perfil
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-md">
                    <DialogHeader>
                      <DialogTitle>Buscar Perfil por Email</DialogTitle>
                      <DialogDescription>
                        Busca el perfil específico de un usuario
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleGetProfile} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="profile-email">Email del Usuario</Label>
                        <Input
                          id="profile-email"
                          type="email"
                          value={profileSearchEmail}
                          onChange={(e) => setProfileSearchEmail(e.target.value)}
                          placeholder="usuario@ejemplo.com"
                          required
                        />
                      </div>
                      {foundProfile && (
                        <div className="p-4 border rounded-lg space-y-2">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10">
                              <AvatarImage src={foundProfile.avatar} alt={foundProfile.email} />
                              <AvatarFallback>
                                {getUserInitials(foundProfile.email)}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{foundProfile.email}</p>
                              <p className="text-sm text-muted-foreground">
                                ID: {foundProfile.id_perfil}
                              </p>
                            </div>
                          </div>
                          {foundProfile.biografia && (
                            <p className="text-sm">{foundProfile.biografia}</p>
                          )}
                          <p className="text-xs text-muted-foreground">
                            Creado: {formatDate(foundProfile.created_at)}
                          </p>
                        </div>
                      )}
                      <div className="flex gap-2">
                        <Button 
                          type="button" 
                          variant="outline" 
                          onClick={() => {
                            setIsGetProfileDialogOpen(false)
                            setFoundProfile(null)
                            setProfileSearchEmail("")
                          }}
                        >
                          Cerrar
                        </Button>
                        <Button type="submit" disabled={loading}>
                          {loading ? "Buscando..." : "Buscar"}
                        </Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              <Tabs defaultValue="users" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="users">
                    Usuarios ({filteredUsers.length})
                  </TabsTrigger>
                  <TabsTrigger value="profiles">
                    Perfiles ({filteredProfiles.length})
                  </TabsTrigger>
                  <TabsTrigger value="without-profile">
                    Sin Perfil ({usersWithoutProfile.length})
                  </TabsTrigger>
                  <TabsTrigger value="stats">
                    Estadísticas
                  </TabsTrigger>
                </TabsList>

                {/* Tab de Usuarios */}
                <TabsContent value="users" className="space-y-4">
                  <div className="grid gap-4">
                    {filteredUsers.map((usr) => (
                      <Card key={usr.email} className="border-l-4 border-l-green-500">
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <div className="flex items-center gap-3">
                                <Avatar className="h-10 w-10">
                                  <AvatarFallback>
                                    {getUserInitials(usr.email)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <p className="font-medium">{usr.email}</p>
                                  <div className="flex items-center gap-2">
                                    <Badge variant={usr.rol === 'moderador' ? 'default' : 'secondary'}>
                                      {usr.rol}
                                    </Badge>
                                    <span className="text-sm text-muted-foreground">
                                      <Calendar className="h-3 w-3 inline mr-1" />
                                      {formatDate(usr.created_at)}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteUser(usr.email)}
                              disabled={loading || usr.email === user?.email} // No puede eliminarse a sí mismo
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                {/* Tab de Perfiles */}
                <TabsContent value="profiles" className="space-y-4">
                  <div className="grid gap-4">
                    {filteredProfiles.map((profile) => (
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
                                  <Calendar className="h-3 w-3 inline mr-1" />
                                  Creado: {formatDate(profile.created_at)}
                                </p>
                                {profile.biografia && (
                                  <p className="text-sm leading-relaxed">
                                    {profile.biografia.length > 150 
                                      ? `${profile.biografia.substring(0, 150)}...` 
                                      : profile.biografia
                                    }
                                  </p>
                                )}
                              </div>
                            </div>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteProfile(profile.email)}
                              disabled={loading}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                {/* Tab de Usuarios sin Perfil */}
                <TabsContent value="without-profile" className="space-y-4">
                  <div className="grid gap-4">
                    {usersWithoutProfile.map((usr) => (
                      <Card key={usr.email} className="border-l-4 border-l-orange-500">
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <div className="flex items-center gap-3">
                                <Avatar className="h-10 w-10">
                                  <AvatarFallback>
                                    {getUserInitials(usr.email)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <p className="font-medium">{usr.email}</p>
                                  <div className="flex items-center gap-2">
                                    <Badge variant={usr.rol === 'moderador' ? 'default' : 'secondary'}>
                                      {usr.rol}
                                    </Badge>
                                    <Badge variant="outline" className="text-orange-600">
                                      Sin Perfil
                                    </Badge>
                                    <span className="text-sm text-muted-foreground">
                                      <Calendar className="h-3 w-3 inline mr-1" />
                                      {formatDate(usr.created_at)}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <UserX className="h-5 w-5 text-orange-500" />
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    {usersWithoutProfile.length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        <UserCheck className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>¡Todos los usuarios tienen perfil!</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                {/* Tab de Estadísticas */}
                <TabsContent value="stats" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total de Usuarios
                        </CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{users.length}</div>
                        <p className="text-xs text-muted-foreground">
                          Usuarios registrados en el sistema
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total de Perfiles
                        </CardTitle>
                        <User className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{profiles.length}</div>
                        <p className="text-xs text-muted-foreground">
                          Perfiles creados por usuarios
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Sin Perfil
                        </CardTitle>
                        <UserX className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{usersWithoutProfile.length}</div>
                        <p className="text-xs text-muted-foreground">
                          Usuarios sin perfil creado
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Moderadores
                        </CardTitle>
                        <Shield className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {users.filter(u => u.rol === 'moderador').length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Usuarios con rol de moderador
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Estudiantes
                        </CardTitle>
                        <UserCheck className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {users.filter(u => u.rol === 'estudiante').length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Usuarios con rol de estudiante
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                          Tasa de Perfiles
                        </CardTitle>
                        <User className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {users.length > 0 ? Math.round((profiles.length / users.length) * 100) : 0}%
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Usuarios que han creado perfil
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
} 