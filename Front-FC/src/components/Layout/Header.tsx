import React, { useState, useRef, useEffect } from 'react';
import { Search, Bell, ChevronDown, User, Settings, LogOut, Shield, HelpCircle, Moon, Sun, Menu } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../hooks/useNotifications';
import NotificationDropdown from './NotificationDropdown';
import SessionIndicator from '../Session/SessionIndicator';

interface HeaderProps {
  title: string;
  subtitle: string;
  onPageChange?: (page: string) => void;
  onToggleSidebar?: () => void;
}

const Header: React.FC<HeaderProps> = ({ title, subtitle, onPageChange, onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const { notifications, unreadCount, markAsRead, markAllAsRead, deleteNotification } = useNotifications();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  
  const currentDate = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsNotificationOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleNotificationToggle = () => {
    setIsNotificationOpen(!isNotificationOpen);
    setIsDropdownOpen(false); // Cerrar dropdown de usuario si está abierto
  };

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case 'administrador':
        return 'Administrador';
      case 'tesoreria':
        return 'Tesorería';
      case 'pagaduria':
        return 'Pagaduría';
      case 'mesa_dinero':
        return 'Mesa de Dinero';
      default:
        return role;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'administrador':
        return 'bg-purple-100 text-purple-800';
      case 'tesoreria':
        return 'bg-blue-100 text-blue-800';
      case 'pagaduria':
        return 'bg-bolivar-100 text-bolivar-800';
      case 'mesa_dinero':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const handleDropdownToggle = () => {
    setIsDropdownOpen(!isDropdownOpen);
    setIsNotificationOpen(false); // Cerrar notificaciones si están abiertas
  };

  const handleLogout = () => {
    setIsDropdownOpen(false);
    logout();
  };

  const handleMenuItemClick = (action: string) => {
    setIsDropdownOpen(false);
    
    // Manejar acción de tema
    if (action === 'theme') {
      toggleTheme();
      return;
    }
    
    // Mapear acciones a páginas
    const pageMap: { [key: string]: string } = {
      'profile': 'perfil',
      'settings': 'configuracion',
      'help': 'ayuda',
      'admin': 'admin'
    };

    const page = pageMap[action];
    if (page && onPageChange) {
      onPageChange(page);
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3">
      <div className="flex items-center justify-between h-12">
        {/* Left Section - Toggle and Title */}
        <div className="flex items-center space-x-4">
          {/* Sidebar Toggle Button */}
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              className="p-2.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-center"
            >
              <Menu className="h-6 w-6 text-gray-500 dark:text-gray-400" />
            </button>
          )}
          
          {/* Page Title Section */}
          <div className="flex flex-col justify-center">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white leading-tight">{title}</h1>
            <p className="text-xs text-gray-600 dark:text-gray-300 capitalize leading-tight">{subtitle || currentDate}</p>
          </div>
        </div>

        {/* Search and User Section */}
        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Buscar transacciones, categorías..."
              className="pl-10 pr-4 py-2 w-80 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Session Indicator */}
          <SessionIndicator compact={true} showInHeader={true} />

          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <button 
              onClick={handleNotificationToggle}
              className="relative p-2 text-gray-400 hover:text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </button>

            <NotificationDropdown
              isOpen={isNotificationOpen}
              onClose={() => setIsNotificationOpen(false)}
              notifications={notifications}
              onMarkAsRead={markAsRead}
              onMarkAllAsRead={markAllAsRead}
              onDeleteNotification={deleteNotification}
            />
          </div>

          {/* User Menu */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={handleDropdownToggle}
              className="flex items-center space-x-3 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 hover:bg-gray-100 dark:bg-gray-700 transition-colors cursor-pointer"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.name}</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(user?.role || '')}`}>
                  {getRoleDisplayName(user?.role || '')}
                </span>
              </div>
              <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
                {/* User Info Header */}
                <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">
                        {user?.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{user?.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{user?.email}</p>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mt-1 ${getRoleColor(user?.role || '')}`}>
                        {getRoleDisplayName(user?.role || '')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="py-2">
                  <button
                    onClick={() => handleMenuItemClick('profile')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                  >
                    <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Mi Perfil</span>
                  </button>

                  <button
                    onClick={() => handleMenuItemClick('settings')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                  >
                    <Settings className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Configuración</span>
                  </button>

                  {user?.role === 'administrador' && (
                    <button
                      onClick={() => handleMenuItemClick('admin')}
                      className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                    >
                      <Shield className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Panel de Admin</span>
                    </button>
                  )}

                  <button
                    onClick={() => handleMenuItemClick('theme')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                  >
                    {isDarkMode ? (
                      <Sun className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    ) : (
                      <Moon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    )}
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {isDarkMode ? 'Tema Claro' : 'Tema Oscuro'}
                    </span>
                  </button>

                  <button
                    onClick={() => handleMenuItemClick('help')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-3"
                  >
                    <HelpCircle className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Ayuda y Soporte</span>
                  </button>
                </div>

                {/* Session Info */}
                <div className="border-t border-gray-100 px-4 py-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    <p>Última sesión: {new Date().toLocaleString('es-CO')}</p>
                    <p>IP: 192.168.1.100</p>
                  </div>
                </div>

                {/* Logout */}
                <div className="border-t border-gray-100 pt-2">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 hover:bg-red-50 transition-colors flex items-center space-x-3 text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    <span className="text-sm font-medium">Cerrar Sesión</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
