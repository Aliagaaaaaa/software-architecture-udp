"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function MessagesPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Mensajes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Aquí podrás revisar tus conversaciones y mensajes privados con otros estudiantes.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
