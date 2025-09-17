/**
 * Hook personalizado para usar WebSocket en componentes React
 * Facilita la integración de actualizaciones en tiempo real en los dashboards
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { websocketService, WebSocketMessage } from '../services/websocketService';

interface UseWebSocketOptions {
  onTransactionUpdate?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  autoReconnect?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionState: string;
  lastMessage: WebSocketMessage | null;
  sendPing: () => void;
  reconnect: () => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('DISCONNECTED');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  // Referencias para evitar re-creación de callbacks
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Actualizar estado de conexión
  const updateConnectionState = useCallback(() => {
    const state = websocketService.getConnectionState();
    const connected = websocketService.isConnected();
    
    setConnectionState(state);
    setIsConnected(connected);
  }, []);

  // Manejar mensajes recibidos
  const handleMessage = useCallback((message: WebSocketMessage) => {
    setLastMessage(message);
    
    // Ejecutar callback específico para actualizaciones/creaciones de transacciones
    if ((message.type === 'transaccion_updated' || 
         message.type === 'transaction_update' || 
         message.type === 'transaccion_created') && 
        optionsRef.current.onTransactionUpdate) {
      optionsRef.current.onTransactionUpdate(message);
    }
  }, []);

  // Manejar conexión establecida
  const handleConnect = useCallback(() => {
    updateConnectionState();
    if (optionsRef.current.onConnect) {
      optionsRef.current.onConnect();
    }
  }, [updateConnectionState]);

  // Manejar desconexión
  const handleDisconnect = useCallback(() => {
    updateConnectionState();
    if (optionsRef.current.onDisconnect) {
      optionsRef.current.onDisconnect();
    }
  }, [updateConnectionState]);

  // Enviar ping
  const sendPing = useCallback(() => {
    websocketService.ping();
  }, []);

  // Reconectar
  const reconnect = useCallback(() => {
    websocketService.reconnect();
  }, []);

  // Configurar listeners al montar el componente
  useEffect(() => {
    // Registrar callbacks
    const unsubscribeMessage = websocketService.onMessage(handleMessage);
    const unsubscribeConnect = websocketService.onConnect(handleConnect);
    const unsubscribeDisconnect = websocketService.onDisconnect(handleDisconnect);
    
    // Actualizar estado inicial
    updateConnectionState();

    // Cleanup al desmontar
    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
    };
  }, [handleMessage, handleConnect, handleDisconnect, updateConnectionState]);

  return {
    isConnected,
    connectionState,
    lastMessage,
    sendPing,
    reconnect
  };
};

/**
 * Hook especializado para dashboards que necesitan actualizarse automáticamente
 */
export const useDashboardWebSocket = (area: 'tesoreria' | 'pagaduria', onDataUpdate: () => void) => {
  const [updateCount, setUpdateCount] = useState(0);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date | null>(null);

  const { isConnected, connectionState, lastMessage } = useWebSocket({
    onTransactionUpdate: (message: WebSocketMessage) => {
      console.log(`🔄 [${area.toUpperCase()}] Actualización recibida:`, message);
      
      // Actualizar contador y timestamp
      setUpdateCount(prev => prev + 1);
      setLastUpdateTime(new Date());
      
      // Ejecutar callback de actualización de datos
      if (onDataUpdate) {
        // Pequeño delay para asegurar que el backend terminó de procesar
        setTimeout(() => {
          onDataUpdate();
        }, 500);
      }
      
      // Mostrar notificación visual
      showUpdateNotification(message, area);
    },
    onConnect: () => {
      console.log(`✅ [${area.toUpperCase()}] WebSocket conectado`);
    },
    onDisconnect: () => {
      console.log(`❌ [${area.toUpperCase()}] WebSocket desconectado`);
    }
  });

  return {
    isConnected,
    connectionState,
    lastMessage,
    updateCount,
    lastUpdateTime
  };
};

/**
 * Mostrar notificación visual de actualización
 */
function showUpdateNotification(message: WebSocketMessage, _area: string): void {
  // Crear elemento de notificación
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transform transition-all duration-300';
  notification.style.transform = 'translateX(100%)';
  
  const dependenciasText = message.total_dependencias_actualizadas 
    ? ` (${message.total_dependencias_actualizadas} actualizaciones)`
    : '';
  
  notification.innerHTML = `
    <div class="flex items-center space-x-2">
      <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
      <span class="text-sm font-medium">
        Datos actualizados automáticamente${dependenciasText}
      </span>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Animar entrada
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Animar salida y remover
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}
