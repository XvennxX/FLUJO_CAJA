import { useState, useCallback } from 'react';

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error' | 'transaction';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  priority: 'high' | 'medium' | 'low';
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'transaction',
      title: 'Nueva transacción registrada',
      message: 'Se ha registrado un pago de $2,500,000 en BANCO DAVIVIENDA',
      timestamp: 'hace 5 minutos',
      isRead: false,
      priority: 'medium'
    },
    {
      id: '2',
      type: 'warning',
      title: 'Saldo bajo detectado',
      message: 'La cuenta CAPITALIZADORA tiene un saldo inferior al mínimo establecido',
      timestamp: 'hace 15 minutos',
      isRead: false,
      priority: 'high'
    },
    {
      id: '3',
      type: 'success',
      title: 'Conciliación completada',
      message: 'La conciliación bancaria del mes se ha completado exitosamente',
      timestamp: 'hace 1 hora',
      isRead: true,
      priority: 'low'
    },
    {
      id: '4',
      type: 'info',
      title: 'Actualización del sistema',
      message: 'Nueva versión del SIFCO disponible con mejoras de seguridad',
      timestamp: 'hace 2 horas',
      isRead: false,
      priority: 'medium'
    },
    {
      id: '5',
      type: 'error',
      title: 'Error en conexión bancaria',
      message: 'No se pudo conectar con CITIBANK. Reintentando automáticamente...',
      timestamp: 'hace 3 horas',
      isRead: true,
      priority: 'high'
    },
    {
      id: '6',
      type: 'transaction',
      title: 'Transferencia completada',
      message: 'Transferencia de $1,200,000 entre cuentas BOLÍVAR procesada',
      timestamp: 'hace 4 horas',
      isRead: false,
      priority: 'low'
    },
    {
      id: '7',
      type: 'warning',
      title: 'Límite de transacciones alcanzado',
      message: 'La cuenta COMERCIALES ha alcanzado el 90% del límite diario',
      timestamp: 'hace 6 horas',
      isRead: true,
      priority: 'medium'
    },
    {
      id: '8',
      type: 'info',
      title: 'Nuevo usuario registrado',
      message: 'Se ha agregado un nuevo usuario al sistema con rol de Tesorería',
      timestamp: 'hace 8 horas',
      isRead: false,
      priority: 'low'
    }
  ]);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => prev.map(notification => 
      notification.id === id ? { ...notification, isRead: true } : notification
    ));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(notification => ({ ...notification, isRead: true })));
  }, []);

  const deleteNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
    };
    setNotifications(prev => [newNotification, ...prev]);
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.isRead).length;
  const highPriorityUnread = notifications.filter(n => !n.isRead && n.priority === 'high').length;

  return {
    notifications,
    unreadCount,
    highPriorityUnread,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification,
    clearAllNotifications
  };
};
