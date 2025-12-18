import React, { useState } from 'react';
import { LayoutDashboard, Building2, Users, Eye } from 'lucide-react';
import DashboardTesoreriaComponent from './DashboardTesoreria';
import DashboardPagaduriaComponent from './DashboardPagaduria';

type DashboardType = 'tesoreria' | 'pagaduria';

const DashboardMesa: React.FC = () => {
  const [activeDashboard, setActiveDashboard] = useState<DashboardType>('tesoreria');

  const renderDashboardSelector = () => (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 mb-6">
      {/* Banner de Modo Solo Lectura */}
      <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex items-center gap-2">
          <Eye className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <span className="text-sm font-medium text-blue-800 dark:text-blue-300">
            Modo Solo Lectura - Mesa de Dinero
          </span>
          <span className="ml-auto text-xs text-blue-600 dark:text-blue-400">
            Visualización completa de ambos dashboards
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center">
            <LayoutDashboard className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Dashboards de Flujo Diario
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Selecciona el área para visualizar su flujo de caja específico
            </p>
          </div>
        </div>

        <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveDashboard('tesoreria')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeDashboard === 'tesoreria'
                ? 'bg-white dark:bg-gray-600 text-bolivar-600 dark:text-bolivar-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Building2 className="w-4 h-4" />
            Tesorería
          </button>
          <button
            onClick={() => setActiveDashboard('pagaduria')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeDashboard === 'pagaduria'
                ? 'bg-white dark:bg-gray-600 text-bolivar-600 dark:text-bolivar-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Users className="w-4 h-4" />
            Pagaduría
          </button>
        </div>
      </div>

      {/* Indicador adicional del dashboard activo */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              activeDashboard === 'tesoreria' ? 'bg-blue-500' : 'bg-green-500'
            }`} />
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              Dashboard Activo: {activeDashboard === 'tesoreria' ? 'Tesorería' : 'Pagaduría'}
            </span>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {activeDashboard === 'tesoreria' 
              ? 'Gestión de flujo de caja y liquidez'
              : 'Gestión de pagos y nómina'
            }
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Selector de Dashboard */}
      {renderDashboardSelector()}

      {/* Dashboard Content - Modo Solo Lectura */}
      <div className="min-h-0 relative">
        {/* Overlay sutil para indicar modo solo lectura (opcional) */}
        <div className="pointer-events-none absolute inset-0 z-10 opacity-0 hover:opacity-5 bg-blue-500 transition-opacity rounded-lg" />
        
        {activeDashboard === 'tesoreria' ? (
          <DashboardTesoreriaComponent readOnly={true} />
        ) : (
          <DashboardPagaduriaComponent readOnly={true} />
        )}
      </div>
    </div>
  );
};

export default DashboardMesa;
