"use client"

import { useState, useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { toast } from "sonner"
import { AlertTriangle, FileText, MessageSquare, Plus, Eye, Edit, Trash2, MoreVertical, Shield, Clock, CheckCircle, XCircle, Users } from "lucide-react"
import { RAZONES_REPORTE } from "@/lib/constants"

type Report = {
  id_reporte: number
  contenido_id: number
  tipo_contenido: string
  razon: string
  fecha: string
  reportado_por: number
  estado: string
  revisado_por?: number
  fecha_revision?: string
  reportado_por_email?: string
  revisado_por_email?: string
}

export function CrearReporte() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)

  // Estados para crear reporte
  const [contenidoId, setContenidoId] = useState("")
  const [tipoContenido, setTipoContenido] = useState("")
  const [razonSeleccionada, setRazonSeleccionada] = useState("")

  // Estados para listar reportes
  const [myReports, setMyReports] = useState<Report[]>([])
  const [allReports, setAllReports] = useState<Report[]>([])
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [newStatus, setNewStatus] = useState("")

  // Estados para asignación de tareas
  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false)
  const [assignTarget, setAssignTarget] = useState<Report | null>(null)
  const [moderators, setModerators] = useState<Array<{email: string, name: string}>>([])
  const [selectedModerator, setSelectedModerator] = useState("")
  const [assignComment, setAssignComment] = useState("")
  const [assignLoading, setAssignLoading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    let userPayload: any
    try {
      userPayload = JSON.parse(atob(token.split(".")[1]))
      setUser({
        name: userPayload.name || userPayload.email,
        email: userPayload.email,
        avatar: userPayload.avatar || "",
        rol: userPayload.rol,
        id_usuario: userPayload.id_usuario
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
      loadMyReports()
      if (userPayload.rol === 'moderador') {
        loadAllReports()
      }
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de creación de reporte
      if (event.data.includes("reprtOK") && event.data.includes("creado exitosamente")) {
        try {
          const reprtOkIndex = event.data.indexOf("reprtOK")
          const jsonString = event.data.slice(reprtOkIndex + "reprtOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.report && json.report.id_reporte) {
            // Crear notificación de reporte para moderadores
            const token = localStorage.getItem("token")
            const razonFinal = RAZONES_REPORTE.find(r => r.value === razonSeleccionada)?.label || razonSeleccionada
            const notificationMessage = `NOTIFcreate_report_notification ${token} ${json.report.id_reporte} '${razonFinal}' '${tipoContenido}'`
            console.log("📤 Enviando notificación de reporte:", notificationMessage)
            if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
              socketRef.current.send(notificationMessage)
            }
            
            toast.success("Reporte creado exitosamente")
            setContenidoId("")
            setTipoContenido("")
            setRazonSeleccionada("")
            setLoading(false)
            loadMyReports()
          }
        } catch (err) {
          console.error("Error al parsear creación de reporte:", err)
          setLoading(false)
        }
      }

      // Respuesta de lista de mis reportes
      if (event.data.includes("reprtOK") && event.data.includes("Tienes")) {
        try {
          const reprtOkIndex = event.data.indexOf("reprtOK")
          const jsonString = event.data.slice(reprtOkIndex + "reprtOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.reports) {
            setMyReports(json.reports)
          }
        } catch (err) {
          console.error("Error al parsear mis reportes:", err)
        }
      }

      // Respuesta de lista de todos los reportes (admin)
      if (event.data.includes("reprtOK") && event.data.includes("Se encontraron")) {
        try {
          const reprtOkIndex = event.data.indexOf("reprtOK")
          const jsonString = event.data.slice(reprtOkIndex + "reprtOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.reports) {
            setAllReports(json.reports)
          }
        } catch (err) {
          console.error("Error al parsear todos los reportes:", err)
        }
      }

      // Respuesta de actualización de estado
      if (event.data.includes("reprtOK") && event.data.includes("actualizado exitosamente")) {
        try {
          toast.success("Estado del reporte actualizado")
          setLoading(false)
          setSelectedReport(null)
          setNewStatus("")
          loadAllReports()
        } catch (err) {
          console.error("Error al parsear actualización de estado:", err)
          setLoading(false)
        }
      }

      // Respuesta de eliminación de reporte
      if (event.data.includes("reprtOK") && event.data.includes("eliminado exitosamente")) {
        try {
          toast.success("Reporte eliminado exitosamente")
          setLoading(false)
          loadMyReports()
          if (user?.rol === 'moderador') {
            loadAllReports()
          }
        } catch (err) {
          console.error("Error al parsear eliminación de reporte:", err)
          setLoading(false)
        }
      }

      // Respuesta de lista de moderadores
      if (event.data.includes("PROFSOK") && event.data.includes("moderadores")) {
        try {
          const profsOkIndex = event.data.indexOf("PROFSOK")
          const jsonString = event.data.slice(profsOkIndex + "PROFSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.moderators) {
            setModerators(json.moderators)
          }
        } catch (err) {
          console.error("Error al parsear moderadores:", err)
        }
      }

      // Respuesta de asignación de tarea
      if (event.data.includes("reprtOK") && event.data.includes("Tarea de moderación asignada exitosamente")) {
        try {
          toast.success("Tarea de moderación asignada exitosamente")
          setAssignLoading(false)
          loadAllReports() // Recargar reportes
        } catch (err) {
          console.error("Error al parsear asignación de tarea:", err)
          setAssignLoading(false)
        }
      }

      if (event.data.includes("reprtNK")) {
        toast.error("Error en la operación")
        setLoading(false)
        setAssignLoading(false)
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  const loadMyReports = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtlist_my_reports ${token}`
      console.log("📤 Cargando mis reportes:", message)
      socketRef.current.send(message)
    }
  }

  const loadAllReports = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtlist_reports ${token}`
      console.log("📤 Cargando todos los reportes:", message)
      socketRef.current.send(message)
    }
  }

  const loadModerators = () => {
    const token = localStorage.getItem("token")
    if (token && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `PROFSlist_moderators ${token}`
      console.log("📤 Cargando lista de moderadores:", message)
      socketRef.current.send(message)
    }
  }

  const handleCreateReport = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!contenidoId.trim() || !tipoContenido || !razonSeleccionada.trim()) {
      toast.error("Todos los campos son obligatorios")
      return
    }

    // Obtener la razón seleccionada
    const razonFinal = RAZONES_REPORTE.find(r => r.value === razonSeleccionada)?.label || razonSeleccionada

    setLoading(true)
    const token = localStorage.getItem("token")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtcreate_report ${token} ${contenidoId} ${tipoContenido} '${razonFinal}'`
      console.log("📤 Creando reporte:", message)
      socketRef.current.send(message)
    } else {
      
      setLoading(false)
    }
  }

  const handleUpdateStatus = (report: Report, status: string) => {
    setLoading(true)
    const token = localStorage.getItem("token")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = `reprtupdate_report_status ${token} ${report.id_reporte} ${status}`
      console.log("📤 Actualizando estado:", message)
      socketRef.current.send(message)
    } else {
      
      setLoading(false)
    }
  }

  const handleDeleteReport = (reportId: number, isAdmin: boolean = false) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este reporte?")) return

    setLoading(true)
    const token = localStorage.getItem("token")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const method = isAdmin ? "admin_delete_report" : "delete_report"
      const message = `reprt${method} ${token} ${reportId}`
      console.log("📤 Eliminando reporte:", message)
      socketRef.current.send(message)
    } else {
      
      setLoading(false)
    }
  }

  const openAssignDialog = (report: Report) => {
    setAssignTarget(report)
    setSelectedModerator("")
    setAssignComment("")
    setIsAssignDialogOpen(true)
    loadModerators()
  }

  const handleAssignTask = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedModerator.trim() || !assignTarget) {
      toast.error("Por favor selecciona un moderador")
      return
    }

    if (assignComment.length > 500) {
      toast.error("El comentario no puede exceder 500 caracteres")
      return
    }

    setAssignLoading(true)
    const token = localStorage.getItem("token")
    
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const comment = assignComment.trim() || "Sin comentarios adicionales"
      const message = `reprtassign_moderation_task ${token} ${assignTarget.id_reporte} '${selectedModerator}' '${comment}'`
      console.log("📤 Asignando tarea de moderación:", message)
      socketRef.current.send(message)
      
      // Enviar notificación al moderador asignado
      const notificationMessage = `NOTIFassign_moderation_task_notification ${token} '${selectedModerator}' ${assignTarget.id_reporte} '${assignTarget.tipo_contenido}' ${assignTarget.contenido_id} '${comment}'`
      console.log("📤 Enviando notificación de asignación:", notificationMessage)
      socketRef.current.send(notificationMessage)
      
      setIsAssignDialogOpen(false)
      setSelectedModerator("")
      setAssignComment("")
      setAssignTarget(null)
    } else {
      
      setAssignLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'pendiente': { variant: 'secondary' as const, icon: Clock, text: 'Pendiente' },
      'revisado': { variant: 'default' as const, icon: Eye, text: 'Revisado' },
      'resuelto': { variant: 'default' as const, icon: CheckCircle, text: 'Resuelto' },
      'descartado': { variant: 'destructive' as const, icon: XCircle, text: 'Descartado' }
    }
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendiente
    const Icon = config.icon
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <AlertTriangle className="h-8 w-8 text-red-500" />
              Gestión de Reportes
            </h1>
          </div>

          <Tabs defaultValue="create" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="create">Crear Reporte</TabsTrigger>
              <TabsTrigger value="my-reports">Mis Reportes</TabsTrigger>
              {user?.rol === 'moderador' && (
                <TabsTrigger value="all-reports">Todos los Reportes</TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="create" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    Crear Nuevo Reporte
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreateReport} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="contenido-id">ID del Contenido *</Label>
                        <Input
                          id="contenido-id"
                          type="number"
                          value={contenidoId}
                          onChange={(e) => setContenidoId(e.target.value)}
                          placeholder="Ej: 123"
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="tipo-contenido">Tipo de Contenido *</Label>
                        <Select value={tipoContenido} onValueChange={setTipoContenido} required>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecciona el tipo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="post">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Publicación
                              </div>
                            </SelectItem>
                            <SelectItem value="comentario">
                              <div className="flex items-center gap-2">
                                <MessageSquare className="h-4 w-4" />
                                Comentario
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="razon">Razón del Reporte *</Label>
                      <Select value={razonSeleccionada} onValueChange={setRazonSeleccionada} required>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecciona una razón" />
                        </SelectTrigger>
                        <SelectContent>
                          {RAZONES_REPORTE.map((razon) => (
                            <SelectItem key={razon.value} value={razon.value}>
                              {razon.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>



                    <Button type="submit" disabled={loading} className="w-full">
                      {loading ? "Creando Reporte..." : "Crear Reporte"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tab para mis reportes */}
            <TabsContent value="my-reports" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Mis Reportes ({myReports.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {myReports.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No has creado ningún reporte</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {myReports.map((report) => (
                        <Card key={report.id_reporte} className="border-l-4 border-l-orange-500">
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="outline">
                                    {report.tipo_contenido === 'post' ? 'Publicación' : 'Comentario'} #{report.contenido_id}
                                  </Badge>
                                  {getStatusBadge(report.estado)}
                                  <span className="text-sm text-muted-foreground">
                                    {formatDate(report.fecha)}
                                  </span>
                                </div>
                                <p className="text-sm mb-2">{report.razon}</p>
                                {report.fecha_revision && (
                                  <p className="text-xs text-muted-foreground">
                                    Revisado el {formatDate(report.fecha_revision)}
                                  </p>
                                )}
                              </div>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem 
                                    onClick={() => handleDeleteReport(report.id_reporte)}
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

            {/* Tab para todos los reportes (solo moderadores) */}
            {user?.rol === 'moderador' && (
              <TabsContent value="all-reports" className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Todos los Reportes ({allReports.length})
                      </CardTitle>
                      <Button onClick={loadAllReports} size="sm" disabled={loading}>
                        Actualizar
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {allReports.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No hay reportes en el sistema</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {allReports.map((report) => (
                          <Card key={report.id_reporte} className="border-l-4 border-l-blue-500">
                            <CardContent className="pt-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Badge variant="outline">
                                      {report.tipo_contenido === 'post' ? 'Publicación' : 'Comentario'} #{report.contenido_id}
                                    </Badge>
                                    {getStatusBadge(report.estado)}
                                    <span className="text-sm text-muted-foreground">
                                      {formatDate(report.fecha)}
                                    </span>
                                  </div>
                                  <p className="text-sm mb-2">{report.razon}</p>
                                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                    <span>Reportado por: {report.reportado_por_email || `ID: ${report.reportado_por}`}</span>
                                    {report.revisado_por && (
                                      <span>Revisado por: {report.revisado_por_email || `ID: ${report.revisado_por}`}</span>
                                    )}
                                  </div>
                                </div>
                                <div className="flex gap-2">
                                  {report.estado === 'pendiente' && (
                                    <>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => openAssignDialog(report)}
                                        disabled={loading}
                                      >
                                        <Users className="h-4 w-4 mr-1" />
                                        Asignar
                                      </Button>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => handleUpdateStatus(report, 'revisado')}
                                        disabled={loading}
                                      >
                                        Marcar Revisado
                                      </Button>
                                      <Button
                                        variant="default"
                                        size="sm"
                                        onClick={() => handleUpdateStatus(report, 'resuelto')}
                                        disabled={loading}
                                      >
                                        Resolver
                                      </Button>
                                      <Button
                                        variant="destructive"
                                        size="sm"
                                        onClick={() => handleUpdateStatus(report, 'descartado')}
                                        disabled={loading}
                                      >
                                        Descartar
                                      </Button>
                                    </>
                                  )}
                                  <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                      <Button variant="ghost" size="sm">
                                        <MoreVertical className="h-4 w-4" />
                                      </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                      <DropdownMenuItem 
                                        onClick={() => handleDeleteReport(report.id_reporte, true)}
                                        className="text-destructive"
                                      >
                                        <Trash2 className="h-4 w-4 mr-2" />
                                        Eliminar (Admin)
                                      </DropdownMenuItem>
                                    </DropdownMenuContent>
                                  </DropdownMenu>
                                </div>
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
        </div>
      </SidebarInset>

      {/* Modal para asignar tarea de moderación */}
      <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Asignar Tarea de Moderación
            </DialogTitle>
            <DialogDescription>
              Asigna este reporte a otro moderador para su revisión. El moderador recibirá una notificación automática.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleAssignTask}>
            <div className="space-y-4">
              {/* Información del reporte */}
              {assignTarget && (
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline">
                      {assignTarget.tipo_contenido === 'post' ? 'Publicación' : 'Comentario'} #{assignTarget.contenido_id}
                    </Badge>
                    <Badge variant="destructive">Pendiente</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{assignTarget.razon}</p>
                  <p className="text-xs text-muted-foreground">
                    Reportado el {formatDate(assignTarget.fecha)} por {assignTarget.reportado_por_email || `ID: ${assignTarget.reportado_por}`}
                  </p>
                </div>
              )}

              {/* Selector de moderador */}
              <div className="space-y-2">
                <Label htmlFor="moderator">Asignar a Moderador *</Label>
                <Select value={selectedModerator} onValueChange={setSelectedModerator} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona un moderador" />
                  </SelectTrigger>
                  <SelectContent>
                    {moderators.map((moderator) => (
                      <SelectItem key={moderator.email} value={moderator.email}>
                        {moderator.name} ({moderator.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Comentario opcional */}
              <div className="space-y-2">
                <Label htmlFor="comment">Comentario Adicional (Opcional)</Label>
                <Textarea
                  id="comment"
                  placeholder="Agrega instrucciones específicas o contexto para el moderador asignado..."
                  value={assignComment}
                  onChange={(e) => setAssignComment(e.target.value)}
                  rows={3}
                  maxLength={500}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Opcional - Máximo 500 caracteres</span>
                  <span>{assignComment.length}/500</span>
                </div>
              </div>

              {/* Información adicional */}
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Nota:</strong> El moderador asignado recibirá una notificación automática con los detalles de la tarea y tu comentario.
                </p>
              </div>
            </div>

            <DialogFooter className="mt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsAssignDialogOpen(false)}
                disabled={assignLoading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                disabled={assignLoading || !selectedModerator.trim()}
              >
                {assignLoading ? "Asignando..." : "Asignar Tarea"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </SidebarProvider>
  )
}
