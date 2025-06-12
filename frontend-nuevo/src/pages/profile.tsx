// src/pages/profile.tsx
import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Label } from "@/components/ui/label"

interface ProfileProps {
  email: string
  name?: string
  avatar?: string
  rol: string
}

export function Profile() {
  const token = localStorage.getItem("token")
  const payload = token
    ? JSON.parse(atob(token.split(".")[1]))
    : null

  if (!payload) {
    window.location.href = "/"
    return null
  }

  const { email, rol } = payload

  return (
    <div className="p-6">
      <Card className="max-w-lg mx-auto">
        <CardHeader>
          <CardTitle>Mi Perfil</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex items-center gap-4">
            <Avatar>
              <AvatarImage src={payload.avatar || ""} alt={email} />
              <AvatarFallback>
                {email.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{payload.name || email}</p>
              <p className="text-sm text-muted-foreground">{email}</p>
            </div>
          </div>

          <div className="grid gap-2">
            <div>
              <Label>Correo</Label>
              <p className="text-sm">{email}</p>
            </div>
            <div>
              <Label>Rol</Label>
              <p className="text-sm capitalize">{rol}</p>
            </div>
          </div>

          <div className="pt-4">
            <Button>Edita tu perfil</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}