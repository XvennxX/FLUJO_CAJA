/**
 * Servicio WebSocket para actualizaciones en tiempo real
 * Conecta con el backend para recibir notificaciones automáticas cuando se modifican transacciones
 */

export interface WebSocketMessage {
  type: string;
  transaccion_id?: number;
  concepto_id?: number;
  area?: string;
  fecha?: string;
  cuenta_id?: number;
  monto_nuevo?: number;
  total_dependencias_actualizadas?: number;
  message?: string;
  user_id?: number;
  timestamp?: string;
}

export interface WebSocketStats {
  total_connections: number;
  registered_users: number;
  anonymous_connections: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000; // 3 segundos
  private isConnecting = false;
  
  // Callbacks para diferentes tipos de eventos
  private onMessageCallbacks: ((message: WebSocketMessage) => void)[] = [];
  private onConnectCallbacks: (() => void)[] = [];
  private onDisconnectCallbacks: (() => void)[] = [];
  private onErrorCallbacks: ((error: Event) => void)[] = [];

  constructor() {
    this.connect();
  }

  /**
   * Establecer conexión WebSocket con el backend
   */
  private connect(): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;
    console.log('🔗 Conectando a WebSocket...');

    try {
      // URL del WebSocket (ajustar según tu configuración)
      const wsUrl = 'ws://localhost:8000/api/v1/api/transacciones-flujo-caja/ws';
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ Conexión WebSocket establecida');
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        
        // Enviar ping inicial
        this.sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString()
        });

        // Notificar callbacks de conexión
        this.onConnectCallbacks.forEach(callback => callback());
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 Mensaje WebSocket recibido:', message);
          
          this.handleMessage(message);
        } catch (error) {
          console.error('❌ Error parseando mensaje WebSocket:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔌 Conexión WebSocket cerrada:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;

        // Notificar callbacks de desconexión
        this.onDisconnectCallbacks.forEach(callback => callback());

        // Intentar reconectar si no fue un cierre manual
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
        this.isConnecting = false;
        
        // Notificar callbacks de error
        this.onErrorCallbacks.forEach(callback => callback(error));
      };

    } catch (error) {
      console.error('❌ Error creando WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  /**
   * Programar reconexión automática
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Máximo número de intentos de reconexión alcanzado');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * this.reconnectAttempts;
    
    console.log(`🔄 Intentando reconectar en ${delay/1000} segundos... (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Manejar mensajes recibidos del WebSocket
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'connection_established':
        console.log('🎉 Conexión establecida:', message.message);
        break;
        
      case 'pong':
        console.log('🏓 Pong recibido - conexión activa');
        break;
        
      case 'transaccion_updated':
        console.log('🔄 Transacción actualizada:', {
          id: message.transaccion_id,
          area: message.area,
          dependencias: message.total_dependencias_actualizadas
        });
        break;
        
      default:
        console.log('📝 Mensaje desconocido:', message.type);
    }

    // Notificar a todos los callbacks registrados
    this.onMessageCallbacks.forEach(callback => {
      try {
        callback(message);
      } catch (error) {
        console.error('❌ Error en callback de mensaje:', error);
      }
    });
  }

  /**
   * Enviar mensaje al servidor WebSocket
   */
  private sendMessage(message: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('❌ Error enviando mensaje:', error);
        return false;
      }
    }
    
    console.warn('⚠️ WebSocket no está conectado');
    return false;
  }

  /**
   * Registrar callback para mensajes recibidos
   */
  onMessage(callback: (message: WebSocketMessage) => void): () => void {
    this.onMessageCallbacks.push(callback);
    
    // Retornar función para des-registrar el callback
    return () => {
      const index = this.onMessageCallbacks.indexOf(callback);
      if (index > -1) {
        this.onMessageCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Registrar callback para conexión establecida
   */
  onConnect(callback: () => void): () => void {
    this.onConnectCallbacks.push(callback);
    
    return () => {
      const index = this.onConnectCallbacks.indexOf(callback);
      if (index > -1) {
        this.onConnectCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Registrar callback para desconexión
   */
  onDisconnect(callback: () => void): () => void {
    this.onDisconnectCallbacks.push(callback);
    
    return () => {
      const index = this.onDisconnectCallbacks.indexOf(callback);
      if (index > -1) {
        this.onDisconnectCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Registrar callback para errores
   */
  onError(callback: (error: Event) => void): () => void {
    this.onErrorCallbacks.push(callback);
    
    return () => {
      const index = this.onErrorCallbacks.indexOf(callback);
      if (index > -1) {
        this.onErrorCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Enviar ping al servidor
   */
  ping(): boolean {
    return this.sendMessage({
      type: 'ping',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Obtener estado de la conexión
   */
  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'CONNECTED';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'DISCONNECTED';
      default: return 'UNKNOWN';
    }
  }

  /**
   * Verificar si está conectado
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Cerrar conexión manualmente
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  /**
   * Reconectar manualmente
   */
  reconnect(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }
}

// Instancia singleton del servicio WebSocket
export const websocketService = new WebSocketService();