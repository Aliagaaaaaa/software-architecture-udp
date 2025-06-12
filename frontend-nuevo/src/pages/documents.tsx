"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DocumentsPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Documentos del Curso</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Aquí encontrarás archivos y documentos compartidos por tus docentes o compañeros.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
