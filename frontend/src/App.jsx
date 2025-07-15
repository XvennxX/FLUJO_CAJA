import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import TransaccionesPage from './pages/transacciones/TransaccionesPage'
import CategoriasPage from './pages/categorias/CategoriasPage'
import ReportesPage from './pages/reportes/ReportesPage'
import UsuariosPage from './pages/usuarios/UsuariosPage'
import FlujoMensualPage from './pages/flujo/FlujoMensualPage'

function App() {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/transacciones" element={<TransaccionesPage />} />
        <Route path="/flujo/:mes/:anio" element={<FlujoMensualPage />} />
        <Route path="/categorias" element={<CategoriasPage />} />
        <Route path="/reportes" element={<ReportesPage />} />
        <Route path="/usuarios" element={<UsuariosPage />} />
        <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
