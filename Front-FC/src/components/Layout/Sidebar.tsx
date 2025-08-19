import React from 'react';
import { 
  LayoutDashboard, 
  Calendar, 
  BarChart3, 
  Users, 
  LogOut,
  DollarSign,
  Building2,
  Shield,
  Calculator
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  isCollapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange, isCollapsed }) => {
  const { logout, user } = useAuth();

  // Función para determinar qué menús puede ver cada rol
  const getAvailableMenus = () => {
    if (!user) return [];

    const baseMenus = [
      { id: 'panel', label: 'Panel', icon: LayoutDashboard }
    ];

    switch (user.role) {
      case 'administrador':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Flujo Mensual', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'informes', label: 'Informes', icon: BarChart3 },
          { id: 'auditoria', label: 'Auditoría', icon: Shield },
          { id: 'usuarios', label: 'Usuarios', icon: Users }
        ];

      case 'tesoreria':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Flujo Mensual', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'informes', label: 'Informes', icon: BarChart3 }
        ];

      case 'pagaduria':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Flujo Mensual', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'informes', label: 'Informes', icon: BarChart3 }
        ];

      case 'mesa_dinero':
        return [
          ...baseMenus,
          { id: 'flujo-mensual', label: 'Flujo Mensual', icon: Calendar },
          { id: 'informes', label: 'Informes', icon: BarChart3 }
        ];

      default:
        return baseMenus;
    }
  };

  const menuItems = getAvailableMenus();

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-screen transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Seguros Bolívar Logo */}
      {!isCollapsed && (
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">SB</span>
            </div>
            <div>
              <div className="text-bolivar-600 font-bold text-lg">SEGUROS</div>
              <div className="text-bolivar-600 font-bold text-lg -mt-1">BOLÍVAR</div>
            </div>
          </div>
        </div>
      )}

      {/* Logo colapsado */}
      {isCollapsed && (
        <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-center">
          <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-sm">SB</span>
          </div>
        </div>
      )}

      {/* SIFCO Application Info */}
      {!isCollapsed && (
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-gray-900 dark:text-white truncate">SIFCO</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">Sistema de Flujo de Caja</p>
            </div>
          </div>
        </div>
      )}

      {/* SIFCO Icon colapsado */}
      {isCollapsed && (
        <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-center">
          <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center">
            <DollarSign className="h-6 w-6 text-white" />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onPageChange(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all group relative ${
                    isActive
                      ? 'bg-bolivar-50 dark:bg-bolivar-900/20 text-bolivar-700 dark:text-bolivar-400 border-r-2 border-bolivar-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }`}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className={`h-5 w-5 ${isActive ? 'text-bolivar-600 dark:text-bolivar-400' : 'text-gray-500 dark:text-gray-400'} ${
                    isCollapsed ? 'mx-auto' : ''
                  }`} />
                  {!isCollapsed && <span className="font-medium">{item.label}</span>}
                  
                  {/* Tooltip para modo colapsado */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                      {item.label}
                    </div>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={logout}
          className={`w-full flex items-center space-x-3 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-400 rounded-lg transition-all group relative ${
            isCollapsed ? 'justify-center' : ''
          }`}
          title={isCollapsed ? 'Cerrar sesión' : undefined}
        >
          <LogOut className="h-5 w-5" />
          {!isCollapsed && <span className="font-medium">Cerrar sesión</span>}
          
          {/* Tooltip para modo colapsado */}
          {isCollapsed && (
            <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              Cerrar sesión
            </div>
          )}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
