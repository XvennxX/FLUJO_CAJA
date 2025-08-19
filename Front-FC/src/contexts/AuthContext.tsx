import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
  loginError: string | null;
  clearLoginError: () => void;
}

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
    localStorage.removeItem('access_token');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading, loginError, clearLoginError }}>
      {children}
    </AuthContext.Provider>
  );
};