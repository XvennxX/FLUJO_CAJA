/**
 * Interceptor Global de API para manejar errores de autenticación
 * 
 * Este módulo intercepta todas las llamadas fetch para:
 * 1. Detectar errores 401 (Unauthorized)
 * 2. Cerrar sesión automáticamente
 * 3. Redirigir al login
 * 4. Sincronizar estado de sesión entre frontend y backend
 */

// Store para callbacks de logout
let logoutCallback: (() => void) | null = null;

/**
 * Registrar función de logout para ser llamada en errores 401
 */
export const registerLogoutCallback = (callback: () => void) => {
  logoutCallback = callback;
};

/**
 * Interceptor de fetch global
 * Envuelve el fetch nativo para capturar y manejar errores 401
 */
const originalFetch = window.fetch;

window.fetch = async (...args) => {
  try {
    const response = await originalFetch(...args);

    // Si recibimos un 401, el token ha expirado o es inválido
    if (response.status === 401) {
      console.error('🚫 Error 401: Token inválido o expirado, cerrando sesión...');
      
      // Mostrar notificación al usuario
      showSessionExpiredNotification();
      
      // Ejecutar logout si está registrado
      if (logoutCallback) {
        setTimeout(() => {
          logoutCallback?.();
        }, 1500); // Dar tiempo para que el usuario vea la notificación
      }
    }

    return response;
  } catch (error) {
    // Propagar el error original
    throw error;
  }
};

/**
 * Mostrar notificación de sesión expirada
 */
const showSessionExpiredNotification = () => {
  // Buscar si ya existe una notificación
  const existingNotification = document.getElementById('session-expired-notification');
  if (existingNotification) {
    return; // No mostrar duplicados
  }

  const notification = document.createElement('div');
  notification.id = 'session-expired-notification';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(220, 38, 38, 0.3);
    z-index: 10000;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    font-weight: 500;
    animation: slideInRight 0.3s ease-out;
  `;

  notification.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
      <line x1="12" y1="9" x2="12" y2="13"></line>
      <line x1="12" y1="17" x2="12.01" y2="17"></line>
    </svg>
    <div>
      <div style="font-weight: 600; margin-bottom: 2px;">Sesión Expirada</div>
      <div style="font-size: 12px; opacity: 0.9;">Tu sesión ha caducado. Redirigiendo al login...</div>
    </div>
  `;

  // Agregar animación CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInRight {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `;
  document.head.appendChild(style);

  document.body.appendChild(notification);

  // Auto-remover después de 3 segundos
  setTimeout(() => {
    notification.style.animation = 'slideInRight 0.3s ease-out reverse';
    setTimeout(() => {
      notification.remove();
      style.remove();
    }, 300);
  }, 2000);
};

// Log de inicialización
console.log('✅ Interceptor de API inicializado para detectar errores de autenticación');
