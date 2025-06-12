import { useState, useCallback } from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSocket } from "@/hooks/useSocket"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "sonner"
import { useNavigate } from "react-router-dom"

export function CrearPublicacion() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const [response, setResponse] = useState("")

  const handleMessage = useCallback((msg: string) => {
    setResponse(msg)
    if (msg.includes("POST_OK")) {
      toast.success("¡Publicación creada con éxito!")
      setTimeout(() => navigate("/forums"), 1500)
    } else {
      toast.error("Error al crear la publicación.")
    }
  }, [navigate])

  const { sendMessage } = useSocket(handleMessage)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!user || !user.name) {
      toast.warning("Primero debes configurar tu perfil para poder publicar.")
      return
    }

    const datos = `${title}|${content}|${user.email}|${user.name}`
    const mensaje = `00001POSTS${datos}`

    sendMessage(mensaje)
    setSubmitted(true)
  }

  return (
    <Card className="max-w-2xl mx-auto mt-10">
      <CardHeader>
        <CardTitle>Crear Publicación</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="Título de la publicación"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <Textarea
            placeholder="Contenido"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <Button type="submit">Publicar</Button>
          {submitted && <p className="text-green-600">Respuesta: {response}</p>}
        </form>
      </CardContent>
    </Card>
  )
}