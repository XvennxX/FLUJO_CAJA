import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Pages/Dashboard';
import Transactions from './components/Pages/Transactions';
import MonthlyFlow from './components/Pages/MonthlyFlow';
import Categories from './components/Pages/Categories';
import Reports from './components/Pages/Reports';
import Users from './components/Pages/Users';

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
    return <LoginForm />;
  }

  const getPageTitle = (page: string) => {
    switch (page) {
      case 'panel':
        return 'Sistema de Flujo de Caja';
      case 'transacciones':
        return 'Gestión de Transacciones';
      case 'flujo-mensual':
        return 'Flujo Mensual';
      case 'categorias':
        return 'Gestión de Categorías';
      case 'informes':
        return 'Informes y Reportes';
      case 'usuarios':
        return 'Gestión de Usuarios';
      default:
        return 'Sistema de Flujo de Caja';
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
      case 'transacciones':
        return 'Administra todos los movimientos financieros';
      case 'flujo-mensual':
        return 'Análisis de ingresos y gastos por mes';
      case 'categorias':
        return 'Organiza tus transacciones por categorías';
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
      case 'transacciones':
        return <Transactions />;
      case 'flujo-mensual':
        return <MonthlyFlow />;
      case 'categorias':
        return <Categories />;
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