import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  LogOut,
  Settings,
  User,
  HelpCircle,
  ChevronRight,
} from "lucide-react"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"
import { useState, useEffect } from "react"

type NavUserProps = {
  user: {
    name?: string
    email?: string
    avatar?: string
    rol?: string
  }
}

export function NavUser({ user }: NavUserProps) {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [avatarUrl, setAvatarUrl] = useState<string>(user?.avatar ?? "/avatars/default.jpg")

  // Si no tenemos avatar en el token, intentar obtenerlo desde el perfil
  useEffect(() => {
    if (user?.avatar) return // ya tenemos avatar

    const token = localStorage.getItem("token")
    if (!token) return

    const socket = new WebSocket("ws://4.228.228.99:3001")

    socket.onopen = () => {
      socket.send(`PROFSget_profile ${token}`)
    }

    socket.onmessage = (event) => {
      if (event.data.includes("PROFSOK")) {
        try {
          const idx = event.data.indexOf("PROFSOK")
          const jsonStr = event.data.slice(idx + "PROFSOK".length)
          const json = JSON.parse(jsonStr)
          if (json.success && json.profile && json.profile.avatar) {
            setAvatarUrl(json.profile.avatar)
          }
        } catch {
          /* ignore parse errors */
        }
        socket.close()
      }
      if (event.data.includes("PROFSNK")) {
        socket.close()
      }
    }

    socket.onerror = () => socket.close()

    return () => {
      if (socket.readyState === WebSocket.OPEN) socket.close()
    }
  }, [user?.avatar])

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="relative flex w-full items-center justify-start gap-3 rounded-lg px-3 py-2 text-left"
        >
          <Avatar className="h-8 w-8">
            <AvatarImage src={avatarUrl} alt={user?.name ?? "User"} />
            <AvatarFallback>
              {user?.name?.[0]?.toUpperCase() ?? "U"}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <p className="text-sm font-medium leading-none">{user?.name ?? "Invitado"}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {user?.email ?? "Sin correo"}
            </p>
          </div>
          <ChevronRight className="ml-auto h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user?.name ?? "Invitado"}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {user?.email ?? "Sin correo"}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => navigate("/perfil")}>
          <User className="mr-2 h-4 w-4" />
          Perfil
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate("/configuracion")}>
          <Settings className="mr-2 h-4 w-4" />
          Configuración
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate("/ayuda")}>
          <HelpCircle className="mr-2 h-4 w-4" />
          Ayuda
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Cerrar sesión
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <div className="flex items-center justify-between px-3 py-2">
          <Label htmlFor="modo-dev" className="text-sm">
            Modo desarrollador
          </Label>
          <Switch id="modo-dev" />
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}