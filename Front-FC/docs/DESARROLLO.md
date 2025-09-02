# Guía de Desarrollo Frontend

Estándares, mejores prácticas y flujo de desarrollo para el sistema de flujo de caja.

## 🚀 **Configuración del Entorno**

### Prerequisitos
- **Node.js** 18+ 
- **npm** 9+
- **Git** para control de versiones
- **VS Code** (recomendado) con extensiones:
  - ES7+ React/Redux/React-Native snippets
  - Tailwind CSS IntelliSense
  - TypeScript Importer
  - Prettier - Code formatter

### Instalación
```bash
# Clonar repositorio
git clone <repository-url>
cd Front-FC

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## 📁 **Estructura del Proyecto**

```
src/
├── components/          # Componentes reutilizables
│   ├── Layout/         # Componentes de estructura
│   ├── Pages/          # Páginas principales
│   └── Calendar/       # Componentes específicos
├── contexts/           # Contextos de React
├── hooks/             # Hooks personalizados
├── types/             # Definiciones TypeScript
├── utils/             # Funciones utilitarias
└── data/              # Datos mock/constantes
```

## 🔧 **Scripts Disponibles**

```bash
# Desarrollo
npm run dev          # Servidor desarrollo (puerto 5000)
npm run build        # Construcción para producción
npm run preview      # Vista previa de build
npm run lint         # Verificar código con ESLint

# Utilidades (scripts personalizados)
node scripts/utils/check-project.js    # Verificar estado del proyecto
node scripts/utils/analyze-bundle.js   # Analizar bundle de producción
```

## 📝 **Estándares de Código**

### Nomenclatura
```typescript
// Componentes: PascalCase
const UserDashboard: React.FC = () => {}

// Hooks: camelCase con "use" prefix
const useAuthUser = () => {}

// Constantes: UPPER_SNAKE_CASE
const API_BASE_URL = 'http://localhost:8000';

// Variables/funciones: camelCase
const currentUser = getCurrentUser();
```

### Estructura de Componentes
```typescript
import React, { useState, useEffect } from 'react';
import { Icon } from 'lucide-react';
import { useCustomHook } from '../hooks/useCustomHook';

// Props interface
interface ComponentProps {
  title: string;
  onAction?: () => void;
}

// Component definition
const ComponentName: React.FC<ComponentProps> = ({ 
  title, 
  onAction 
}) => {
  // Hooks
  const [state, setState] = useState(false);
  const { data } = useCustomHook();

  // Effects
  useEffect(() => {
    // Effect logic
  }, []);

  // Event handlers
  const handleClick = () => {
    // Handler logic
  };

  // Render
  return (
    <div className="component-container">
      {/* JSX content */}
    </div>
  );
};

export default ComponentName;
```

### TypeScript
```typescript
// Definir interfaces para props
interface UserProps {
  user: User;
  onEdit: (id: number) => void;
}

// Tipar hooks personalizados
const useUsers = (): {
  users: User[];
  loading: boolean;
  error: string | null;
} => {
  // Hook implementation
};

// Usar tipos para estado
const [users, setUsers] = useState<User[]>([]);
```

### Estilos con Tailwind
```tsx
// Componente responsivo con dark mode
<div className="bg-white dark:bg-gray-800 p-4 md:p-6 lg:p-8 rounded-lg shadow-sm">
  <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
    Título
  </h2>
</div>

// Botones consistentes
<button className="px-4 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors">
  Acción
</button>
```

## 🔄 **Flujo de Desarrollo**

### 1. Feature Branch
```bash
git checkout -b feature/nueva-funcionalidad
```

### 2. Desarrollo
- Escribir código siguiendo estándares
- Crear/actualizar tests si es necesario
- Verificar lint: `npm run lint`

### 3. Verificación
```bash
# Verificar estado del proyecto
node scripts/utils/check-project.js

# Construir y analizar
npm run build
node scripts/utils/analyze-bundle.js
```

### 4. Commit y Push
```bash
git add .
git commit -m "feat: descripción de la funcionalidad"
git push origin feature/nueva-funcionalidad
```

## 🧪 **Testing (Futuro)**

```typescript
// Test de componente
import { render, screen } from '@testing-library/react';
import ComponentName from './ComponentName';

test('renders component correctly', () => {
  render(<ComponentName title="Test" />);
  expect(screen.getByText('Test')).toBeInTheDocument();
});
```

## 🎨 **Convenciones de UI**

### Colores
- **Primario:** `bg-bolivar-600` (azul Bolívar)
- **Éxito:** `bg-green-600`
- **Error:** `bg-red-600`
- **Advertencia:** `bg-yellow-600`
- **Información:** `bg-blue-600`

### Espaciado
- **Contenedores:** `p-6` (24px)
- **Componentes:** `space-y-4` (16px vertical)
- **Elementos:** `gap-2` (8px)

### Tipografía
- **Títulos:** `text-2xl font-bold`
- **Subtítulos:** `text-lg font-semibold`
- **Cuerpo:** `text-base`
- **Pequeño:** `text-sm text-gray-600`

## 🔗 **Integración con Backend**

### API Calls
```typescript
// Usar fetch con manejo de errores
const apiCall = async (endpoint: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

### Gestión de Estado
```typescript
// Hook para datos del servidor
const useApiData = (endpoint: string) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiCall(endpoint);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error };
};
```

## 🚀 **Optimización para Producción**

### Bundle Optimization
- **Code Splitting:** Lazy loading de páginas
- **Tree Shaking:** Eliminación automática de código no usado
- **Chunk Splitting:** Separación de vendor y app chunks

### Performance
- **Lazy Loading:** `React.lazy()` para componentes pesados
- **Memoization:** `React.memo()` y `useMemo()` cuando sea necesario
- **Virtual Lists:** Para listas grandes de datos

### SEO y Accessibility
- Semantic HTML
- ARIA labels
- Alt text para imágenes
- Contraste de colores adecuado

## 🔧 **Troubleshooting**

### Problemas Comunes
1. **Error de módulos:** `rm -rf node_modules && npm install`
2. **TypeScript errors:** Verificar tipos en `src/types/`
3. **Build fails:** Revisar `npm run lint`
4. **Performance:** Usar `analyze-bundle.js`

### Debugging
```typescript
// Console logs para desarrollo
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data);
}

// React DevTools para inspeccionar componentes
// Redux DevTools para estado global (si se implementa)
```
