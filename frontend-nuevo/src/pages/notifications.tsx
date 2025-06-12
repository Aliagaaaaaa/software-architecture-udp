"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function NotificationsPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Notificaciones</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Aquí se mostrarán las notificaciones generadas por el sistema o por tus interacciones.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
