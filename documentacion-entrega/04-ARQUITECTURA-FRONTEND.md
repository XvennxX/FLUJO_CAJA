# ARQUITECTURA FRONTEND - SISTEMA DE FLUJO DE CAJA

## INFORMACIÓN GENERAL

**Proyecto**: Sistema de Flujo de Caja - Bolívar  
**Framework**: React 18.3.1 con TypeScript  
**Build Tool**: Vite 5.4.2  
**Styling**: Tailwind CSS 3.4.1  
**Iconografía**: Lucide React 0.344.0  
**Gráficos**: Recharts 3.1.1  
**Fecha de Documentación**: 18 de Diciembre de 2025  

---

## 🏗️ ARQUITECTURA GENERAL

### Patrón de Diseño

El frontend sigue una **arquitectura basada en componentes** con React y TypeScript, utilizando **Context API** para el estado global y **hooks personalizados** para la lógica reutilizable.

```
┌─────────────────┐
│   App Layer     │ ← Aplicación principal y routing
├─────────────────┤
│ Context Layer   │ ← Estado global (Auth, Theme, Session)
├─────────────────┤
│Component Layer  │ ← Componentes React organizados
├─────────────────┤
│ Services Layer  │ ← API calls y lógica de negocio
├─────────────────┤
│  Utils Layer    │ ← Utilidades y helpers
└─────────────────┘
```

### Estructura de Directorios

```
Front-FC/src/
├── components/                 # Componentes React organizados
│   ├── Layout/                # Componentes de estructura
│   │   ├── Header.tsx        # Encabezado principal
│   │   ├── Sidebar.tsx       # Menú lateral con roles
│   │   └── ToastContainer.tsx # Sistema de notificaciones
│   ├── Pages/                 # Páginas principales de la app
│   │   ├── Dashboard.tsx     # Dashboard principal
│   │   ├── DashboardAdmin.tsx # Panel administrativo
│   │   ├── DashboardMesa.tsx  # Dashboard Mesa de Dinero
│   │   ├── DashboardPagaduria.tsx # Dashboard Pagaduría
│   │   ├── DashboardTesoreria.tsx # Dashboard Tesorería
│   │   ├── Login.tsx         # Pantalla de login
│   │   ├── Users.tsx         # Gestión de usuarios
│   │   ├── Companies.tsx     # Gestión de compañías
│   │   ├── Conceptos.tsx     # Gestión de conceptos
│   │   └── ...               # 15+ páginas especializadas
│   ├── Modals/               # Componentes modales
│   ├── Calendar/             # Componentes de calendario
│   ├── Session/              # Gestión de sesión
│   └── UI/                   # Componentes base reutilizables
├── contexts/                  # Context providers para estado global
│   ├── AuthContext.tsx       # Autenticación y usuario
│   ├── ThemeContext.tsx      # Tema claro/oscuro
│   └── SessionContext.tsx    # Control de sesión activa
├── hooks/                     # Hooks personalizados
│   ├── useAuth.tsx          # Hook de autenticación
│   ├── useActivityTracker.tsx # Seguimiento actividad
│   └── useAuditoria.tsx     # Hook de auditoría
├── services/                  # Servicios para API calls
├── types/                     # Definiciones TypeScript
├── utils/                     # Utilidades y helpers
├── data/                      # Datos mock y constantes
└── styles/                    # Estilos globales
```

---

## 🔧 CONFIGURACIÓN BASE

### Vite Configuration (`vite.config.ts`)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          recharts: ['recharts'],
        },
      },
    },
  },
})
```

### Tailwind Configuration (`tailwind.config.js`)

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        bolivar: {
          blue: '#0066cc',
          red: '#cc0000',
          gray: '#666666',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
      }
    },
  },
  plugins: [],
}
```

### TypeScript Configuration (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/contexts/*": ["contexts/*"],
      "@/types/*": ["types/*"],
      "@/utils/*": ["utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN

### Context de Autenticación (`AuthContext.tsx`)

```tsx
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

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Configuración de tokens
const TOKEN_CONFIG = {
  EXPIRE_TIME: 60 * 60 * 1000,    // 1 hora en ms (sincronizado con backend)
  REFRESH_BEFORE: 5 * 60 * 1000,  // Renovar 5 minutos antes de expirar
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tokenExpireTime, setTokenExpireTime] = useState<number | null>(null);
  const refreshTimerRef = useRef<number | null>(null);

  // Mapeo de roles desde la base de datos a códigos del sistema
  const mapRoleToSystemCode = (roleFromDB: string): 'administrador' | 'tesoreria' | 'pagaduria' | 'mesa_dinero' => {
    switch (roleFromDB.toLowerCase()) {
      case 'administrador': return 'administrador';
      case 'tesorería':
      case 'tesoreria': return 'tesoreria';
      case 'pagaduría':
      case 'pagaduria': return 'pagaduria';
      case 'mesa de dinero':
      case 'mesa_dinero': return 'mesa_dinero';
      default:
        console.warn(`Rol desconocido: ${roleFromDB}, usando administrador por defecto`);
        return 'administrador';
    }
  };

  // Función de login con validación completa
  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    setLoginError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Guardar token y configurar usuario
        localStorage.setItem('access_token', data.access_token);
        setToken(data.access_token);
        
        const mappedRole = mapRoleToSystemCode(data.user.rol);
        const userData: User = {
          id: data.user.id.toString(),
          name: data.user.nombre,
          email: data.user.email,
          role: mappedRole,
          estado: true
        };

        setUser(userData);
        
        // Configurar renovación automática de token
        const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
        setTokenExpireTime(expireTime);
        scheduleTokenRefresh(expireTime);
        
        return { success: true };
      } else {
        // Manejar errores específicos del backend
        let errorMessage = data.detail || 'Error de autenticación';
        
        if (response.status === 403) {
          errorMessage = 'Su cuenta ha sido desactivada. Contacte al administrador.';
        } else if (response.status === 401) {
          errorMessage = 'Usuario o contraseña incorrectos';
        }
        
        setLoginError(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Error en login:', error);
      const errorMessage = 'Error de conexión. Verifique su red e intente nuevamente.';
      setLoginError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  // Renovación automática de token
  const refreshToken = async (): Promise<boolean> => {
    const currentToken = localStorage.getItem('access_token');
    if (!currentToken) return false;

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
        
        // Reprogramar siguiente renovación
        const expireTime = Date.now() + TOKEN_CONFIG.EXPIRE_TIME;
        setTokenExpireTime(expireTime);
        scheduleTokenRefresh(expireTime);
        
        console.log('✅ Token renovado exitosamente');
        return true;
      } else {
        console.error('❌ Error renovando token');
        logout();
        return false;
      }
    } catch (error) {
      console.error('❌ Error en renovación de token:', error);
      logout();
      return false;
    }
  };

  // Programar renovación automática
  const scheduleTokenRefresh = (expireTime: number) => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    const refreshTime = expireTime - TOKEN_CONFIG.REFRESH_BEFORE - Date.now();
    
    if (refreshTime > 0) {
      console.log(`⏰ Token se renovará en ${Math.round(refreshTime / 60000)} minutos`);
      refreshTimerRef.current = setTimeout(() => {
        refreshToken();
      }, refreshTime);
    }
  };

  // Logout completo
  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
    setTokenExpireTime(null);
    
    // Limpiar timer de renovación
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
    
    console.log('👋 Usuario desconectado');
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      logout,
      isLoading,
      loginError,
      clearLoginError,
      refreshToken
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

---

## 🎨 COMPONENTES DE LAYOUT

### Sidebar con Control de Roles (`Sidebar.tsx`)

```tsx
interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  isCollapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onPageChange, isCollapsed }) => {
  const { logout, user } = useAuth();
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);

  // Estructura de menús jerárquica por roles
  const getMenuStructure = () => {
    if (!user) return [];

    const menuStructure = [
      {
        id: 'gestion',
        label: 'Gestión Financiera',
        icon: DollarSign,
        items: [
          { id: 'panel', label: 'Flujo Diario', icon: LayoutDashboard },
          { id: 'conciliacion', label: 'Conciliación', icon: Calculator },
          { id: 'historico-trm', label: 'TRM Histórico', icon: TrendingUp }
        ]
      },
      {
        id: 'analisis',
        label: 'Análisis y Reportes',
        icon: FileText,
        items: [
          { id: 'flujo-mensual', label: 'Dashboard', icon: Calendar },
          { id: 'informes', label: 'Consolidado', icon: BarChart3 }
        ]
      },
      {
        id: 'parametros',
        label: 'Parámetros',
        icon: Settings,
        items: [
          { id: 'companias', label: 'Compañías', icon: Building2 },
          { id: 'conceptos', label: 'Conceptos', icon: Layers }
        ]
      },
      {
        id: 'control',
        label: 'Control y Seguridad',
        icon: Shield,
        items: [
          { id: 'auditoria', label: 'Auditoría', icon: Shield },
          { id: 'usuarios', label: 'Usuarios', icon: Users },
          { id: 'cargue-inicial', label: 'Cargue Inicial', icon: Calendar }
        ]
      }
    ];

    // Filtrar menús según rol del usuario
    switch (user.role) {
      case 'administrador':
        return menuStructure; // Admin ve todo

      case 'tesoreria':
        return menuStructure.filter(group => group.id !== 'control');

      case 'pagaduria':
        return menuStructure.filter(group => group.id !== 'control');

      case 'mesa_dinero':
        return menuStructure.filter(group => 
          group.id !== 'parametros' && group.id !== 'control'
        ).map(group => {
          if (group.id === 'gestion') {
            // Mesa de dinero no ve conciliación
            return {
              ...group,
              items: group.items.filter(item => item.id !== 'conciliacion')
            };
          }
          return group;
        });

      default:
        return [];
    }
  };

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupId) 
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  const menuStructure = getMenuStructure();

  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Logo / Brand */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        {!isCollapsed ? (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FC</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-900 dark:text-white">SIFCO</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Flujo de Caja</p>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto">
            <span className="text-white font-bold text-sm">FC</span>
          </div>
        )}
      </div>

      {/* Usuario actual */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        {!isCollapsed ? (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 dark:text-white truncate">
                {user?.name}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                {user?.role?.replace('_', ' ')}
              </p>
            </div>
          </div>
        ) : (
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mx-auto">
            <span className="text-white font-semibold text-sm">
              {user?.name?.charAt(0)?.toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Navegación principal */}
      <nav className="flex-1 overflow-y-auto py-4">
        {menuStructure.map((group) => (
          <div key={group.id} className="mb-2">
            {/* Encabezado de grupo */}
            {!isCollapsed && (
              <button
                onClick={() => toggleGroup(group.id)}
                className="w-full px-4 py-2 flex items-center justify-between text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <group.icon size={16} />
                  <span>{group.label}</span>
                </div>
                {expandedGroups.includes(group.id) ? (
                  <ChevronDown size={16} />
                ) : (
                  <ChevronRight size={16} />
                )}
              </button>
            )}

            {/* Items del grupo */}
            {(expandedGroups.includes(group.id) || isCollapsed) && (
              <div className={isCollapsed ? '' : 'ml-4'}>
                {group.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onPageChange(item.id)}
                    className={`w-full px-4 py-2 flex items-center space-x-3 text-left transition-colors ${
                      currentPage === item.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-r-2 border-blue-600'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                    title={isCollapsed ? item.label : undefined}
                  >
                    <item.icon size={20} />
                    {!isCollapsed && <span className="font-medium">{item.label}</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Botón de logout */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          title={isCollapsed ? "Cerrar Sesión" : undefined}
        >
          <LogOut size={20} />
          {!isCollapsed && <span className="font-medium">Cerrar Sesión</span>}
        </button>
      </div>
    </div>
  );
};
```

### Header Principal (`Header.tsx`)

```tsx
interface HeaderProps {
  title: string;
  onToggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ title, onToggleSidebar }) => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Toggle sidebar */}
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <Menu size={20} className="text-gray-600 dark:text-gray-400" />
          </button>

          {/* Título de la página */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {title}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {new Date().toLocaleDateString('es-CO', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Indicador de conectividad */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              En línea
            </span>
          </div>

          {/* Toggle tema claro/oscuro */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {theme === 'light' ? (
              <Moon size={20} className="text-gray-600 dark:text-gray-400" />
            ) : (
              <Sun size={20} className="text-gray-600 dark:text-gray-400" />
            )}
          </button>

          {/* Notificaciones */}
          <NotificationDropdown />

          {/* Avatar de usuario */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
```

---

## 📊 PÁGINAS PRINCIPALES

### Dashboard Principal (`Dashboard.tsx`)

```tsx
const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { registrarAccion } = useAuditoria();
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [cashFlowData, setCashFlowData] = useState<CashFlowData>({});
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    company: 'all',
    area: 'all'
  });

  // Cargar datos del flujo de caja
  useEffect(() => {
    const loadCashFlowData = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `/api/v1/transacciones-flujo-caja/fecha/${selectedDate}?area=${filters.area}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );

        if (response.ok) {
          const data = await response.json();
          setCashFlowData(data);
          
          // Registrar acceso en auditoría
          registrarAccion('dashboard', 'VIEW', {
            fecha: selectedDate,
            area: filters.area
          });
        }
      } catch (error) {
        console.error('Error cargando flujo de caja:', error);
      } finally {
        setLoading(false);
      }
    };

    loadCashFlowData();
  }, [selectedDate, filters.area]);

  // Renderizado condicional según rol
  const renderDashboardByRole = () => {
    switch (user?.role) {
      case 'administrador':
        return <DashboardAdmin />;
      case 'mesa_dinero':
        return <DashboardMesa />;
      case 'pagaduria':
        return <DashboardPagaduria />;
      case 'tesoreria':
        return <DashboardTesoreria />;
      default:
        return <div>Rol no reconocido</div>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Controles de filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <DatePicker
              value={selectedDate}
              onChange={setSelectedDate}
              label="Fecha del flujo"
            />
            
            <select
              value={filters.area}
              onChange={(e) => setFilters(prev => ({ ...prev, area: e.target.value }))}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">Todas las áreas</option>
              <option value="tesoreria">Tesorería</option>
              <option value="pagaduria">Pagaduría</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            {loading && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            )}
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Última actualización: {new Date().toLocaleTimeString('es-CO')}
            </span>
          </div>
        </div>
      </div>

      {/* Dashboard específico por rol */}
      {renderDashboardByRole()}

      {/* Resumen de totales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SummaryCard
          title="Total Ingresos"
          value="$125,450,000"
          change="+5.2%"
          changeType="positive"
          icon={TrendingUp}
        />
        <SummaryCard
          title="Total Egresos"
          value="$89,230,000"
          change="-2.1%"
          changeType="negative"
          icon={TrendingDown}
        />
        <SummaryCard
          title="Saldo Neto"
          value="$36,220,000"
          change="+12.8%"
          changeType="positive"
          icon={DollarSign}
        />
      </div>
    </div>
  );
};
```

---

## 🎯 SISTEMA DE TIPOS TYPESCRIPT

### Definiciones de Tipos (`types/index.ts`)

```typescript
// Tipo de usuario con roles específicos
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'administrador' | 'tesoreria' | 'pagaduria' | 'mesa_dinero';
  estado: boolean;
  avatar?: string;
}

// Estructura de transacciones
export interface Transaction {
  id: string;
  fecha: string;
  concepto: {
    id: number;
    nombre: string;
    codigo: string;
    area: 'tesoreria' | 'pagaduria' | 'ambas';
  };
  cuenta?: {
    id: number;
    numero_cuenta: string;
    banco: {
      nombre: string;
    };
    compania: {
      nombre: string;
    };
  };
  monto: number;
  descripcion?: string;
  usuario: {
    nombre: string;
  };
  created_at: string;
  updated_at: string;
}

// Datos de flujo de caja diario
export interface FlujoCajaDiario {
  fecha: string;
  area: string;
  items: FlujoCajaDiarioItem[];
  total_ingresos: number;
  total_egresos: number;
  saldo_neto: number;
}

export interface FlujoCajaDiarioItem {
  concepto_id: number;
  concepto_nombre: string;
  codigo: string;
  monto: number;
  transacciones_count: number;
}

// Configuración de conceptos
export interface Concepto {
  id: number;
  nombre: string;
  codigo: string;
  tipo: string;
  area: 'tesoreria' | 'pagaduria' | 'ambas';
  orden_display: number;
  activo: boolean;
  depende_de_concepto_id?: number;
  tipo_dependencia?: 'copia' | 'suma' | 'resta';
  formula_dependencia?: string;
}

// Estructura de compañías
export interface Company {
  id: number;
  nombre: string;
  cuentas_bancarias?: BankAccount[];
}

// Cuentas bancarias
export interface BankAccount {
  id: number;
  numero_cuenta: string;
  tipo_cuenta: 'CORRIENTE' | 'AHORROS';
  banco: {
    id: number;
    nombre: string;
  };
  compania: {
    id: number;
    nombre: string;
  };
  monedas?: CuentaMoneda[];
}

// Configuración de monedas por cuenta
export interface CuentaMoneda {
  id: number;
  tipo_moneda: 'COP' | 'USD';
  saldo_inicial: number;
  saldo_actual: number;
  activo: boolean;
}

// Datos TRM
export interface TRM {
  fecha: string;
  valor: number;
  fecha_creacion: string;
}

// Configuración de sesión
export interface SessionConfig {
  warningTime: number; // Tiempo en ms antes de mostrar advertencia
  expireTime: number;  // Tiempo en ms para expirar sesión
  checkInterval: number; // Intervalo de verificación
}

// Respuesta de API genérica
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  detail?: string;
}

// Filtros para dashboards
export interface DashboardFilters {
  fecha: string;
  area: 'all' | 'tesoreria' | 'pagaduria';
  compania: 'all' | number;
  banco: 'all' | number;
}
```

---

## 🛠️ HOOKS PERSONALIZADOS

### Hook de Auditoría (`useAuditoria.tsx`)

```tsx
interface AuditoriaHook {
  registrarAccion: (tabla: string, accion: string, datos?: any) => Promise<void>;
  obtenerAuditoria: (filtros?: any) => Promise<any[]>;
  loading: boolean;
  error: string | null;
}

export const useAuditoria = (): AuditoriaHook => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const registrarAccion = async (tabla: string, accion: string, datos?: any) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/v1/auditoria', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          tabla_afectada: tabla,
          accion,
          datos_nuevos: datos,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('Error registrando auditoría');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error en auditoría:', err);
    } finally {
      setLoading(false);
    }
  };

  const obtenerAuditoria = async (filtros?: any): Promise<any[]> => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams(filtros);
      const response = await fetch(`/api/v1/auditoria?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error obteniendo auditoría');
      }

      const data = await response.json();
      return data;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      return [];
    } finally {
      setLoading(false);
    }
  };

  return {
    registrarAccion,
    obtenerAuditoria,
    loading,
    error
  };
};
```

### Hook de Seguimiento de Actividad (`useActivityTracker.tsx`)

```tsx
export const useActivityTracker = () => {
  const lastActivity = useRef(Date.now());
  const activityTimer = useRef<number | null>(null);

  const trackActivity = useCallback(() => {
    lastActivity.current = Date.now();
    
    // Enviar heartbeat al servidor cada 5 minutos de actividad
    if (activityTimer.current) {
      clearTimeout(activityTimer.current);
    }

    activityTimer.current = setTimeout(async () => {
      try {
        await fetch('/api/v1/session/heartbeat', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
      } catch (error) {
        console.warn('Error enviando heartbeat:', error);
      }
    }, 5 * 60 * 1000); // 5 minutos

  }, []);

  const trackPageNavigation = useCallback((page: string) => {
    // Registrar navegación de página para analytics
    try {
      fetch('/api/v1/analytics/page-view', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          page,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent
        })
      });
    } catch (error) {
      console.warn('Error registrando navegación:', error);
    }
  }, []);

  useEffect(() => {
    // Configurar listeners de actividad
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    
    events.forEach(event => {
      document.addEventListener(event, trackActivity);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, trackActivity);
      });
      
      if (activityTimer.current) {
        clearTimeout(activityTimer.current);
      }
    };
  }, [trackActivity]);

  return {
    trackActivity,
    trackPageNavigation,
    getLastActivity: () => lastActivity.current
  };
};
```

---

## 🔄 GESTIÓN DE ESTADO Y COMUNICACIÓN

### Context de Sesión (`SessionContext.tsx`)

```tsx
interface SessionContextType {
  isSessionWarningVisible: boolean;
  sessionTimeLeft: number;
  extendSession: () => void;
  trackActivity: () => void;
}

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSessionWarningVisible, setIsSessionWarningVisible] = useState(false);
  const [sessionTimeLeft, setSessionTimeLeft] = useState(0);
  const { logout } = useAuth();

  const SESSION_CONFIG = {
    warningTime: 10 * 60 * 1000,  // 10 minutos
    expireTime: 60 * 60 * 1000,   // 1 hora
    checkInterval: 30 * 1000       // 30 segundos
  };

  // Extender sesión
  const extendSession = useCallback(() => {
    const newExpiration = Date.now() + SESSION_CONFIG.expireTime;
    localStorage.setItem('session_expiration', newExpiration.toString());
    setIsSessionWarningVisible(false);
  }, []);

  // Verificar estado de la sesión
  useEffect(() => {
    const checkSession = () => {
      const expiration = localStorage.getItem('session_expiration');
      if (!expiration) return;

      const expirationTime = parseInt(expiration);
      const timeLeft = expirationTime - Date.now();

      setSessionTimeLeft(Math.max(0, timeLeft));

      if (timeLeft <= 0) {
        // Sesión expirada
        logout();
      } else if (timeLeft <= SESSION_CONFIG.warningTime && !isSessionWarningVisible) {
        // Mostrar advertencia
        setIsSessionWarningVisible(true);
      }
    };

    const interval = setInterval(checkSession, SESSION_CONFIG.checkInterval);
    return () => clearInterval(interval);
  }, [logout, isSessionWarningVisible]);

  return (
    <SessionContext.Provider value={{
      isSessionWarningVisible,
      sessionTimeLeft,
      extendSession,
      trackActivity
    }}>
      {children}
      {isSessionWarningVisible && <SessionWarningModal />}
    </SessionContext.Provider>
  );
};
```

---

## 📱 DISEÑO RESPONSIVE Y TEMA

### Sistema de Tema (`ThemeContext.tsx`)

```tsx
type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Detectar preferencia del sistema
    const saved = localStorage.getItem('theme');
    if (saved) return saved as Theme;
    
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    // Aplicar tema al documento
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

### Clases CSS Responsive

```css
/* Utilidades personalizadas en index.css */
@layer utilities {
  .sidebar-transition {
    @apply transition-all duration-300 ease-in-out;
  }
  
  .glass-effect {
    @apply bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border border-white/20;
  }
  
  .table-responsive {
    @apply min-w-full overflow-x-auto;
  }
  
  .card-shadow {
    @apply shadow-sm hover:shadow-md transition-shadow duration-200;
  }
  
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium;
  }
  
  .btn-secondary {
    @apply bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg transition-colors;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  }
}

/* Animaciones personalizadas */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
```

---

## 🔧 OPTIMIZACIONES Y RENDIMIENTO

### Lazy Loading de Componentes

```tsx
// Carga diferida de páginas pesadas
const DashboardAdmin = React.lazy(() => import('./components/Pages/DashboardAdmin'));
const Reports = React.lazy(() => import('./components/Pages/Reports'));
const Auditoria = React.lazy(() => import('./components/Pages/Auditoria'));

// En App.tsx
<Suspense fallback={
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
}>
  {renderPageComponent()}
</Suspense>
```

### Memoización de Componentes Pesados

```tsx
const ExpensiveChart = React.memo<ChartProps>(({ data, filters }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      formattedValue: new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
      }).format(item.value)
    }));
  }, [data]);

  return <RenderChart data={processedData} />;
});
```

### Interceptor de API con Retry Logic

```tsx
// utils/apiInterceptor.ts
class ApiClient {
  private baseURL = 'http://localhost:8000/api/v1';
  private maxRetries = 3;

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    let attempt = 1;
    
    while (attempt <= this.maxRetries) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            ...options?.headers
          }
        });

        if (response.status === 401) {
          // Token expirado, intentar renovar
          const renewed = await this.refreshToken();
          if (renewed && attempt < this.maxRetries) {
            attempt++;
            continue;
          }
          throw new Error('Sesión expirada');
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();

      } catch (error) {
        if (attempt === this.maxRetries) {
          throw error;
        }
        
        // Backoff exponencial
        await this.delay(Math.pow(2, attempt) * 1000);
        attempt++;
      }
    }

    throw new Error('Max retries exceeded');
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const apiClient = new ApiClient();
```

Este documento proporciona una visión completa de la arquitectura del frontend, incluyendo todos los componentes principales, patrones de diseño, sistema de tipos TypeScript, y optimizaciones implementadas en el sistema de flujo de caja.