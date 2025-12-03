/**
 * Configuración centralizada de API
 * 
 * Este archivo centraliza todas las URLs y configuraciones de API
 * para facilitar el cambio entre ambientes (dev, staging, production)
 */

const config = {
  // URL base del API
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Versión del API
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  
  // WebSocket URL
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  
  // Ambiente actual
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  
  // Flags de ambiente
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  
  // Configuración de aplicación
  appName: import.meta.env.VITE_APP_NAME || 'SIFCO - Sistema de Flujo de Caja',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
};

// URLs construidas
export const API_BASE_URL = `${config.apiBaseUrl}/api/${config.apiVersion}`;
export const WS_URL = config.wsUrl;

// Endpoints específicos (para facilitar su uso)
export const API_ENDPOINTS = {
  // Autenticación
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    logout: `${API_BASE_URL}/auth/logout`,
    refresh: `${API_BASE_URL}/auth/refresh`,
  },
  
  // Usuarios
  users: {
    list: `${API_BASE_URL}/users`,
    create: `${API_BASE_URL}/users`,
    get: (id: number) => `${API_BASE_URL}/users/${id}`,
    update: (id: number) => `${API_BASE_URL}/users/${id}`,
    delete: (id: number) => `${API_BASE_URL}/users/${id}`,
  },
  
  // Empresas
  companies: {
    list: `${API_BASE_URL}/companies/test`,
    create: `${API_BASE_URL}/companies/test`,
    get: (id: number) => `${API_BASE_URL}/companies/test/${id}`,
    update: (id: number) => `${API_BASE_URL}/companies/test/${id}`,
    delete: (id: number) => `${API_BASE_URL}/companies/test/${id}`,
  },
  
  // Cuentas bancarias
  bankAccounts: {
    byCompany: (companyId: number) => `${API_BASE_URL}/bank-accounts/test/companies/${companyId}`,
    get: (id: number) => `${API_BASE_URL}/bank-accounts/${id}`,
    update: (id: number) => `${API_BASE_URL}/bank-accounts/test/${id}`,
    banks: `${API_BASE_URL}/bank-accounts/test/banks`,
  },
  
  // Transacciones
  transactions: {
    byDate: (fecha: string, area: string) => `${API_BASE_URL}/api/transacciones-flujo-caja/fecha/${fecha}?area=${area}`,
    create: `${API_BASE_URL}/api/transacciones-flujo-caja`,
    quickUpdate: (id: number) => `${API_BASE_URL}/api/transacciones-flujo-caja/${id}/quick`,
    delete: (id: number) => `${API_BASE_URL}/api/transacciones-flujo-caja/${id}`,
  },
  
  // TRM
  trm: {
    byDate: (date: string) => `${API_BASE_URL}/trm/by-date/${date}`,
    range: (fechaFin: string, limit: number = 1) => `${API_BASE_URL}/trm/range?fecha_fin=${fechaFin}&limit=${limit}`,
    current: `${API_BASE_URL}/trm/current`,
  },
  
  // Días hábiles
  diasHabiles: `${API_BASE_URL}/dias-habiles`,
  
  // Diferencia de saldos
  diferenciaSaldos: {
    calcular: `${API_BASE_URL}/diferencia-saldos/calcular-diferencia-saldos`,
    verificar: (fecha: string) => `${API_BASE_URL}/diferencia-saldos/verificar-necesidad/${fecha}`,
  },
  
  // Saldo inicial
  saldoInicial: API_BASE_URL,
};

// Configuración de headers comunes
export const getAuthHeaders = (includeContentType: boolean = true) => {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {};
  
  if (includeContentType) {
    headers['Content-Type'] = 'application/json';
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Helper para hacer peticiones con manejo de errores
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const headers = {
    ...getAuthHeaders(),
    ...options.headers,
  };
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
};

// Logging condicional (solo en desarrollo)
export const devLog = (...args: any[]) => {
  if (config.isDevelopment) {
    console.log(...args);
  }
};

export const devError = (...args: any[]) => {
  if (config.isDevelopment) {
    console.error(...args);
  }
};

export const devWarn = (...args: any[]) => {
  if (config.isDevelopment) {
    console.warn(...args);
  }
};

// Exportar configuración por defecto
export default config;
