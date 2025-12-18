import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { User } from '../types';
import { registerLogoutCallback } from '../utils/apiInterceptor';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
  loginError: string | null;
  clearLoginError: () => void;
  refreshToken: () => Promise<boolean>;
}

// Configuración de renovación de token
const TOKEN_CONFIG = {
  EXPIRE_TIME: 60 * 60 * 1000, // 1 hora en ms (debe coincidir con backend)
  REFRESH_BEFORE: 5 * 60 * 1000, // Renovar 5 minutos antes de expirar
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// URL base de la API
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [tokenExpireTime, setTokenExpireTime] = useState<number | null>(null);
  const refreshTimerRef = useRef<number | null>(null);

  // Función para mapear roles de español a códigos del sistema
  const mapRoleToSystemCode = (roleFromDB: string): 'administrador' | 'tesoreria' | 'pagaduria' | 'mesa_dinero' => {
    switch (roleFromDB.toLowerCase()) {
      case 'administrador':
        return 'administrador';
      case 'tesorería':
      case 'tesoreria':
        return 'tesoreria';
      case 'pagaduría':
      case 'pagaduria':
        return 'pagaduria';
      case 'mesa de dinero':
      case 'mesa_dinero':
        return 'mesa_dinero';
      default:
        console.warn(`Rol desconocido desde DB: ${roleFromDB}, usando administrador por defecto`);
        return 'administrador';
    }
  };

  const clearLoginError = () => setLoginError(null);

  // Función para renovar el token
  const refreshToken = async (): Promise<boolean> => {
    const currentToken = localStorage.getItem('access_token');
    if (!currentToken) {
      return false;
    }

    try {
      console.log('🔄 Renovando token...');
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        setToken(data.access_token);
        
        // Actualizar tiempo de expiración
        const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
        setTokenExpireTime(expireTime);
        
        console.log('✅ Token renovado exitosamente');
        
        // Programar próxima renovación
        scheduleTokenRefresh(expireTime);
        
        return true;
      } else {
        console.error('❌ Error renovando token, cerrando sesión');
        logout();
        return false;
      }
    } catch (error) {
      console.error('❌ Error en renovación de token:', error);
      logout();
      return false;
    }
  };

  // Programar renovación automática del token
  const scheduleTokenRefresh = (expireTime: number) => {
    // Limpiar timer anterior
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    // Calcular cuándo renovar (10 minutos antes de expirar)
    const refreshTime = expireTime - TOKEN_CONFIG.REFRESH_BEFORE - Date.now();
    
    if (refreshTime > 0) {
      console.log(`⏰ Token se renovará en ${Math.round(refreshTime / 60000)} minutos`);
      refreshTimerRef.current = setTimeout(() => {
        refreshToken();
      }, refreshTime);
    }
  };

  // Validar si el token ha expirado
  const isTokenExpired = (expireTime: number | null): boolean => {
    if (!expireTime) return false;
    return Date.now() >= expireTime;
  };

  useEffect(() => {
    // Verificar si hay un token guardado al cargar la aplicación
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            const mappedRole = mapRoleToSystemCode(userData.rol);
            setUser({
              id: userData.id.toString(),
              name: userData.nombre,
              email: userData.email,
              role: mappedRole,
              estado: userData.estado
            });
            setToken(token);
            
            // Programar renovación del token
            const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
            setTokenExpireTime(expireTime);
            scheduleTokenRefresh(expireTime);
            
            console.log('🔄 AuthContext: token verificado, rol mapeado:', userData.rol, '->', mappedRole);
          } else {
            // Token inválido, limpiar
            localStorage.removeItem('access_token');
            setToken(null);
          }
        } catch (error) {
          console.error('Error verificando autenticación:', error);
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    console.log('🔐 AuthContext login called with:', { email, password: '***' });
    
    // Limpiar error anterior
    setLoginError(null);
    
    // Validaciones básicas
    if (!email || !password) {
      const errorMsg = 'Por favor, completa todos los campos';
      setLoginError(errorMsg);
      return { success: false, error: errorMsg };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      const errorMsg = 'Por favor, ingresa un correo electrónico válido';
      setLoginError(errorMsg);
      return { success: false, error: errorMsg };
    }
    
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Guardar token
        localStorage.setItem('access_token', data.access_token);
        setToken(data.access_token);
        
        // Configurar usuario
        const mappedRole = mapRoleToSystemCode(data.user.rol);
        setUser({
          id: data.user.id.toString(),
          name: data.user.nombre,
          email: data.user.email,
          role: mappedRole,
          estado: data.user.estado
        });
        
        // Programar renovación del token
        const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
        setTokenExpireTime(expireTime);
        scheduleTokenRefresh(expireTime);
        
        console.log('🔄 AuthContext: login exitoso, rol mapeado:', data.user.rol, '->', mappedRole);
        console.log('🔄 AuthContext: login exitoso, isLoading será false');
        setIsLoading(false);
        return { success: true };
      } else {
        console.log('🔄 AuthContext: login falló, isLoading será false');
        setIsLoading(false);
        
        // Establecer error en el contexto
        let errorMessage = '';
        if (response.status === 401) {
          errorMessage = 'Usuario o contraseña incorrectos. Verifica tus credenciales e intenta nuevamente.';
        } else if (response.status === 403) {
          // Usuario inactivo
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || 'Su cuenta ha sido desactivada. Contacte al administrador.';
          } catch {
            errorMessage = 'Su cuenta ha sido desactivada. Contacte al administrador.';
          }
        } else if (response.status === 422) {
          errorMessage = 'Por favor verifica que el email sea válido y todos los campos estén completos.';
        } else if (response.status >= 500) {
          errorMessage = 'Error interno del servidor. Intenta más tarde.';
        } else {
          errorMessage = 'Error desconocido. Intenta nuevamente.';
        }
        
        setLoginError(errorMessage);
        return { 
          success: false, 
          error: errorMessage
        };
      }
    } catch (error) {
      console.log('🔄 AuthContext: error de conexión, isLoading será false');
      setIsLoading(false);
      const errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.';
      setLoginError(errorMessage);
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = () => {
    // Limpiar timer de renovación
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
    
    localStorage.removeItem('access_token');
    setUser(null);
    setToken(null);
    setTokenExpireTime(null);
    
    console.log('🚪 Sesión cerrada correctamente');
  };

  // Registrar callback de logout para el interceptor de API
  useEffect(() => {
    registerLogoutCallback(logout);
    console.log('✅ Callback de logout registrado en el interceptor de API');
  }, []);

  // Limpiar timer al desmontar
  useEffect(() => {
    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading, loginError, clearLoginError, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};