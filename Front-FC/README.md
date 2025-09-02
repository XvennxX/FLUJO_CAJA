# Sistema de Flujo de Caja - Frontend

Aplicación web desarrollada con React + TypeScript para el sistema de flujo de caja de Bolívar.

## 🏗️ **Estructura del Proyecto**

```
Front-FC/
├── src/                     # Código fuente principal
│   ├── components/         # Componentes React
│   │   ├── Layout/        # Componentes de estructura (Header, Sidebar)
│   │   ├── Pages/         # Páginas principales
│   │   └── Calendar/      # Componentes de calendario
│   ├── contexts/          # Contextos de React (Auth, Theme)
│   ├── hooks/             # Hooks personalizados
│   ├── types/             # Definiciones TypeScript
│   ├── utils/             # Funciones utilitarias
│   └── data/              # Datos mock y constantes
├── scripts/                # Scripts organizados por funcionalidad
│   ├── build/             # Scripts de construcción
│   ├── deploy/            # Scripts de despliegue
│   └── utils/             # Utilidades de análisis
├── docs/                   # Documentación del proyecto
├── dist/                   # Archivos construidos (generado)
├── package.json            # Dependencias y scripts npm
├── vite.config.ts          # Configuración de Vite
├── tailwind.config.js      # Configuración de Tailwind CSS
└── tsconfig.json           # Configuración de TypeScript
```

## 🚀 **Inicio Rápido**

### 1. Prerequisitos
- **Node.js** 18 o superior
- **npm** 9 o superior
- **Git** para control de versiones

### 2. Instalación
```bash
# Clonar repositorio (si aplica)
git clone <repository-url>
cd Front-FC

# Instalar dependencias
npm install

# Verificar configuración del proyecto
npm run check
```

### 3. Desarrollo
```bash
# Iniciar servidor de desarrollo
npm run dev

# La aplicación estará disponible en: http://localhost:5000
```

### 4. Construcción para producción
```bash
# Construir aplicación optimizada
npm run build:prod

# Analizar bundle generado
npm run analyze

# Vista previa de la construcción
npm run preview
```

## 🎯 **Características Principales**

### 🔐 **Autenticación y Roles**
- Sistema de login con JWT
- Roles diferenciados: Mesa, Pagaduría, Tesorería
- Dashboards personalizados por rol
- Gestión de sesiones segura

### 📊 **Dashboard de Flujo de Caja**
- Vista diaria de ingresos y egresos
- Tabla dinámica con **columnas fijas** (sticky)
- Navegación por fechas y filtros
- Resumen financiero en tiempo real
- Gráficos interactivos con Recharts

### 💰 **TRM Integrada**
- Obtención automática de TRM diaria
- Conversión automática de monedas
- Histórico de tasas de cambio
- Alertas de variaciones significativas

### 👥 **Gestión de Usuarios**
- CRUD completo de usuarios (solo admin)
- Asignación de roles y permisos
- Estados activo/inactivo
- Sistema de auditoría

### 🔍 **Auditoría Completa**
- Log detallado de todas las acciones
- Filtros por usuario, fecha y módulo
- Trazabilidad de cambios
- Reportes de actividad

## 🔧 **Tecnologías Utilizadas**

### Core Framework
- **React** 18.3 - Biblioteca de UI
- **TypeScript** 5.5 - Tipado estático
- **Vite** 5.4 - Build tool y dev server

### UI y Estilos
- **Tailwind CSS** 3.4 - Framework de CSS utility-first
- **Lucide React** - Iconos SVG optimizados
- **Responsive Design** - Mobile-first approach

### Visualización de Datos
- **Recharts** 3.1 - Gráficos y charts
- **date-fns** 4.1 - Manipulación de fechas

### Herramientas de Desarrollo
- **ESLint** 9.9 - Linting de código
- **PostCSS** - Procesamiento de CSS
- **Autoprefixer** - Prefijos CSS automáticos

## 📱 **Páginas y Funcionalidades**

### Dashboard Principal
- 📅 **Navegación por fechas** con calendario visual
- 🏢 **Filtros por compañía** (Capitalizadora, Bolívar, Comerciales)
- 🏦 **Filtros por banco** con cuentas asociadas
- 💵 **Columnas fijas** para código y cuenta bancaria
- 📊 **Resumen diario** de ingresos, egresos y saldo

### Dashboards Especializados
- **Pagaduría:** Foco en nómina y pagos a proveedores
- **Tesorería:** Análisis de liquidez y proyecciones
- **Mesa de Dinero:** Operaciones financieras y conciliación

### Gestión y Administración
- 👤 **Usuarios:** CRUD completo con roles
- 🏢 **Compañías:** Gestión de entidades
- 🔍 **Auditoría:** Logs detallados de actividad
- ⚙️  **Configuración:** Ajustes del sistema

## 🎨 **Diseño y UX**

### Tema Bolívar
- **Colores corporativos:** Azul Bolívar como color principal
- **Modo oscuro:** Toggle automático con persistencia
- **Tipografía:** Sistema de fuentes optimizado
- **Iconografía:** Consistente con Lucide React

### Responsive Design
- **Mobile First:** Optimizado para dispositivos móviles
- **Tablet Ready:** Adaptación automática a tablets
- **Desktop Enhanced:** Experiencia completa en escritorio

### Accesibilidad
- **ARIA Labels:** Navegación accesible
- **Contraste:** Cumple estándares WCAG
- **Keyboard Navigation:** Soporte completo de teclado

## 🔧 **Scripts Disponibles**

### Desarrollo
```bash
npm run dev          # Servidor de desarrollo (puerto 5000)
npm run lint         # Verificar código con ESLint
npm run lint:fix     # Corregir errores de linting automáticamente
```

### Construcción
```bash
npm run build        # Construcción básica
npm run build:prod   # Construcción con linting previo
npm run preview      # Vista previa de construcción
```

### Utilidades
```bash
npm run check        # Verificar estado del proyecto
npm run analyze      # Analizar bundle de producción
npm run clean        # Limpiar archivos temporales
npm run clean:install # Reinstalación completa de dependencias
```

### Scripts Avanzados
```bash
# Construcción con análisis (Windows)
scripts\build\build-prod.bat

# Verificación completa del proyecto
node scripts/utils/check-project.js

# Análisis detallado del bundle
node scripts/utils/analyze-bundle.js
```

## 🔐 **Configuración de Autenticación**

### Conexión con Backend
```typescript
// Configuración en src/contexts/AuthContext.tsx
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Usuarios de Prueba
| Rol | Email | Password |
|-----|-------|----------|
| Mesa de Dinero | mesadinero@bolivar.com | mesa123 |
| Pagaduría | pagaduria@bolivar.com | pagaduria123 |
| Tesorería | tesoreria@bolivar.com | tesoreria123 |

## 📊 **Integración con TRM**

La aplicación se integra automáticamente con el sistema TRM del backend:

- **Obtención Automática:** TRM actualizada diariamente a las 7 PM
- **Conversión en Tiempo Real:** USD a COP automático
- **Histórico:** Acceso a tasas históricas
- **Alertas:** Notificaciones de cambios significativos

## 🚀 **Despliegue**

### Desarrollo Local
```bash
npm run dev
# Aplicación disponible en http://localhost:5000
```

### Producción
```bash
# Construir para producción
npm run build:prod

# Los archivos estáticos se generan en /dist
# Configurar servidor web (Nginx, Apache) para servir desde /dist
```

### Docker (Futuro)
```dockerfile
# Ejemplo de Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5000
CMD ["npm", "run", "preview"]
```

## 📚 **Documentación Adicional**

- **[Arquitectura de Componentes](docs/ARQUITECTURA_COMPONENTES.md)** - Estructura detallada de componentes
- **[Guía de Desarrollo](docs/DESARROLLO.md)** - Estándares y mejores prácticas
- **[Scripts de Build](scripts/build/README.md)** - Documentación de construcción
- **[Utilidades](scripts/utils/README.md)** - Herramientas de análisis

## 🔧 **Configuración de Desarrollo**

### VS Code (Recomendado)
Extensiones recomendadas:
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript Importer
- Prettier - Code formatter

### Configuración de ESLint
```json
// .eslintrc.json
{
  "extends": ["@eslint/js", "typescript-eslint"],
  "rules": {
    "react-hooks/exhaustive-deps": "warn",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

## 🚦 **Estado del Proyecto**

✅ **Funcionalidades Completadas:**
- [x] Sistema de autenticación completo
- [x] Dashboards por rol implementados
- [x] Tabla de flujo de caja con columnas fijas
- [x] Integración con TRM automática
- [x] Sistema de notificaciones
- [x] Gestión de usuarios y auditoría
- [x] Responsive design
- [x] Modo oscuro/claro
- [x] Scripts de construcción y análisis

🚧 **En Desarrollo:**
- [ ] Tests unitarios y de integración
- [ ] PWA (Progressive Web App)
- [ ] Optimizaciones de performance
- [ ] Documentación de API

## 📞 **Soporte**

Para soporte técnico o preguntas sobre el desarrollo:
1. Revisar la documentación en `/docs`
2. Ejecutar `npm run check` para diagnóstico
3. Consultar logs en la consola del navegador
4. Verificar conectividad con el backend en `http://localhost:8000`

---

**Versión:** 1.0.0  
**Última actualización:** Agosto 2025  
**Compatibilidad:** Node.js 18+, Navegadores modernos
