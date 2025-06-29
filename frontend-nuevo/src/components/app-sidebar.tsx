import * as React from "react"
import { useNavigate } from "react-router-dom"
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

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const navigate = useNavigate()

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
  ]

  const navAdmin = [
    {
      title: "Gestión de Usuarios",
      url: "/admin/users",
      icon: IconUsers,
    },
    {
      title: "Información del Sistema",
      url: "/system-info",
      icon: IconInfoCircle,
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
        
        <NavSecondary items={navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  )
}