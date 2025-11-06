# Frontend - React + TypeScript + Vite

## 📁 Estructura Limpia y Organizada

```
Front-FC/
├── public/                  # Archivos estáticos
│   ├── assets/
│   └── logos/
├── src/
│   ├── components/          # ✅ Solo componentes reutilizables
│   │   ├── Calendar/       # Componentes de calendario
│   │   ├── Conceptos/      # Gestión de conceptos
│   │   ├── Dashboard/      # Componentes de dashboard
│   │   ├── Layout/         # Layout components (Header, Sidebar)
│   │   ├── Session/        # Manejo de sesiones
│   │   └── UI/             # Componentes UI generales
│   ├── pages/              # ✅ Páginas principales (antes components/Pages)
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Users.tsx
│   │   └── ...
│   ├── contexts/           # Context providers
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── types/              # TypeScript types
│   ├── utils/              # Utilidades
│   ├── styles/             # Estilos globales
│   ├── App.tsx            # Componente raíz
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globales
├── scripts/                # Scripts de build y deploy
│   ├── build/
│   ├── deploy/
│   └── utils/
├── docs/                   # Documentación
├── .env                    # Variables de entorno
├── .env.example           # Ejemplo de variables
├── package.json           # Dependencias
├── vite.config.ts         # Configuración de Vite
├── tailwind.config.js     # Configuración de Tailwind
└── tsconfig.json          # Configuración de TypeScript
```

## 🧹 Limpieza Realizada

### ❌ Eliminados (archivos basura):
- `.bolt/` - Carpeta de Bolt.new (no necesaria)
- `debug_sync.html` - Archivo de debug temporal
- `dist/` - Build artifacts (se regeneran)
- `.env.development`, `.env.production` - Duplicados innecesarios

### ❌ Archivos duplicados eliminados:
- `Companies_Enhanced.tsx`, `Companies_New.tsx` → Solo `Companies.tsx`
- `DashboardPagaduriaNew.tsx`, `DashboardPagaduriaTable.tsx`
- `DashboardTesoreriaNew.tsx`, `DashboardTesoreriaTable.tsx`
- `LoginTest.tsx`, `Login_new.tsx` → Solo `Login.tsx`
- `Header.tsx` (raíz) → Ya existe en `Layout/Header.tsx`
- `LoginForm.tsx` → Obsoleto

### ✅ Reorganización:
- `src/components/Pages/` → `src/pages/` (mejor organización)
- Componentes duplicados eliminados
- Imports actualizados en `App.tsx`

## 🚀 Desarrollo

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview
```

## 📝 Convenciones

### Estructura de archivos:
- **Pages**: Páginas completas en `src/pages/`
- **Components**: Componentes reutilizables en `src/components/`
- **Hooks**: Custom hooks en `src/hooks/`
- **Services**: Lógica de API en `src/services/`

### Nomenclatura:
- Componentes: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Utilidades: `camelCase.ts`
- Tipos: `PascalCase` en `types/index.ts`

## 🔧 Configuración

### Variables de Entorno (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

Ver `.env.example` para más detalles.

## 📚 Documentación Adicional

Ver carpeta `docs/` para documentación detallada:
- `ARQUITECTURA_COMPONENTES.md`
- `DESARROLLO.md`

---

**Última limpieza:** 6 de Noviembre 2025  
**Archivos eliminados:** 15+ archivos duplicados/obsoletos  
**Estructura:** Limpia y organizada según estándares de React
