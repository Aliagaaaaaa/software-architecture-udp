import * as React from "react"
import { useNavigate } from "react-router-dom"
import { useEffect, useState, useRef } from "react"
import {
  IconBell,
  IconLayoutDashboard,
  IconMessage,
  IconReport,
  IconCalendarEvent,
  IconBook,
  IconClipboardList,
  IconChevronRight,
  IconUsers,
  IconShield,
  IconInfoCircle,
  IconFileText,
} from "@tabler/icons-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  user: {
    name: string
    email: string
    avatar: string
    rol?: string
  }
}

// Utilidad simple para obtener token
const getToken = () => {
  try {
    return localStorage.getItem("token") || ""
  } catch {
    return ""
  }
}

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const navigate = useNavigate()
  const [unreadCount, setUnreadCount] = useState(0)
  const socketRef = useRef<WebSocket | null>(null)

  // Obtener recuento de notificaciones no leídas al montar
  useEffect(() => {
    const token = getToken()
    if (!token) return

    const socket = new WebSocket("ws://4.228.228.99:3001")
    socketRef.current = socket

    socket.onopen = () => {
      socket.send(`NOTIFget_unread_count ${token}`)
    }

    socket.onmessage = (event) => {
      if (event.data.includes("NOTIFOK")) {
        try {
          const idx = event.data.indexOf("NOTIFOK")
          const jsonString = event.data.slice(idx + "NOTIFOK".length)
          const response = JSON.parse(jsonString)
          if (response.unread_count !== undefined) {
            setUnreadCount(response.unread_count)
          }
        } catch {
          /* ignore parse errors */
        }
      }
    }

    return () => {
      socket.close()
    }
  }, [])

  const navMain = [
    {
      title: "Foros",
      url: "/forums",
      icon: IconLayoutDashboard,
    },
    {
      title: "Mis Publicaciones",
      url: "/perfil",
      icon: IconFileText,
    },
    {
      title: "Estadísticas",
      url: "/stats",
      icon: IconClipboardList,
    },
  ]

  const navDocuments = [
    {
      name: "Normas del foro",
      url: "/rules",
      icon: IconBook,
    },
    {
      name: "Estadísticas",
      url: "/stats",
      icon: IconClipboardList,
    },
    {
      name: "Documentos del curso",
      url: "/documents",
      icon: IconBook,
    },
  ]

  const navSecondary = [
    {
      title: "Notificaciones",
      url: "/notifications",
      icon: IconBell,
    },
    {
      title: "Mensajes",
      url: "/messages",
      icon: IconMessage,
    },
    {
      title: "Reportes",
      url: "/crear-reporte",
      icon: IconReport,
    },
    {
      title: "Eventos",
      url: "/crear-evento",
      icon: IconCalendarEvent,
    },
    {
      title: "Información del Sistema",
      url: "/system-info",
      icon: IconInfoCircle,
    },
  ]

  const navAdmin = [
    {
      title: "Gestión de Usuarios",
      url: "/admin/users",
      icon: IconUsers,
    },
  ]

  const isModerator = user?.rol === "moderador"

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
              onClick={() => navigate("/")}
            >
              <div>
                <IconChevronRight className="!size-5" />
                <span className="text-base font-semibold">Foro UDP</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavDocuments items={navDocuments} />
        
        {/* Sección de administración solo para moderadores */}
        {isModerator && (
          <SidebarGroup>
            <SidebarGroupLabel className="flex items-center gap-2">
              <IconShield className="h-4 w-4" />
              Administración
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {navAdmin.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton tooltip={item.title} onClick={() => navigate(item.url)}>
                      {item.icon && <item.icon />}
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
        
        <NavSecondary items={navSecondary} unreadCount={unreadCount} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  )
}