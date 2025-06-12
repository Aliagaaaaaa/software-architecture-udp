import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function CrearEvento() {
  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Crear Evento</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Programa y comparte un evento con otros estudiantes.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
