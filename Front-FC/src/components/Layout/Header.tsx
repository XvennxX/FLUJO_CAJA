import React from 'react';
import { Search, Bell, ChevronDown } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  title: string;
  subtitle: string;
}

const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  const { user } = useAuth();
  
  const currentDate = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page Title Section */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          <p className="text-sm text-gray-600 capitalize">{subtitle || currentDate}</p>
        </div>

        {/* Search and User Section */}
        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Buscar transacciones, categorías..."
              className="pl-10 pr-4 py-2 w-80 border border-gray-300 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="flex items-center space-x-3 bg-gray-50 rounded-lg px-3 py-2 hover:bg-gray-100 transition-colors cursor-pointer">
            <div className="w-8 h-8 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">
                {user?.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;