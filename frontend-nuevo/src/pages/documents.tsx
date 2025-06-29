"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

export function DocumentsPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      setUser({
        name: payload.name || payload.email,
        email: payload.email,
        avatar: payload.avatar || "",
        rol: payload.rol
      })
    } catch (err) {
      console.error("Error parsing token:", err)
      navigate("/login")
    }
  }, [navigate])

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" user={user} />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-col gap-6 p-6">
          <Card>
            <CardHeader>
              <CardTitle>Documentos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Aquí se mostrarán documentos importantes del foro y del sistema.
              </p>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
