"use client"

import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

type Foro = {
  id: number
  titulo: string
  descripcion: string
}

export default function Forums() {
  const [foros, setForos] = useState<Foro[]>([])
  const [user, setUser] = useState<any>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }

    const payload = JSON.parse(atob(token.split(".")[1]))
    setUser(payload)

    const socket = new WebSocket("ws://localhost:3001")
    socket.onopen = () => {
      socket.send("FORUMlist_forums " + token)
    }

    socket.onmessage = (event) => {
      // Buscar el patrón que indica respuesta de foros
      if (event.data.includes("FORUMOK")) {
        try {
          // Extraer el JSON que viene después del código de respuesta
          const forumOkIndex = event.data.indexOf("FORUMOK")
          const jsonString = event.data.slice(forumOkIndex + "FORUMOK".length)
          const json = JSON.parse(jsonString)
          
          if (json.success && json.forums) {
            // Mapear los datos a la estructura esperada por el componente
            const forosFormateados = json.forums.map((foro: any) => ({
              id: foro.id_foro,
              titulo: foro.titulo,
              descripcion: foro.categoria || "Sin descripción"
            }))
            setForos(forosFormateados)
          }
        } catch (err) {
          console.error("Error al parsear foros:", err)
        }
      }
    }

    socket.onerror = console.error
    socket.onclose = () => console.log("WebSocket cerrado")
  }, [navigate])

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
              <h2 className="text-2xl font-semibold">Foros Disponibles</h2>
              {foros.map((foro) => (
                <div key={foro.id} className="border p-4 rounded shadow">
                  <h3 className="text-xl font-bold">{foro.titulo}</h3>
                  <p className="text-muted-foreground">{foro.descripcion}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}