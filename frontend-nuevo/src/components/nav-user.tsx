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
  const avatarUrl = user?.avatar ?? "/avatars/default.jpg"

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