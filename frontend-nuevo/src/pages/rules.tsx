"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function RulesPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Normas del Foro</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Estas son las reglas que rigen el uso responsable del foro. Revisa las políticas de respeto y uso académico.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
