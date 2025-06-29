import {
  IconCirclePlusFilled,
  IconFileDescription,
  IconCalendarEvent,
  IconReport,
  type Icon,
} from "@tabler/icons-react"
import { useNavigate } from "react-router-dom"
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"

export function NavMain({
  items,
}: {
  items: {
    title: string
    url: string
    icon?: Icon
  }[]
}) {
  const navigate = useNavigate()

  return (
    <SidebarGroup>
      <SidebarGroupContent className="flex flex-col gap-2">
        {/* Botón Crear como dropdown */}
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  tooltip="Crear"
                  className="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear"
                >
                  <IconCirclePlusFilled />
                  <span>Crear</span>
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48 ml-2">
                <DropdownMenuItem onClick={() => navigate("/crear-publicacion")}>
                  <IconFileDescription className="size-4" />
                  <span>Publicación</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate("/crear-evento")}>
                  <IconCalendarEvent className="size-4" />
                  <span>Evento</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate("/crear-reporte")}>
                  <IconReport className="size-4" />
                  <span>Reporte</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>

        {/* Menú principal */}
        <SidebarMenu>
          {items.map((item) => (
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
  )
}