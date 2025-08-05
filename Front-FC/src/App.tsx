import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Pages/Login';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Pages/Dashboard';
import Conciliacion from './components/Pages/Conciliacion';
import MonthlyFlow from './components/Pages/MonthlyFlow';
import Reports from './components/Pages/Reports';
import Users from './components/Pages/Users';
import Companies from './components/Pages/Companies';
import Auditoria from './components/Pages/Auditoria';

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [currentPage, setCurrentPage] = useState('panel');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando...</p>
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
      default:
        return currentDate;
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'panel':
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
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          title={getPageTitle(currentPage)} 
          subtitle={getPageSubtitle(currentPage)} 
        />
        <main className="flex-1 overflow-y-auto p-6">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;