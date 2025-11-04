import React, { useState } from 'react';
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
  TrendingUp,
  ChevronDown,
  ChevronRight,
  DollarSign,
  Settings,
  FileText
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  isCollapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange, isCollapsed }) => {
  const { logout, user } = useAuth();
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);

  // Función para determinar qué menús puede ver cada rol organizados por categorías
  const getMenuStructure = () => {
    if (!user) return [];

    const menuStructure = [
      {
        id: 'gestion',
        label: 'Gestión Financiera',
        icon: DollarSign,
        items: [
          { id: 'panel', label: 'Flujo Diario', icon: LayoutDashboard },
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp }
        ]
      },
      {
        id: 'analisis',
        label: 'Análisis y Reportes',
        icon: FileText,
        items: [
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 }
        ]
      },
      {
        id: 'parametros',
        label: 'Parámetros',
        icon: Settings,
        items: [
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'conceptos', label: 'Conceptos', icon: Layers }
        ]
      },
      {
        id: 'control',
        label: 'Control y Seguridad',
        icon: Shield,
        items: [
          { id: 'auditoria', label: 'Auditoría', icon: Shield },
          { id: 'usuarios', label: 'Usuarios', icon: Users }
        ]
      }
    ];

    // Filtrar según el rol del usuario
    switch (user.role) {
      case 'administrador':
        return menuStructure; // Admin ve todo incluyendo Control y Seguridad

      case 'tesoreria':
        return menuStructure.filter(group => 
          // Tesorería no ve Control y Seguridad
          group.id !== 'control'
        );

      case 'pagaduria':
        return menuStructure.filter(group => 
          // Pagaduría no ve Control y Seguridad
          group.id !== 'control'
        );

      case 'mesa_dinero':
        return menuStructure.filter(group => 
          // Mesa de dinero no ve parámetros ni Control y Seguridad
          group.id !== 'parametros' && group.id !== 'control'
        ).map(group => {
          if (group.id === 'gestion') {
            // Mesa de dinero no ve conciliación
            return {
              ...group,
              items: group.items.filter(item => item.id !== 'conciliacion')
            };
          }
          return group;
        });

      default:
        return [{
          id: 'gestion',
          label: 'Gestión Financiera',
          icon: DollarSign,
          items: [{ id: 'panel', label: 'Flujo Diario', icon: LayoutDashboard }]
        }];
    }
  };

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupId)
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  const menuStructure = getMenuStructure();

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
      <nav className={`flex-1 ${isCollapsed ? 'p-2' : 'p-4'} overflow-y-auto`}>
        {isCollapsed ? (
          // Modo colapsado: mostrar solo iconos sin agrupación
          <ul className="space-y-1">
            {menuStructure.flatMap(group => group.items).map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <li key={item.id}>
                  <button
                    onClick={() => onPageChange(item.id)}
                    className={`w-full flex items-center justify-center p-3 rounded-lg text-left transition-all group relative ${
                      isActive
                        ? 'bg-bolivar-50 dark:bg-bolivar-900/20 text-bolivar-700 dark:text-bolivar-400 border-r-2 border-bolivar-500'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                    }`}
                    title={item.label}
                  >
                    <Icon className={`h-6 w-6 ${
                      isActive ? 'text-bolivar-600 dark:text-bolivar-400' : 'text-gray-500 dark:text-gray-400'
                    }`} />
                    
                    {/* Tooltip para modo colapsado */}
                    <div className="absolute left-full ml-3 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none shadow-lg">
                      {item.label}
                      <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-700"></div>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        ) : (
          // Modo expandido: mostrar agrupación completa
          <div className="space-y-6">
            {menuStructure.map((group) => (
              <div key={group.id}>
                {/* Encabezado del grupo */}
                <button
                  onClick={() => toggleGroup(group.id)}
                  className="w-full flex items-center space-x-3 px-3 py-3 text-base font-bold text-gray-800 dark:text-gray-200 hover:text-bolivar-600 dark:hover:text-bolivar-400 transition-colors border-b border-gray-100 dark:border-gray-700 mb-3"
                >
                  <group.icon className="h-5 w-5" />
                  <span className="flex-1 text-left">{group.label}</span>
                  {expandedGroups.includes(group.id) ? (
                    <ChevronDown className="h-5 w-5" />
                  ) : (
                    <ChevronRight className="h-5 w-5" />
                  )}
                </button>

                {/* Items del grupo */}
                {expandedGroups.includes(group.id) && (
                  <ul className="space-y-2 ml-4 mb-4">
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const isActive = currentPage === item.id;
                      
                      return (
                        <li key={item.id}>
                          <button
                            onClick={() => onPageChange(item.id)}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all text-base ${
                              isActive
                                ? 'bg-bolivar-50 dark:bg-bolivar-900/20 text-bolivar-700 dark:text-bolivar-400 border-r-2 border-bolivar-500 font-medium'
                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200 font-normal'
                            }`}
                          >
                            <Icon className={`h-5 w-5 ${
                              isActive ? 'text-bolivar-600 dark:text-bolivar-400' : 'text-gray-400 dark:text-gray-500'
                            }`} />
                            <span>{item.label}</span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
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
