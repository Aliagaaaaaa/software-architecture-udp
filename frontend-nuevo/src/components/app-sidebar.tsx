import * as React from "react"
import {
  IconBell,
  IconLayoutDashboard,
  IconMessage,
  IconReport,
  IconCalendarEvent,
  IconBook,
  IconClipboardList,
  IconChevronRight,
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
} from "@/components/ui/sidebar"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  user: {
    name: string
    email: string
    avatar: string
  }
}

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const navMain = [
    {
      title: "Foros",
      url: "/forums",
      icon: IconLayoutDashboard,
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

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/">
                <IconChevronRight className="!size-5" />
                <span className="text-base font-semibold">Foro UDP</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavDocuments items={navDocuments} />
        <NavSecondary items={navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  )
}