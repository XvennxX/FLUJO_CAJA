import React from 'react';
import { 
  LayoutDashboard, 
  Calendar, 
  BarChart3, 
  Users, 
  LogOut,
  Building2,
  Shield,
  Calculator,
  Layers,
  TrendingUp
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
      { id: 'panel', label: 'Flujo Diario', icon: LayoutDashboard }
    ];

    switch (user.role) {
      case 'administrador':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'conceptos', label: 'Conceptos', icon: Layers },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 },
          { id: 'auditoria', label: 'Auditoría', icon: Shield },
          { id: 'usuarios', label: 'Usuarios', icon: Users }
        ];

      case 'tesoreria':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'conceptos', label: 'Conceptos', icon: Layers },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 }
        ];

      case 'pagaduria':
        return [
          ...baseMenus,
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'conceptos', label: 'Conceptos', icon: Layers },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 }
        ];

      case 'mesa_dinero':
        return [
          ...baseMenus,
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'conceptos', label: 'Conceptos', icon: Layers },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 }
        ];

      default:
        return baseMenus;
    }
  };

  const menuItems = getAvailableMenus();

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-screen transition-all duration-300 ${
      isCollapsed ? 'w-20' : 'w-64'
    }`}>
      {/* Logo Seguros Bolívar - Arriba */}
      {!isCollapsed && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 h-[80px] flex items-center justify-center">
          <img 
            src="/logos/seguros-bolivar-completo.png" 
            alt="Seguros Bolívar" 
            className="h-16 w-auto object-contain"
          />
        </div>
      )}

      {/* Logo Bolívar colapsado */}
      {isCollapsed && (
        <div className="py-3 border-b border-gray-200 dark:border-gray-700 h-[80px] flex items-center justify-center">
          <img 
            src="/logos/bolivar-icon.png" 
            alt="Seguros Bolívar" 
            className="h-14 w-auto object-contain"
            title="Seguros Bolívar"
          />
        </div>
      )}

      {/* Logo SIFCO - Abajo */}
      {!isCollapsed && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 h-[80px] flex items-center justify-center">
          <img 
            src="/logos/sifco-logo.png" 
            alt="SIFCO - Sistema de Flujo de Caja" 
            className="h-16 w-auto object-contain"
          />
        </div>
      )}

      {/* Logo SIFCO colapsado */}
      {isCollapsed && (
        <div className="py-3 border-b border-gray-200 dark:border-gray-700 h-[80px] flex items-center justify-center">
          <img 
            src="/logos/sifco-icon.png" 
            alt="SIFCO" 
            className="h-12 w-auto object-contain"
            title="SIFCO - Sistema de Flujo de Caja"
          />
        </div>
      )}

      {/* Navigation */}
      <nav className={`flex-1 ${isCollapsed ? 'p-2' : 'p-4'}`}>
        <ul className={isCollapsed ? 'space-y-1' : 'space-y-2'}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onPageChange(item.id)}
                  className={`w-full flex items-center rounded-lg text-left transition-all group relative ${
                    isCollapsed 
                      ? 'justify-center p-3' 
                      : 'space-x-3 px-3 py-2'
                  } ${
                    isActive
                      ? 'bg-bolivar-50 dark:bg-bolivar-900/20 text-bolivar-700 dark:text-bolivar-400 border-r-2 border-bolivar-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }`}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className={`${
                    isCollapsed ? 'h-6 w-6' : 'h-5 w-5'
                  } ${
                    isActive ? 'text-bolivar-600 dark:text-bolivar-400' : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  {!isCollapsed && <span className="font-medium">{item.label}</span>}
                  
                  {/* Tooltip para modo colapsado */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-3 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none shadow-lg">
                      {item.label}
                      {/* Flecha del tooltip */}
                      <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-700"></div>
                    </div>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className={`${isCollapsed ? 'p-2' : 'p-4'} border-t border-gray-200 dark:border-gray-700`}>
        <button
          onClick={logout}
          className={`w-full flex items-center rounded-lg text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-400 transition-all group relative ${
            isCollapsed ? 'justify-center p-3' : 'space-x-3 px-3 py-2'
          }`}
          title={isCollapsed ? 'Cerrar sesión' : undefined}
        >
          <LogOut className={isCollapsed ? 'h-6 w-6' : 'h-5 w-5'} />
          {!isCollapsed && <span className="font-medium">Cerrar sesión</span>}
          
          {/* Tooltip para modo colapsado */}
          {isCollapsed && (
            <div className="absolute left-full ml-3 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none shadow-lg">
              Cerrar sesión
              {/* Flecha del tooltip */}
              <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-700"></div>
            </div>
          )}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
