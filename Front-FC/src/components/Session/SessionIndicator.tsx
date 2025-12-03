import React from 'react';
import { Shield, Clock, AlertTriangle, XCircle } from 'lucide-react';
import { useSession } from '../../contexts/SessionContext';

interface SessionIndicatorProps {
  showInHeader?: boolean;
  compact?: boolean;
}

const SessionIndicator: React.FC<SessionIndicatorProps> = ({ 
  showInHeader = false, 
  compact = false 
}) => {
  const { sessionState, timeRemaining, getSessionStatus } = useSession();
  
  const status = getSessionStatus();
  
  // Obtener color y ícono según estado
  const getStateConfig = () => {
    switch (sessionState) {
      case 'ACTIVE':
        return {
          color: 'text-green-600 dark:text-green-400',
          bgColor: 'bg-green-100 dark:bg-green-900/20',
          borderColor: 'border-green-300 dark:border-green-600',
          icon: Shield,
          label: 'Sesión Activa',
          dotColor: 'bg-green-500'
        };
      case 'INACTIVE':
        return {
          color: 'text-blue-600 dark:text-blue-400',
          bgColor: 'bg-blue-100 dark:bg-blue-900/20',
          borderColor: 'border-blue-300 dark:border-blue-600',
          icon: Clock,
          label: 'Inactiva',
          dotColor: 'bg-blue-500'
        };
      case 'WARNING':
        return {
          color: 'text-yellow-600 dark:text-yellow-400',
          bgColor: 'bg-yellow-100 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-300 dark:border-yellow-600',
          icon: AlertTriangle,
          label: 'Aviso',
          dotColor: 'bg-yellow-500 animate-pulse'
        };
      case 'CRITICAL':
        return {
          color: 'text-red-600 dark:text-red-400',
          bgColor: 'bg-red-100 dark:bg-red-900/20',
          borderColor: 'border-red-300 dark:border-red-600',
          icon: XCircle,
          label: 'Crítico',
          dotColor: 'bg-red-500 animate-pulse'
        };
      case 'EXPIRED':
        return {
          color: 'text-gray-600 dark:text-gray-400',
          bgColor: 'bg-gray-100 dark:bg-gray-900/20',
          borderColor: 'border-gray-300 dark:border-gray-600',
          icon: XCircle,
          label: 'Expirada',
          dotColor: 'bg-gray-500'
        };
      default:
        return {
          color: 'text-gray-600 dark:text-gray-400',
          bgColor: 'bg-gray-100 dark:bg-gray-900/20',
          borderColor: 'border-gray-300 dark:border-gray-600',
          icon: Shield,
          label: 'Desconocido',
          dotColor: 'bg-gray-500'
        };
    }
  };

  const config = getStateConfig();
  const IconComponent = config.icon;

  // Formato compacto para header
  if (compact) {
    return (
      <div 
        className={`flex items-center gap-2 px-2 py-1 rounded-md ${config.bgColor} ${config.borderColor} border`}
        title={`Sesión: ${config.label} - ${status.formattedTime} restantes`}
      >
        <div className={`w-2 h-2 rounded-full ${config.dotColor}`} />
        {!showInHeader && (
          <span className={`text-xs font-medium ${config.color}`}>
            {config.label}
          </span>
        )}
      </div>
    );
  }

  // Formato completo
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg ${config.bgColor} ${config.borderColor} border`}>
      <IconComponent className={`w-5 h-5 ${config.color}`} />
      
      <div className="flex-1">
        <div className={`text-sm font-medium ${config.color}`}>
          {config.label}
        </div>
        
        {sessionState !== 'ACTIVE' && sessionState !== 'EXPIRED' && (
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Tiempo restante: {status.formattedTime}
          </div>
        )}
        
        {sessionState === 'ACTIVE' && (
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Sesión mantenida por actividad
          </div>
        )}
      </div>
      
      {(sessionState === 'WARNING' || sessionState === 'CRITICAL') && (
        <div className={`w-2 h-2 rounded-full ${config.dotColor}`} />
      )}
    </div>
  );
};

export default SessionIndicator;