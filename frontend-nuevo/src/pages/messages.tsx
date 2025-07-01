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
import { Plus, MessageSquare, Send, Inbox, User, Calendar, MoreVertical, Edit, Trash2, MessageCircle, ArrowRight, Users2, Eye } from "lucide-react"
import { toast } from "sonner"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { buildServiceMessage } from "@/lib/utils"

type Message = {
  id_mensaje: number
  contenido: string
  fecha: string
  emisor_email: string
  receptor_email: string
  emisor_id?: number
  receptor_id?: number
  is_sent?: boolean
}

type Comment = {
  id_comentario: number
  contenido: string
  fecha: string
  autor_email: string
  id_post: number
  post_preview: string
}

type Conversation = {
  other_user: string
  messages: Message[]
  last_message_date: string
}

export default function Messages() {
  const [user, setUser] = useState<any>(null)
  const [sentMessages, setSentMessages] = useState<Message[]>([])
  const [receivedMessages, setReceivedMessages] = useState<Message[]>([])
  const [myComments, setMyComments] = useState<Comment[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [conversationMessages, setConversationMessages] = useState<Message[]>([])
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditCommentDialogOpen, setIsEditCommentDialogOpen] = useState(false)
  const [isConversationDialogOpen, setIsConversationDialogOpen] = useState(false)
  const [editingComment, setEditingComment] = useState<Comment | null>(null)
  const [newMessageEmail, setNewMessageEmail] = useState("")
  const [newMessageContent, setNewMessageContent] = useState("")
  const [editCommentContent, setEditCommentContent] = useState("")
  const [conversationEmail, setConversationEmail] = useState("")
  const [newConversationMessage, setNewConversationMessage] = useState('')
  const [sendingConversationMessage, setSendingConversationMessage] = useState(false)
  const [loading, setLoading] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const navigate = useNavigate()

  const loadSentMessages = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("MSGES", "list_sent_messages")
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    }
  }

  const loadReceivedMessages = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("MSGES", "list_received_messages")
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    }
  }

  const loadMyComments = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("COMMS", "list_my_comments")
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    }
  }

  const loadConversation = (otherUserEmail: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("MSGES", "list_conversation", otherUserEmail)
        console.log("📤 Enviando mensaje de conversación:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    } else {
      console.error("❌ WebSocket no está conectado para cargar conversación")
    }
  }

  // Función para extraer conversaciones únicas de mensajes enviados y recibidos
  const extractConversations = (sent: Message[], received: Message[]) => {
    const conversationMap = new Map<string, Conversation>()

    // Procesar mensajes enviados
    sent.forEach(msg => {
      const otherUser = msg.receptor_email
      if (!conversationMap.has(otherUser)) {
        conversationMap.set(otherUser, {
          other_user: otherUser,
          messages: [],
          last_message_date: msg.fecha
        })
      }
      const conv = conversationMap.get(otherUser)!
      conv.messages.push({ ...msg, is_sent: true })
      if (new Date(msg.fecha) > new Date(conv.last_message_date)) {
        conv.last_message_date = msg.fecha
      }
    })

    // Procesar mensajes recibidos
    received.forEach(msg => {
      const otherUser = msg.emisor_email
      if (!conversationMap.has(otherUser)) {
        conversationMap.set(otherUser, {
          other_user: otherUser,
          messages: [],
          last_message_date: msg.fecha
        })
      }
      const conv = conversationMap.get(otherUser)!
      conv.messages.push({ ...msg, is_sent: false })
      if (new Date(msg.fecha) > new Date(conv.last_message_date)) {
        conv.last_message_date = msg.fecha
      }
    })

    // Ordenar mensajes dentro de cada conversación por fecha
    conversationMap.forEach(conv => {
      conv.messages.sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime())
    })

    // Convertir a array y ordenar por último mensaje
    const conversations = Array.from(conversationMap.values())
      .sort((a, b) => new Date(b.last_message_date).getTime() - new Date(a.last_message_date).getTime())

    setConversations(conversations)
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
      loadSentMessages()
      loadReceivedMessages()
      loadMyComments()
    }

    socket.onmessage = (event) => {
      console.log("📨 Respuesta del backend:", event.data)
      
      // Respuesta de mensajes enviados
      if (event.data.includes("MSGESOK") && event.data.includes("enviados")) {
        try {
          const msgesOkIndex = event.data.indexOf("MSGESOK")
          const jsonString = event.data.slice(msgesOkIndex + "MSGESOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.messages) {
            setSentMessages(json.messages)
          }
        } catch (err) {
          console.error("Error al parsear mensajes enviados:", err)
        }
      }
      
      // Respuesta de mensajes recibidos
      if (event.data.includes("MSGESOK") && event.data.includes("recibidos")) {
        try {
          const msgesOkIndex = event.data.indexOf("MSGESOK")
          const jsonString = event.data.slice(msgesOkIndex + "MSGESOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.messages) {
            setReceivedMessages(json.messages)
          }
        } catch (err) {
          console.error("Error al parsear mensajes recibidos:", err)
        }
      }

      // Respuesta de conversación específica
      if (event.data.includes("MSGESOK") && (event.data.includes("Conversación con") || event.data.includes("Conversaci\\u00f3n con"))) {
        console.log("📨 Respuesta de conversación detectada:", event.data)
        try {
          const msgesOkIndex = event.data.indexOf("MSGESOK")
          const jsonString = event.data.slice(msgesOkIndex + "MSGESOK".length)
          console.log("🔍 JSON de conversación:", jsonString)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.messages) {
            console.log("✅ Configurando conversación:", json.other_user, "con", json.messages.length, "mensajes")
            setConversationMessages(json.messages)
            setSelectedConversation(json.other_user)
            setIsConversationDialogOpen(true)
            console.log("🎯 Estado del diálogo:", {
              isOpen: true,
              selectedConversation: json.other_user,
              messagesCount: json.messages.length
            })
            // Scroll to bottom after messages load
            setTimeout(() => {
              messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
            }, 100)
          } else {
            console.error("❌ Datos de conversación inválidos:", json)
          }
        } catch (err) {
          console.error("Error al parsear conversación:", err)
        }
      }

      // Respuesta de mis comentarios
      if (event.data.includes("COMMSOK") && event.data.includes("comentarios creados")) {
        try {
          const commsOkIndex = event.data.indexOf("COMMSOK")
          const jsonString = event.data.slice(commsOkIndex + "COMMSOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.comments) {
            setMyComments(json.comments)
          }
        } catch (err) {
          console.error("Error al parsear mis comentarios:", err)
        }
      }
    }

    socket.onerror = (err) => console.error("❌ WebSocket error:", err)
    socket.onclose = () => console.log("🔒 WebSocket cerrado")

    return () => socket.close()
  }, [navigate])

  // Actualizar conversaciones cuando cambien los mensajes
  useEffect(() => {
    extractConversations(sentMessages, receivedMessages)
  }, [sentMessages, receivedMessages])

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessageEmail.trim() || !newMessageContent.trim()) return

    setLoading(true)
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("MSGES", "send_message", newMessageEmail, `'${newMessageContent}'`)
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
        setLoading(false)
      }
    }

    // Escuchar respuesta de envío
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("MSGESOK")) {
          // Extraer el ID del mensaje de la respuesta para crear notificación
          try {
            const msgesOkIndex = event.data.indexOf("MSGESOK")
            const jsonString = event.data.slice(msgesOkIndex + "MSGESOK".length)
            const response = JSON.parse(jsonString)
            
            if (response.success && response.message && response.message.id_mensaje) {
              // Crear notificación para el receptor del mensaje
              const token = localStorage.getItem("token")
              if (token) {
                const messagePreview = newMessageContent.length > 50 ? 
                  newMessageContent.substring(0, 50) + "..." : 
                  newMessageContent
                const notificationMessage = `NOTIFcreate_message_notification ${token} ${newMessageEmail} ${response.message.id_mensaje} '${messagePreview}'`
                socketRef.current?.send(notificationMessage)
              }
            }
          } catch (err) {
            console.error("Error procesando respuesta de mensaje:", err)
          }
          
          setIsCreateDialogOpen(false)
          setNewMessageEmail("")
          setNewMessageContent("")
          setLoading(false)
          toast.success("Mensaje enviado exitosamente")
          loadSentMessages() // Recargar la lista
          loadReceivedMessages() // También recargar recibidos para actualizar conversaciones
        } else if (event.data.includes("MSGESNK")) {
          setLoading(false)
          toast.error("Error enviando mensaje")
          console.error("Error enviando mensaje")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleDeleteMessage = (messageId: number, isAdmin = false) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este mensaje?")) return

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const command = isAdmin ? "admin_delete_message" : "delete_message"
        const message = buildServiceMessage("MSGES", command, messageId.toString())
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    }

    // Escuchar respuesta de eliminación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("MSGESOK") && event.data.includes("eliminado exitosamente")) {
          toast.success("Mensaje eliminado exitosamente")
          loadSentMessages()
          loadReceivedMessages()
          // Si estamos viendo una conversación, recargarla
          if (selectedConversation) {
            loadConversation(selectedConversation)
          }
        } else if (event.data.includes("MSGESNK")) {
          toast.error("Error eliminando mensaje")
          console.error("Error eliminando mensaje")
        }
        
        // Restaurar el handler original
        if (originalOnMessage && socketRef.current) {
          socketRef.current.onmessage = originalOnMessage
        }
      }
    }
  }

  const handleViewConversation = (otherUserEmail: string) => {
    console.log("🔍 Ver conversación con:", otherUserEmail)
    setConversationEmail(otherUserEmail)
    loadConversation(otherUserEmail)
  }

  const handleSendConversationMessage = async () => {
    if (!newConversationMessage.trim() || !selectedConversation || sendingConversationMessage) {
      return
    }

    setSendingConversationMessage(true)
    
    try {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const messageContent = newConversationMessage.trim()
        const message = buildServiceMessage("MSGES", "send_message", selectedConversation, `'${messageContent}'`)
        console.log("📤 Enviando mensaje en conversación:", message)
        socketRef.current.send(message)
        
        // Escuchar la respuesta para obtener el ID del mensaje y enviar notificación
        const originalOnMessage = socketRef.current.onmessage
        socketRef.current.onmessage = (event) => {
          console.log("📨 Respuesta de envío:", event.data)
          
          if (event.data.includes("MSGESOK")) {
            try {
              const msgesOkIndex = event.data.indexOf("MSGESOK")
              const jsonString = event.data.slice(msgesOkIndex + "MSGESOK".length)
              const response = JSON.parse(jsonString)
              
              if (response.success && response.message && response.message.id_mensaje) {
                console.log("✅ Mensaje enviado con ID:", response.message.id_mensaje)
                
                // Enviar notificación
                const token = localStorage.getItem("token")
                if (token) {
                  const messagePreview = messageContent.length > 50 ? 
                    messageContent.substring(0, 50) + '...' : messageContent
                  
                  const notificationMessage = `NOTIFcreate_message_notification ${token} ${selectedConversation} ${response.message.id_mensaje} '${messagePreview}'`
                  console.log("📤 Enviando notificación:", notificationMessage)
                  socketRef.current?.send(notificationMessage)
                }
                
                // Show success toast
                toast.success("Mensaje enviado exitosamente")
                
                // Recargar la conversación después de un breve delay
                setTimeout(() => {
                  loadConversation(selectedConversation)
                  // Scroll to bottom after sending message
                  setTimeout(() => {
                    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
                  }, 200)
                }, 500)
              }
            } catch (err) {
              console.error("Error parseando respuesta de mensaje:", err)
              toast.error("Error procesando respuesta del servidor")
            }
          } else if (event.data.includes("MSGESNK")) {
            console.error("Error enviando mensaje en conversación:", event.data)
            toast.error("Error enviando mensaje")
          }
          
          // Restaurar el handler original
          if (originalOnMessage) {
            socketRef.current!.onmessage = originalOnMessage
          }
          
          // Reset loading state
          setSendingConversationMessage(false)
        }
        
        // Limpiar el input
        setNewConversationMessage('')
      }
    } catch (err) {
      console.error("Error enviando mensaje en conversación:", err)
      toast.error("Error enviando mensaje")
      setSendingConversationMessage(false)
    }
  }

  const canDeleteMessage = (message: Message) => {
    return user && (user.email === message.emisor_email || user.rol === "moderador")
  }

  const canAdminDelete = (message: Message) => {
    return user && user.rol === "moderador" && user.email !== message.emisor_email
  }

  const handleEditComment = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingComment || !editCommentContent.trim()) return

    setLoading(true)
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("COMMS", "update_comment", editingComment.id_comentario.toString(), `'${editCommentContent}'`)
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
        setLoading(false)
      }
    }

    // Escuchar respuesta de actualización
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("COMMSOK") && event.data.includes("actualizado exitosamente")) {
          setIsEditCommentDialogOpen(false)
          setEditingComment(null)
          setEditCommentContent("")
          setLoading(false)
          loadMyComments() // Recargar la lista
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

  const handleDeleteComment = (commentId: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este comentario?")) return

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = buildServiceMessage("COMMS", "delete_comment", commentId.toString())
        console.log("📤 Enviando mensaje:", message)
        socketRef.current.send(message)
      } catch (err) {
        console.error("Error building message:", err)
      }
    }

    // Escuchar respuesta de eliminación
    const originalOnMessage = socketRef.current?.onmessage
    if (socketRef.current) {
      socketRef.current.onmessage = (event) => {
        if (event.data.includes("COMMSOK") && event.data.includes("eliminado exitosamente")) {
          loadMyComments() // Recargar la lista
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

  const openEditCommentDialog = (comment: Comment) => {
    setEditingComment(comment)
    setEditCommentContent(comment.contenido)
    setIsEditCommentDialogOpen(true)
  }

  const goToPost = (postId: number) => {
    navigate(`/post/${postId}`)
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
                <h1 className="text-2xl font-bold">Mensajes y Comentarios</h1>
                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Nuevo Mensaje
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Nuevo Mensaje</DialogTitle>
                      <DialogDescription>
                        Envía un mensaje privado a otro usuario.
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleSendMessage} className="space-y-4">
                      <div>
                        <Label htmlFor="email">Email del destinatario</Label>
                        <Input
                          id="email"
                          type="email"
                          value={newMessageEmail}
                          onChange={(e) => setNewMessageEmail(e.target.value)}
                          placeholder="usuario@ejemplo.com"
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="content">Mensaje</Label>
                        <Textarea
                          id="content"
                          value={newMessageContent}
                          onChange={(e) => setNewMessageContent(e.target.value)}
                          placeholder="Escribe tu mensaje aquí..."
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
                          {loading ? "Enviando..." : "Enviar Mensaje"}
                        </Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              {/* Dialog para ver conversación completa */}
              <Dialog open={isConversationDialogOpen} onOpenChange={setIsConversationDialogOpen}>
                <DialogContent className="max-w-4xl h-[85vh] max-h-[85vh] p-0 w-full overflow-hidden conversation-modal">
                  <div className="flex flex-col h-full w-full">
                    {/* Header */}
                    <DialogHeader className="px-6 py-4 border-b bg-gradient-to-r from-blue-50 to-purple-50 flex-shrink-0">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                          {selectedConversation?.charAt(0).toUpperCase()}
                        </div>
                        <div className="min-w-0 flex-1">
                          <DialogTitle className="text-lg font-semibold text-gray-900 truncate">
                            {selectedConversation}
                          </DialogTitle>
                          <DialogDescription className="text-sm text-gray-600">
                            {conversationMessages.length} mensaje{conversationMessages.length !== 1 ? 's' : ''} en total
                          </DialogDescription>
                        </div>
                      </div>
                    </DialogHeader>

                    {/* Messages Container */}
                    <div className="flex-1 p-4 overflow-hidden" style={{ height: 'calc(85vh - 280px)', maxHeight: 'calc(85vh - 280px)' }}>
                      <div className="h-full overflow-y-auto overflow-x-hidden space-y-4 pr-2 custom-scrollbar">
                        {conversationMessages.length > 0 ? (
                          conversationMessages.map((msg, index) => (
                            <div
                              key={msg.id_mensaje}
                              className={`flex w-full ${msg.is_sent ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}
                              style={{ animationDelay: `${index * 50}ms` }}
                            >
                              <div className={`max-w-[75%] min-w-0 ${msg.is_sent ? 'ml-auto' : 'mr-auto'}`}>
                                {/* Message bubble */}
                                <div className={`relative rounded-2xl p-4 shadow-sm break-words ${
                                  msg.is_sent 
                                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white' 
                                    : 'bg-white border border-gray-200 text-gray-900'
                                }`}>
                                  {/* Message content */}
                                  <p className="text-sm leading-relaxed whitespace-pre-wrap break-words word-wrap overflow-wrap-anywhere">
                                    {msg.contenido}
                                  </p>
                                  
                                  {/* Message tail */}
                                  <div className={`absolute top-3 w-3 h-3 transform rotate-45 ${
                                    msg.is_sent 
                                      ? 'right-[-6px] bg-blue-500' 
                                      : 'left-[-6px] bg-white border-l border-t border-gray-200'
                                  }`} />
                                </div>

                                {/* Message info */}
                                <div className={`flex items-center gap-2 mt-1 px-2 flex-wrap ${
                                  msg.is_sent ? 'justify-end' : 'justify-start'
                                }`}>
                                  <span className="text-xs text-gray-500 flex-shrink-0">
                                    {msg.is_sent ? 'Tú' : msg.emisor_email?.split('@')[0]}
                                  </span>
                                  <span className="text-xs text-gray-400 flex-shrink-0">•</span>
                                  <span className="text-xs text-gray-500 flex-shrink-0">
                                    {new Date(msg.fecha).toLocaleString('es-ES', {
                                      month: 'short',
                                      day: 'numeric',
                                      hour: '2-digit',
                                      minute: '2-digit'
                                    })}
                                  </span>
                                  {canDeleteMessage(msg) && (
                                    <>
                                      <span className="text-xs text-gray-400 flex-shrink-0">•</span>
                                      <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                          <Button 
                                            variant="ghost" 
                                            size="sm" 
                                            className="h-6 w-6 p-0 text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                                          >
                                            <MoreVertical className="h-3 w-3" />
                                          </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                          <DropdownMenuItem 
                                            onClick={() => handleDeleteMessage(msg.id_mensaje, canAdminDelete(msg))}
                                            className="text-red-600 focus:text-red-700"
                                          >
                                            <Trash2 className="mr-2 h-3 w-3" />
                                            Eliminar
                                          </DropdownMenuItem>
                                        </DropdownMenuContent>
                                      </DropdownMenu>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="flex items-center justify-center h-full">
                            <div className="text-center text-gray-500">
                              <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                              <p className="text-sm">No hay mensajes en esta conversación</p>
                            </div>
                          </div>
                        )}
                        {/* Invisible div for scrolling to bottom */}
                        <div ref={messagesEndRef} />
                      </div>
                    </div>

                    {/* Message Input */}
                    <div className="px-6 py-4 border-t bg-white flex-shrink-0">
                      <div className="flex items-end gap-3">
                        <div className="flex-1 min-w-0">
                          <Textarea
                            value={newConversationMessage}
                            onChange={(e) => setNewConversationMessage(e.target.value)}
                            placeholder={`Escribe un mensaje a ${selectedConversation}...`}
                            className="min-h-[80px] max-h-[120px] resize-none border-gray-200 focus:border-blue-500 focus:ring-blue-500 w-full"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault()
                                handleSendConversationMessage()
                              }
                            }}
                          />
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500">
                              Presiona Enter para enviar, Shift+Enter para nueva línea
                            </span>
                            <span className="text-xs text-gray-400">
                              {newConversationMessage.length}/1000
                            </span>
                          </div>
                        </div>
                        <Button 
                          onClick={handleSendConversationMessage}
                          disabled={!newConversationMessage.trim() || sendingConversationMessage}
                          className="h-[80px] px-6 bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium flex-shrink-0"
                        >
                          {sendingConversationMessage ? (
                            <div className="flex items-center gap-2">
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                              <span>Enviando...</span>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2">
                              <Send className="h-4 w-4" />
                              <span>Enviar</span>
                            </div>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="px-6 py-3 border-t bg-gray-50 flex-shrink-0">
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-gray-500">
                          Conversación con {selectedConversation}
                        </div>
                        <Button 
                          onClick={() => setIsConversationDialogOpen(false)}
                          variant="outline"
                          size="sm"
                        >
                          Cerrar
                        </Button>
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              {/* Dialog para editar comentario */}
              <Dialog open={isEditCommentDialogOpen} onOpenChange={setIsEditCommentDialogOpen}>
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
                        onClick={() => setIsEditCommentDialogOpen(false)}
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

              <Tabs defaultValue="conversations" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="conversations">
                    <Users2 className="mr-2 h-4 w-4" />
                    Conversaciones ({conversations.length})
                  </TabsTrigger>
                  <TabsTrigger value="received">
                    <Inbox className="mr-2 h-4 w-4" />
                    Recibidos ({receivedMessages.length})
                  </TabsTrigger>
                  <TabsTrigger value="sent">
                    <Send className="mr-2 h-4 w-4" />
                    Enviados ({sentMessages.length})
                  </TabsTrigger>
                  <TabsTrigger value="comments">
                    <MessageCircle className="mr-2 h-4 w-4" />
                    Mis Comentarios ({myComments.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="conversations" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users2 className="h-5 w-5" />
                        Conversaciones
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {conversations.length > 0 ? (
                        <div className="space-y-3">
                          {conversations.map((conv) => {
                            const lastMessage = conv.messages[conv.messages.length - 1]
                            return (
                              <Card key={conv.other_user} className="border-l-4 border-l-purple-500 hover:bg-gray-50 cursor-pointer"
                                    onClick={() => handleViewConversation(conv.other_user)}>
                                <CardHeader className="pb-2">
                                  <div className="flex items-center justify-between">
                                    <div className="space-y-1">
                                      <div className="flex items-center gap-2">
                                        <User className="h-4 w-4" />
                                        <span className="font-medium">{conv.other_user}</span>
                                        <Badge variant="outline" className="text-xs">
                                          {conv.messages.length} mensaje{conv.messages.length !== 1 ? 's' : ''}
                                        </Badge>
                                      </div>
                                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                        <Calendar className="h-3 w-3" />
                                        <span>Último: {new Date(conv.last_message_date).toLocaleDateString()}</span>
                                      </div>
                                    </div>
                                    <Button 
                                      variant="ghost" 
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        handleViewConversation(conv.other_user)
                                      }}
                                    >
                                      <Eye className="h-4 w-4" />
                                      Ver conversación
                                    </Button>
                                  </div>
                                </CardHeader>
                                <CardContent className="pt-0">
                                  <p className="text-sm text-muted-foreground line-clamp-2">
                                    <span className="font-medium">
                                      {lastMessage.is_sent ? 'Tú: ' : `${lastMessage.emisor_email}: `}
                                    </span>
                                    {lastMessage.contenido}
                                  </p>
                                </CardContent>
                              </Card>
                            )
                          })}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No tienes conversaciones aún.</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            ¡Envía tu primer mensaje para comenzar una conversación!
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="received" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Inbox className="h-5 w-5" />
                        Mensajes Recibidos
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {receivedMessages.length > 0 ? (
                        <div className="space-y-3">
                          {receivedMessages.map((message) => (
                            <Card key={message.id_mensaje} className="border-l-4 border-l-green-500">
                              <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                      <User className="h-3 w-3" />
                                      <span className="font-medium">De: {message.emisor_email}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <Calendar className="h-3 w-3" />
                                      {new Date(message.fecha).toLocaleDateString()}
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-2">
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleViewConversation(message.emisor_email)}
                                      className="h-8 px-2"
                                    >
                                      <Eye className="h-4 w-4" />
                                      Ver conversación
                                    </Button>

                                    {canDeleteMessage(message) && (
                                      <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                            <MoreVertical className="h-4 w-4" />
                                          </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                          <DropdownMenuItem 
                                            onClick={() => handleDeleteMessage(message.id_mensaje, canAdminDelete(message))}
                                            className="text-red-600"
                                          >
                                            <Trash2 className="mr-2 h-4 w-4" />
                                            Eliminar
                                          </DropdownMenuItem>
                                        </DropdownMenuContent>
                                      </DropdownMenu>
                                    )}
                                  </div>
                                </div>
                              </CardHeader>
                              <CardContent className="pt-0">
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                  {message.contenido}
                                </p>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No tienes mensajes recibidos.</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="sent" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Send className="h-5 w-5" />
                        Mensajes Enviados
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {sentMessages.length > 0 ? (
                        <div className="space-y-3">
                          {sentMessages.map((message) => (
                            <Card key={message.id_mensaje} className="border-l-4 border-l-blue-500">
                              <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                      <User className="h-3 w-3" />
                                      <span className="font-medium">Para: {message.receptor_email}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <Calendar className="h-3 w-3" />
                                      {new Date(message.fecha).toLocaleDateString()}
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-2">
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleViewConversation(message.receptor_email)}
                                      className="h-8 px-2"
                                    >
                                      <Eye className="h-4 w-4" />
                                      Ver conversación
                                    </Button>

                                    {canDeleteMessage(message) && (
                                      <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                            <MoreVertical className="h-4 w-4" />
                                          </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                          <DropdownMenuItem 
                                            onClick={() => handleDeleteMessage(message.id_mensaje, canAdminDelete(message))}
                                            className="text-red-600"
                                          >
                                            <Trash2 className="mr-2 h-4 w-4" />
                                            Eliminar
                                          </DropdownMenuItem>
                                        </DropdownMenuContent>
                                      </DropdownMenu>
                                    )}
                                  </div>
                                </div>
                              </CardHeader>
                              <CardContent className="pt-0">
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                  {message.contenido}
                                </p>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No has enviado mensajes aún.</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="comments" className="space-y-4">
      <Card>
        <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <MessageCircle className="h-5 w-5" />
                        Mis Comentarios
                      </CardTitle>
        </CardHeader>
        <CardContent>
                      {myComments.length > 0 ? (
                        <div className="space-y-3">
                          {myComments.map((comment) => (
                            <Card key={comment.id_comentario} className="border-l-4 border-l-purple-500">
                              <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                      <Calendar className="h-3 w-3" />
                                      {new Date(comment.fecha).toLocaleDateString()}
                                    </div>
                                    <Badge variant="outline" className="text-xs">
                                      Post: {comment.post_preview}
                                    </Badge>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => goToPost(comment.id_post)}
                                      className="h-8 px-2"
                                    >
                                      <ArrowRight className="h-4 w-4" />
                                      Ver Post
                                    </Button>
                                    
                                    <DropdownMenu>
                                      <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                          <MoreVertical className="h-4 w-4" />
                                        </Button>
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent align="end">
                                        <DropdownMenuItem onClick={() => openEditCommentDialog(comment)}>
                                          <Edit className="mr-2 h-4 w-4" />
                                          Editar
                                        </DropdownMenuItem>
                                        <DropdownMenuItem 
                                          onClick={() => handleDeleteComment(comment.id_comentario)}
                                          className="text-red-600"
                                        >
                                          <Trash2 className="mr-2 h-4 w-4" />
                                          Eliminar
                                        </DropdownMenuItem>
                                      </DropdownMenuContent>
                                    </DropdownMenu>
                                  </div>
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
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No has hecho comentarios aún.</p>
                          <p className="text-sm text-muted-foreground mt-1">
                            ¡Participa en las discusiones de los foros!
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
