import React from 'react';
import { CheckCircle, AlertTriangle, Clock, X } from 'lucide-react';
import { useSession } from '../../contexts/SessionContext';

const SessionToast: React.FC = () => {
  const { sessionState, warning, getSessionStatus, dismissWarning } = useSession();
  
  // Solo mostrar toast para warnings tipo 'warning' (no críticos)
  if (!warning.show || warning.type === 'critical') return null;
  
  const status = getSessionStatus();
  
  return (
    <div className="fixed top-4 right-4 z-40 max-w-sm">
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg shadow-lg p-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
        
        <div className="flex-1">
          <div className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            Sesión expirará en {warning.timeRemaining}
          </div>
          <div className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
            Cualquier actividad mantendrá tu sesión activa
          </div>
          
          {/* Barra de progreso mini */}
          <div className="w-full bg-yellow-200 dark:bg-yellow-800 rounded-full h-1 mt-2">
            <div 
              className="bg-yellow-500 h-1 rounded-full transition-all duration-1000"
              style={{ 
                width: `${Math.max(5, (status.timeRemaining / (60 * 60 * 1000)) * 100)}%` 
              }}
            />
          </div>
        </div>
        
        <button
          onClick={dismissWarning}
          className="text-yellow-600 dark:text-yellow-400 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default SessionToast;