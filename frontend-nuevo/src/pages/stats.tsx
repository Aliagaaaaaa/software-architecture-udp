"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function StatsPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Estadísticas del Foro</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Se mostrarán métricas del uso del foro: publicaciones activas, usuarios más activos, etc.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
