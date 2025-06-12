import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { LoginForm } from "@/components/login-form"
import { Register } from "@/components/register"
import Forums from "@/forums"
import { CrearPublicacion } from "@/pages/crear-publicacion"
import { CrearEvento } from "@/pages/crear-evento"
import { CrearReporte } from "@/pages/crear-reporte"
import { NotificationsPage } from "@/pages/notifications"
import { MessagesPage } from "@/pages/messages"
import { StatsPage } from "@/pages/stats"
import { DocumentsPage } from "@/pages/documents"
import { RulesPage } from "@/pages/rules"
import { Profile } from "@/pages/profile"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forums" element={<Forums />} />
        <Route path="/crear-publicacion" element={<CrearPublicacion />} />
        <Route path="/crear-evento" element={<CrearEvento />} />
        <Route path="/crear-reporte" element={<CrearReporte />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/messages" element={<MessagesPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/perfil" element={<Profile />} />

      </Routes>
    </Router>
  )
}

export default App