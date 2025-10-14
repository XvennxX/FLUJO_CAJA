import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth } from './AuthContext';

// Configuración de sesión (sincronizada con backend)
const SESSION_CONFIG = {
  INACTIVITY_TIMEOUT: 60 * 60 * 1000, // 1 hora en milliseconds
  TOKEN_LIFETIME: 120 * 60 * 1000, // 2 horas - debe coincidir con backend
  WARNING_TIMES: [
    { time: 50 * 60 * 1000, message: '10 minutos', type: 'warning' as const },
    { time: 58 * 60 * 1000, message: '2 minutos', type: 'critical' as const }
  ],
  ACTIVE_EVENTS: [
    'dashboard_edit',
    'page_navigation',
    'filter_change',
    'date_change',
    'form_interaction',
    'button_click',
    'menu_interaction',
    'data_save'
  ]
};

type SessionState = 'ACTIVE' | 'INACTIVE' | 'WARNING' | 'CRITICAL' | 'EXPIRED';

type ActivityType = typeof SESSION_CONFIG.ACTIVE_EVENTS[number];

interface SessionWarning {
  timeRemaining: string;
  type: 'warning' | 'critical';
  show: boolean;
}

interface SessionContextType {
  sessionState: SessionState;
  timeRemaining: number;
  warning: SessionWarning;
  isActive: boolean;
  recordActivity: (activityType: ActivityType, details?: string) => void;
  extendSession: () => void;
  dismissWarning: () => void;
  getSessionStatus: () => {
    state: SessionState;
    timeRemaining: number;
    formattedTime: string;
  };
}

const SessionContext = createContext<SessionContextType | null>(null);

interface SessionProviderProps {
  children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const { logout, user } = useAuth();
  
  // Estados principales
  const [sessionState, setSessionState] = useState<SessionState>('ACTIVE');
  const [lastActivity, setLastActivity] = useState<number>(Date.now());
  const [timeRemaining, setTimeRemaining] = useState<number>(SESSION_CONFIG.INACTIVITY_TIMEOUT);
  const [warning, setWarning] = useState<SessionWarning>({
    timeRemaining: '',
    type: 'warning',
    show: false
  });

  // Formatear tiempo restante
  const formatTimeRemaining = useCallback((milliseconds: number): string => {
    const minutes = Math.floor(milliseconds / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  }, []);

  // Registrar actividad del usuario
  const recordActivity = useCallback((activityType: ActivityType, details?: string) => {
    const now = Date.now();
    
    console.log('👤 Actividad registrada:', {
      tipo: activityType,
      detalles: details,
      timestamp: new Date(now).toLocaleString(),
      usuario: user?.name
    });

    setLastActivity(now);
    setSessionState('ACTIVE');
    setTimeRemaining(SESSION_CONFIG.INACTIVITY_TIMEOUT);
    
    // Ocultar warnings si están activos
    if (warning.show) {
      setWarning(prev => ({ ...prev, show: false }));
    }

    // Log para auditoria (opcional)
    try {
      localStorage.setItem('last_user_activity', JSON.stringify({
        type: activityType,
        details: details,
        timestamp: now,
        user: user?.id
      }));
    } catch (error) {
      console.warn('No se pudo guardar actividad en localStorage:', error);
    }
  }, [user, warning.show]);

  // Extender sesión manualmente
  const extendSession = useCallback(() => {
    console.log('🔄 Sesión extendida manualmente');
    recordActivity('manual_extension', 'Usuario extendió sesión desde aviso');
  }, [recordActivity]);

  // Descartar warning
  const dismissWarning = useCallback(() => {
    setWarning(prev => ({ ...prev, show: false }));
  }, []);

  // Obtener estado de sesión
  const getSessionStatus = useCallback(() => {
    return {
      state: sessionState,
      timeRemaining: timeRemaining,
      formattedTime: formatTimeRemaining(timeRemaining)
    };
  }, [sessionState, timeRemaining, formatTimeRemaining]);

  // Timer principal de sesión
  useEffect(() => {
    if (!user) return; // No ejecutar si no hay usuario

    const interval = setInterval(() => {
      const now = Date.now();
      const timeSinceLastActivity = now - lastActivity;
      const remaining = SESSION_CONFIG.INACTIVITY_TIMEOUT - timeSinceLastActivity;

      setTimeRemaining(remaining);

      if (remaining <= 0) {
        // Sesión expirada
        console.log('⏰ Sesión expirada por inactividad');
        setSessionState('EXPIRED');
        clearInterval(interval);
        
        // Cerrar sesión después de un breve delay
        setTimeout(() => {
          logout();
        }, 1000);
        return;
      }

      // Verificar si debe mostrar warnings
      const warningConfig = SESSION_CONFIG.WARNING_TIMES.find(w => 
        remaining <= (SESSION_CONFIG.INACTIVITY_TIMEOUT - w.time) && 
        remaining > (SESSION_CONFIG.INACTIVITY_TIMEOUT - w.time) - 5000 // 5 segundos de ventana
      );

      if (warningConfig && !warning.show) {
        console.log(`⚠️ Mostrando aviso: ${warningConfig.message} restantes`);
        setSessionState(warningConfig.type === 'critical' ? 'CRITICAL' : 'WARNING');
        setWarning({
          timeRemaining: warningConfig.message,
          type: warningConfig.type,
          show: true
        });
      }

      // Actualizar estado basado en tiempo restante
      if (remaining > (SESSION_CONFIG.INACTIVITY_TIMEOUT - SESSION_CONFIG.WARNING_TIMES[0].time)) {
        if (sessionState !== 'ACTIVE' && !warning.show) {
          setSessionState('ACTIVE');
        }
      } else if (remaining > (SESSION_CONFIG.INACTIVITY_TIMEOUT - SESSION_CONFIG.WARNING_TIMES[1].time)) {
        if (sessionState !== 'WARNING' && sessionState !== 'ACTIVE') {
          setSessionState('INACTIVE');
        }
      }
    }, 1000); // Verificar cada segundo

    return () => clearInterval(interval);
  }, [lastActivity, user, logout, sessionState, warning.show]);

  // Auto-registro de actividad en eventos globales
  useEffect(() => {
    if (!user) return;

    const handleGlobalActivity = (event: Event) => {
      // Solo registrar ciertos tipos de eventos para evitar spam
      if (event.target && (event.target as HTMLElement).closest('.session-activity')) {
        recordActivity('form_interaction', `Interacción con elemento del formulario`);
      }
    };

    // Eventos globales de actividad
    const events = ['keydown', 'click'];
    events.forEach(eventType => {
      document.addEventListener(eventType, handleGlobalActivity, { passive: true });
    });

    return () => {
      events.forEach(eventType => {
        document.removeEventListener(eventType, handleGlobalActivity);
      });
    };
  }, [user, recordActivity]);

  // Estado derivado
  const isActive = sessionState === 'ACTIVE';

  const contextValue: SessionContextType = {
    sessionState,
    timeRemaining,
    warning,
    isActive,
    recordActivity,
    extendSession,
    dismissWarning,
    getSessionStatus
  };

  return (
    <SessionContext.Provider value={contextValue}>
      {children}
    </SessionContext.Provider>
  );
};

// Hook personalizado para usar el contexto
export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession debe usarse dentro de SessionProvider');
  }
  return context;
};

// Hook para registrar actividad fácilmente
export const useActivityTracker = () => {
  const { recordActivity } = useSession();
  
  return {
    trackPageNavigation: (page: string) => recordActivity('page_navigation', `Navegó a ${page}`),
    trackDashboardEdit: (concepto: string, valor: number) => recordActivity('dashboard_edit', `Editó ${concepto}: ${valor}`),
    trackFilterChange: (filter: string, value: string) => recordActivity('filter_change', `Filtro ${filter}: ${value}`),
    trackDateChange: (date: string) => recordActivity('date_change', `Cambió fecha a ${date}`),
    trackDataSave: (type: string) => recordActivity('data_save', `Guardó ${type}`),
    trackButtonClick: (button: string) => recordActivity('button_click', `Clic en ${button}`),
    trackMenuInteraction: (menu: string) => recordActivity('menu_interaction', `Interacción con ${menu}`)
  };
};