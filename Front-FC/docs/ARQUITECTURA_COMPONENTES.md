# Estructura de Componentes

Documentación de la arquitectura de componentes del sistema de flujo de caja.

## 🏗️ **Arquitectura General**

La aplicación sigue una arquitectura por capas con separación clara de responsabilidades:

```
src/components/
├── Layout/          # Componentes de estructura
├── Pages/           # Páginas principales
├── Calendar/        # Componentes de calendario
└── [Individual]/    # Componentes específicos
```

## 📱 **Componentes de Layout**

### `Header.tsx`
Barra superior de la aplicación con navegación y información del usuario.

**Props:**
- `title: string` - Título de la página actual
- `subtitle?: string` - Subtítulo opcional
- `onToggleSidebar?: () => void` - Función para toggle del sidebar

**Características:**
- 🔔 Sistema de notificaciones integrado
- 🌙 Toggle de tema oscuro/claro
- 👤 Menú de perfil de usuario
- 📱 Responsive design

### `Sidebar.tsx`
Navegación lateral con menú contextual por rol de usuario.

**Props:**
- `currentPage: string` - Página actualmente activa
- `onPageChange: (page: string) => void` - Callback de cambio de página
- `collapsed: boolean` - Estado de colapso del sidebar

**Navegación por roles:**
- **Mesa de Dinero:** Dashboard, Conciliación, Reportes
- **Pagaduría:** Dashboard específico, Usuarios, Auditoría
- **Tesorería:** Dashboard tesorería, Flujo mensual, Configuración

### `ToastContainer.tsx`
Sistema de notificaciones toast para feedback del usuario.

**Características:**
- ✅ Notificaciones de éxito
- ❌ Notificaciones de error
- ⚠️  Advertencias
- ℹ️  Información general

## 📄 **Páginas Principales**

### `Dashboard.tsx`
Panel principal con vista del flujo de caja diario.

**Características:**
- 📊 Tabla dinámica con conceptos de flujo
- 📅 Navegación por fechas
- 💰 Resumen de ingresos y egresos
- 🏦 Filtros por compañía y banco
- 📱 Columnas fijas (sticky) para mejor UX

**Estado del componente:**
```typescript
interface DashboardState {
  selectedDate: Date;
  selectedCompany: string;
  selectedBank: string;
  cashFlowData: CashFlowData[];
  isLoading: boolean;
}
```

### `DashboardPagaduria.tsx` / `DashboardTesoreria.tsx`
Dashboards especializados para roles específicos.

**Diferencias por rol:**
- **Pagaduría:** Foco en pagos y nómina
- **Tesorería:** Foco en liquidez y proyecciones

### `Users.tsx`
Gestión de usuarios del sistema (solo administradores).

**Funcionalidades:**
- 👥 CRUD completo de usuarios
- 🔍 Búsqueda y filtros
- 👤 Asignación de roles
- 📧 Gestión de estados (activo/inactivo)

### `Auditoria.tsx`
Log de auditoría para seguimiento de acciones.

**Campos registrados:**
- 🕐 Timestamp de la acción
- 👤 Usuario que ejecutó la acción
- 🔧 Tipo de acción (CREATE, UPDATE, DELETE)
- 📄 Módulo afectado
- 💾 Valores antes/después del cambio

## 🗓️ **Componentes de Calendario**

### `DatePicker.tsx`
Selector de fechas con calendario visual.

**Props:**
- `selectedDate: Date` - Fecha seleccionada
- `onDateChange: (date: Date) => void` - Callback de cambio
- `minDate?: Date` - Fecha mínima seleccionable
- `maxDate?: Date` - Fecha máxima seleccionable

## 📊 **Componentes de Datos**

### `SummaryCards.tsx`
Tarjetas de resumen con métricas principales.

**Métricas mostradas:**
- 💚 Total ingresos del día
- 🔴 Total egresos del día
- 💙 Saldo neto
- 📈 Variación vs día anterior

### `TransactionList.tsx`
Lista detallada de transacciones con paginación.

### `CategoryChart.tsx`
Gráficos de categorías usando Recharts.

**Tipos de gráficos:**
- 🥧 Pie chart para distribución
- 📊 Bar chart para comparaciones
- 📈 Line chart para tendencias

## 🔧 **Patrones de Desarrollo**

### Hooks Personalizados
- `useAuth()` - Gestión de autenticación
- `useCashFlow()` - Datos de flujo de caja
- `useNotifications()` - Sistema de notificaciones
- `useToast()` - Mensajes toast

### Contextos
- `AuthContext` - Estado de autenticación global
- `ThemeContext` - Gestión de tema oscuro/claro

### Gestión de Estado
```typescript
// Patrón useState para estado local
const [data, setData] = useState<DataType[]>([]);

// Patrón useReducer para estado complejo
const [state, dispatch] = useReducer(reducer, initialState);
```

### Tipado TypeScript
```typescript
// Definición de tipos en src/types/index.ts
export interface User {
  id: number;
  name: string;
  email: string;
  role: 'mesa' | 'pagaduria' | 'tesoreria';
}
```

## 🎨 **Estilos y Diseño**

### Tailwind CSS
- **Utilidades:** Clases predefinidas para rapidez
- **Responsive:** Mobile-first design
- **Dark Mode:** Soporte automático con `dark:` prefix

### Tema Bolívar
```css
/* Colores principales */
--bolivar-500: #1e40af;  /* Azul principal */
--bolivar-600: #1d4ed8;  /* Azul hover */
--bolivar-700: #1e3a8a;  /* Azul activo */
```

### Iconos
- **Lucide React:** Iconos SVG optimizados
- **Consistencia:** Set uniforme en toda la app
