import React from 'react';
import { Clock, AlertTriangle, Shield, X } from 'lucide-react';
import { useSession } from '../../contexts/SessionContext';

const SessionWarningModal: React.FC = () => {
  const { warning, sessionState, extendSession, dismissWarning, getSessionStatus } = useSession();
  
  if (!warning.show) return null;

  const status = getSessionStatus();
  
  const getConfig = () => {
    if (warning.type === 'critical') {
      return {
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        borderColor: 'border-red-200 dark:border-red-800',
        textColor: 'text-red-900 dark:text-red-100',
        buttonColor: 'bg-red-600 hover:bg-red-700 text-white',
        icon: AlertTriangle,
        iconColor: 'text-red-600 dark:text-red-400'
      };
    }
    return {
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      borderColor: 'border-yellow-200 dark:border-yellow-800',
      textColor: 'text-yellow-900 dark:text-yellow-100',
      buttonColor: 'bg-yellow-600 hover:bg-yellow-700 text-white',
      icon: Clock,
      iconColor: 'text-yellow-600 dark:text-yellow-400'
    };
  };

  const config = getConfig();
  const IconComponent = config.icon;

  const handleExtend = () => {
    extendSession();
    dismissWarning();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className={`
        w-full max-w-md mx-4 p-6 rounded-xl border-2 shadow-2xl
        ${config.bgColor} ${config.borderColor}
        transform transition-all duration-300 scale-100
      `}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <IconComponent className={`w-6 h-6 ${config.iconColor}`} />
            <h3 className={`text-lg font-bold ${config.textColor}`}>
              {warning.type === 'critical' ? '🚨 Sesión Crítica' : '⚠️ Aviso de Sesión'}
            </h3>
          </div>
          
          {warning.type !== 'critical' && (
            <button
              onClick={dismissWarning}
              className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          )}
        </div>

        {/* Contenido */}
        <div className={`mb-6 ${config.textColor}`}>
          <p className="text-base mb-3">
            {warning.type === 'critical' 
              ? 'Tu sesión está a punto de expirar por inactividad.'
              : 'Tu sesión expirará pronto debido a la inactividad.'
            }
          </p>
          
          <div className="flex items-center gap-2 p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">
              Tiempo restante: {status.formattedTime}
            </span>
          </div>
          
          <p className="text-sm mt-3 opacity-75">
            {warning.type === 'critical'
              ? 'Haz clic en "Mantener Activa" para continuar trabajando o guarda tu progreso.'
              : 'Cualquier actividad en el sistema mantendrá tu sesión activa automáticamente.'
            }
          </p>
        </div>

        {/* Botones */}
        <div className="flex gap-3">
          <button
            onClick={handleExtend}
            className={`
              flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg
              font-medium transition-all duration-200 transform hover:scale-105
              ${config.buttonColor}
            `}
          >
            <Shield className="w-4 h-4" />
            Mantener Activa
          </button>
          
          {warning.type !== 'critical' && (
            <button
              onClick={dismissWarning}
              className="px-4 py-3 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              Entendido
            </button>
          )}
        </div>

        {/* Progress bar visual */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 ${
                warning.type === 'critical' ? 'bg-red-500' : 'bg-yellow-500'
              }`}
              style={{ 
                width: `${Math.max(5, (status.timeRemaining / (60 * 60 * 1000)) * 100)}%` 
              }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0 min</span>
            <span>60 min</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionWarningModal;