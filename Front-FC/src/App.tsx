import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SessionProvider, useActivityTracker } from './contexts/SessionContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Login from './components/Pages/Login';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Pages/Dashboard';
import DashboardAdmin from './components/Pages/DashboardAdmin';
import DashboardPagaduria from './components/Pages/DashboardPagaduria';
import DashboardTesoreria from './components/Pages/DashboardTesoreria';
import Conciliacion from './components/Pages/Conciliacion';
import MonthlyFlow from './components/Pages/MonthlyFlow';
import Reports from './components/Pages/Reports';
import Users from './components/Pages/Users';
import Companies from './components/Pages/Companies';
import Auditoria from './components/Pages/Auditoria';
import Profile from './components/Pages/Profile';
import Settings from './components/Pages/Settings';
import Help from './components/Pages/Help';
import AdminPanel from './components/Pages/AdminPanel';
import Conceptos from './components/Pages/Conceptos';
import HistoricoTRM from './components/Pages/HistoricoTRM';
import CargueInicial from './components/Pages/CargueInicial';
import SessionWarningModal from './components/Session/SessionWarningModal';
import SessionToast from './components/Session/SessionToast';

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const { trackPageNavigation } = useActivityTracker();
  const [currentPage, setCurrentPage] = useState('panel');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Manejar cambio de página con seguimiento de actividad
  const handlePageChange = (page: string) => {
    setCurrentPage(page);
    trackPageNavigation(page);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  const getPageTitle = (page: string) => {
    switch (page) {
      case 'panel':
        if (user?.role === 'administrador') {
          return 'SIFCO - Dashboards de Flujo Diario';
        }
        if (user?.role === 'pagaduria') {
          return 'SIFCO - Flujo Diario de Pagaduría';
        }
        if (user?.role === 'tesoreria') {
          return 'SIFCO - Flujo Diario de Tesorería';
        }
        return 'SIFCO - Flujo Diario';
      case 'conciliacion':
        return 'Conciliación Contable';
      case 'flujo-mensual':
        return 'Dashboard';
      case 'companias':
        return 'Gestión de Compañías';
      case 'conceptos':
        return 'Gestión de Conceptos';
      case 'historico-trm':
        return 'TRM Histórico';
      case 'auditoria':
        return 'Auditoría del Sistema';
      case 'informes':
        return 'Consolidado';
      case 'usuarios':
        return 'Gestión de Usuarios';
      case 'cargue-inicial':
        return 'Cargue Inicial de Saldos';
      case 'perfil':
        return 'Mi Perfil de Usuario';
      case 'configuracion':
        return 'Configuración del Sistema';
      case 'ayuda':
        return 'Ayuda y Soporte';
      case 'admin':
        return 'Panel de Administración';
      default:
        return 'SIFCO - Sistema de Flujo de Caja';
    }
  };

  const getPageSubtitle = (page: string) => {
    const currentDate = new Date().toLocaleDateString('es-CO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    switch (page) {
      case 'panel':
        if (user?.role === 'administrador') {
          return 'Accede a los dashboards actualizados de Tesorería y Pagaduría';
        }
        if (user?.role === 'pagaduria') {
          return 'Panel especializado para gestión de pagos y presupuestos';
        }
        if (user?.role === 'tesoreria') {
          return 'Panel especializado para gestión de tesorería y flujo de caja';
        }
        return currentDate;
      case 'conciliacion':
        return 'Resumen de cierres contables por compañía';
      case 'flujo-mensual':
        return 'Panel de análisis de ingresos y gastos por mes';
      case 'companias':
        return 'Administra las compañías y sus cuentas bancarias';
      case 'conceptos':
        return 'Administra los conceptos de flujo de caja para ambas áreas';
      case 'historico-trm':
        return 'Consulta el histórico de la Tasa Representativa del Mercado';
      case 'auditoria':
        return 'Historial de actividades y cambios del sistema';
      case 'informes':
        return 'Reportes detallados y análisis financiero consolidado';
      case 'usuarios':
        return 'Administración de usuarios del sistema';
      case 'cargue-inicial':
        return 'Configura saldos iniciales para días anteriores';
      case 'perfil':
        return 'Gestiona tu información personal y preferencias';
      case 'configuracion':
        return 'Personaliza tu experiencia en SIFCO';
      case 'ayuda':
        return 'Encuentra respuestas y obtén asistencia';
      case 'admin':
        return 'Herramientas avanzadas de administración del sistema';
      default:
        return currentDate;
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'panel':
        if (user?.role === 'administrador') {
          return <DashboardAdmin />;
        }
        if (user?.role === 'pagaduria') {
          return <DashboardPagaduria />;
        }
        if (user?.role === 'tesoreria') {
          return <DashboardTesoreria />;
        }
        return <Dashboard />;
      case 'conciliacion':
        return <Conciliacion />;
      case 'flujo-mensual':
        return <MonthlyFlow />;
      case 'companias':
        return <Companies />;
      case 'conceptos':
        return <Conceptos />;
      case 'historico-trm':
        return <HistoricoTRM />;
      case 'auditoria':
        return <Auditoria />;
      case 'informes':
        return <Reports />;
      case 'usuarios':
        return <Users />;
      case 'cargue-inicial':
        return <CargueInicial />;
      case 'perfil':
        return <Profile />;
      case 'configuracion':
        return <Settings />;
      case 'ayuda':
        return <Help />;
      case 'admin':
        return <AdminPanel />;
      default:
        if (user?.role === 'administrador') {
          return <DashboardAdmin />;
        }
        if (user?.role === 'pagaduria') {
          return <DashboardPagaduria />;
        }
        if (user?.role === 'tesoreria') {
          return <DashboardTesoreria />;
        }
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar 
        currentPage={currentPage} 
        onPageChange={handlePageChange}
        isCollapsed={sidebarCollapsed}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          title={getPageTitle(currentPage)} 
          subtitle={getPageSubtitle(currentPage)} 
          onPageChange={handlePageChange}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        <main className="flex-1 overflow-y-auto p-6 dark:bg-gray-900">
          {renderPage()}
        </main>
      </div>
      
      {/* Modal y Toast de avisos de sesión */}
      <SessionWarningModal />
      <SessionToast />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <ThemeProvider>
          <AppContent />
        </ThemeProvider>
      </SessionProvider>
    </AuthProvider>
  );
}

export default App;