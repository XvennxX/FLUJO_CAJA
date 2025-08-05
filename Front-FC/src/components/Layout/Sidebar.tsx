import React from 'react';
import { 
  LayoutDashboard, 
  Calendar, 
  BarChart3, 
  Users, 
  LogOut,
  DollarSign,
  Building2,
  Shield
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange }) => {
  const { logout } = useAuth();

  const menuItems = [
    { id: 'panel', label: 'Panel', icon: LayoutDashboard },
    { id: 'conciliacion', label: 'Conciliación', icon: DollarSign },
    { id: 'flujo-mensual', label: 'Flujo Mensual', icon: Calendar },
    { id: 'companias', label: 'Compañías', icon: Building2 },
    { id: 'informes', label: 'Informes', icon: BarChart3 },
    { id: 'auditoria', label: 'Auditoría', icon: Shield },
    { id: 'usuarios', label: 'Usuarios', icon: Users },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      {/* Seguros Bolívar Logo */}
      <div className="p-6 border-b border-gray-200">
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

      {/* SIFCO Application Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center">
            <DollarSign className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-gray-900 truncate">SIFCO</p>
            <p className="text-xs text-gray-500 truncate">Sistema de Flujo de Caja</p>
          </div>
        </div>
      </div>

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
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all ${
                    isActive
                      ? 'bg-bolivar-50 text-bolivar-700 border-r-2 border-bolivar-500'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`h-5 w-5 ${isActive ? 'text-bolivar-600' : 'text-gray-500'}`} />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-red-50 hover:text-red-700 rounded-lg transition-all"
        >
          <LogOut className="h-5 w-5" />
          <span className="font-medium">Cerrar sesión</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;