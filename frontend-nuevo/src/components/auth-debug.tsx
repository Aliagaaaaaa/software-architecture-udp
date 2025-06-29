import React from "react"
import { useAuth } from "@/hooks/useAuth"
import { getAuthToken, getTokenExpiration, isTokenExpired, isTokenExpiringSoon } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Clock, User, Shield, AlertTriangle, CheckCircle } from "lucide-react"

export function AuthDebug() {
  const { user, isAuthenticated, isTokenValid, isLoading } = useAuth()
  const token = getAuthToken()

  if (process.env.NODE_ENV === "production") {
    return null
  }

  const tokenExpiration = token ? getTokenExpiration(token) : null
  const tokenExpired = token ? isTokenExpired(token) : true
  const tokenExpiringSoon = token ? isTokenExpiringSoon(token) : true

  return (
    <Card className="fixed bottom-4 right-4 w-80 z-50 bg-white/95 backdrop-blur-sm border shadow-lg">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Shield className="h-4 w-4" />
          Auth Debug
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <span>Estado:</span>
          <Badge variant={isAuthenticated ? "default" : "destructive"}>
            {isLoading ? "Cargando..." : isAuthenticated ? "Autenticado" : "No autenticado"}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span>Token válido:</span>
          <Badge variant={isTokenValid ? "default" : "destructive"}>
            {isTokenValid ? "Sí" : "No"}
          </Badge>
        </div>

        {user && (
          <div className="flex items-center justify-between">
            <span>Usuario:</span>
            <span className="font-mono">{user.email}</span>
          </div>
        )}

        {user && (
          <div className="flex items-center justify-between">
            <span>Rol:</span>
            <Badge variant={user.rol === "moderador" ? "destructive" : "secondary"}>
              {user.rol}
            </Badge>
          </div>
        )}

        {token && (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span>Token presente:</span>
              <CheckCircle className="h-3 w-3 text-green-500" />
            </div>
            
            <div className="flex items-center justify-between">
              <span>Expira:</span>
              <span className="font-mono text-xs">{tokenExpiration}</span>
            </div>

            <div className="flex items-center justify-between">
              <span>Estado:</span>
              <div className="flex items-center gap-1">
                {tokenExpired ? (
                  <Badge variant="destructive" className="text-xs">
                    <AlertTriangle className="h-2 w-2 mr-1" />
                    Expirado
                  </Badge>
                ) : tokenExpiringSoon ? (
                  <Badge variant="outline" className="text-xs">
                    <Clock className="h-2 w-2 mr-1" />
                    Expira pronto
                  </Badge>
                ) : (
                  <Badge variant="default" className="text-xs">
                    <CheckCircle className="h-2 w-2 mr-1" />
                    Válido
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs"
            onClick={() => {
              console.log("=== AUTH DEBUG INFO ===")
              console.log("User:", user)
              console.log("Token:", token)
              console.log("Token expiration:", tokenExpiration)
              console.log("Is authenticated:", isAuthenticated)
              console.log("Is token valid:", isTokenValid)
              console.log("Is loading:", isLoading)
              console.log("Token expired:", tokenExpired)
              console.log("Token expiring soon:", tokenExpiringSoon)
              console.log("======================")
            }}
          >
            Log Debug Info
          </Button>
        </div>
      </CardContent>
    </Card>
  )
} 