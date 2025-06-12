import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function CrearReporte() {
  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Crear Reporte</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Describe y envía un reporte relacionado con el uso del foro o sus usuarios.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
