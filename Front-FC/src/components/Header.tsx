import React from 'react';
import { TrendingUp, Calendar } from 'lucide-react';

const Header: React.FC = () => {
  const currentDate = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl shadow-lg">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">CashFlow Pro</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">Gestión inteligente de flujo de caja</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <Calendar className="h-5 w-5" />
            <span className="text-sm font-medium capitalize">{currentDate}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
