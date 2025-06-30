import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { LoginForm } from "@/components/login-form"
import { Register } from "@/components/register"
import Forums from "@/forums"
import ForumDetail from "@/pages/forum-detail"
import PostDetail from "@/pages/post-detail"
import { CrearPublicacion } from "@/pages/crear-publicacion"
import { CrearEvento } from "@/pages/crear-evento"
import { CrearReporte } from "@/pages/crear-reporte"
import { NotificationsPage } from "@/pages/notifications"
import Messages from "@/pages/messages"
import { StatsPage } from "@/pages/stats"
import { DocumentsPage } from "@/pages/documents"
import { RulesPage } from "@/pages/rules"
import { Profile } from "@/pages/profile"
import AdminUsers from "@/pages/admin-users"
import SystemInfo from "@/pages/system-info"
import { AuthProvider } from "@/contexts/AuthContext"
import { Toaster } from "@/components/ui/sonner"

function App() {
  return (
    <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
          <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forums" element={<Forums />} />
          <Route path="/forum/:forumId" element={<ForumDetail />} />
          <Route path="/post/:postId" element={<PostDetail />} />
        <Route path="/crear-publicacion" element={<CrearPublicacion />} />
        <Route path="/crear-evento" element={<CrearEvento />} />
        <Route path="/crear-reporte" element={<CrearReporte />} />
        <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/messages" element={<Messages />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/perfil" element={<Profile />} />
          <Route path="/admin/users" element={<AdminUsers />} />
          <Route path="/system-info" element={<SystemInfo />} />
      </Routes>
    </Router>
    <Toaster />
    </AuthProvider>
  )
}

export default App