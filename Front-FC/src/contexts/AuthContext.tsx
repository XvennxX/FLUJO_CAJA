import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const mockUsers: User[] = [
  {
    id: '1',
    name: 'Ana García',
    email: 'admin@bolivar.com',
    role: 'administrador',
  },
  {
    id: '2',
    name: 'Carlos Rodríguez',
    email: 'tesoreria@bolivar.com',
    role: 'tesoreria',
  },
  {
    id: '3',
    name: 'María Fernández',
    email: 'pagaduria@bolivar.com',
    role: 'pagaduria',
  },
  {
    id: '4',
    name: 'Roberto Silva',
    email: 'mesadinero@bolivar.com',
    role: 'mesa_dinero',
  }
];

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simular verificación de sesión existente
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    
    // Simular autenticación
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verificar credenciales
    const credentials = [
      { email: 'admin@bolivar.com', password: 'admin123' },
      { email: 'tesoreria@bolivar.com', password: 'tesoreria123' },
      { email: 'pagaduria@bolivar.com', password: 'pagaduria123' },
      { email: 'mesadinero@bolivar.com', password: 'mesa123' }
    ];

    const validCredential = credentials.find(
      cred => cred.email === email && cred.password === password
    );

    if (validCredential) {
      const foundUser = mockUsers.find(u => u.email === email);
      if (foundUser) {
        setUser(foundUser);
        localStorage.setItem('user', JSON.stringify(foundUser));
        setIsLoading(false);
        return true;
      }
    }
    
    setIsLoading(false);
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};