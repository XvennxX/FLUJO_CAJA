import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Login from './components/Pages/Login';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Pages/Dashboard';
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

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
        if (user?.role === 'pagaduria') {
          return 'SIFCO - Panel de Pagaduría';
        }
        if (user?.role === 'tesoreria') {
          return 'SIFCO - Panel de Tesorería';
        }
        return 'SIFCO - Sistema de Flujo de Caja';
      case 'conciliacion':
        return 'Conciliación Contable';
      case 'flujo-mensual':
        return 'Flujo Mensual';
      case 'companias':
        return 'Gestión de Compañías';
      case 'auditoria':
        return 'Auditoría del Sistema';
      case 'informes':
        return 'Informes y Reportes';
      case 'usuarios':
        return 'Gestión de Usuarios';
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
        return 'Análisis de ingresos y gastos por mes';
      case 'companias':
        return 'Administra las compañías y sus cuentas bancarias';
      case 'auditoria':
        return 'Historial de actividades y cambios del sistema';
      case 'informes':
        return 'Reportes detallados y análisis financiero';
      case 'usuarios':
        return 'Administración de usuarios del sistema';
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
      case 'auditoria':
        return <Auditoria />;
      case 'informes':
        return <Reports />;
      case 'usuarios':
        return <Users />;
      case 'perfil':
        return <Profile />;
      case 'configuracion':
        return <Settings />;
      case 'ayuda':
        return <Help />;
      case 'admin':
        return <AdminPanel />;
      default:
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
        onPageChange={setCurrentPage}
        isCollapsed={sidebarCollapsed}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          title={getPageTitle(currentPage)} 
          subtitle={getPageSubtitle(currentPage)} 
          onPageChange={setCurrentPage}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        <main className="flex-1 overflow-y-auto p-6 dark:bg-gray-900">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;