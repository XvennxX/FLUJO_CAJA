# 💰 Aplicación de Flujo de Caja

Una aplicación web moderna para la gestión y seguimiento de flujo de caja empresarial, desarrollada con React, TypeScript y Tailwind CSS.

## 🚀 Características

### 📊 Dashboard Principal
- **Vista consolidada** de flujo de caja por empresa y fecha
- **Soporte multi-moneda** (USD y COP)
- **Filtros dinámicos** por empresas y divisas
- **Resumen ejecutivo** con totales y balances

### 💼 Gestión de Transacciones
- **Registro completo** de ingresos y gastos
- **Categorización automática** de transacciones
- **Búsqueda y filtros** avanzados
- **Edición y eliminación** de registros

### 📈 Reportes y Analytics
- **Reportes mensuales** detallados
- **Análisis por categorías** con gráficos
- **Tendencias temporales** de ingresos y gastos
- **Exportación de datos** en múltiples formatos

### 🏷️ Gestión de Categorías
- **Categorías personalizables** para ingresos y gastos
- **Códigos de color** para identificación visual
- **Estadísticas por categoría** con totales y porcentajes

### 👥 Administración de Usuarios
- **Sistema de autenticación** seguro
- **Gestión de roles** y permisos
- **Perfiles de usuario** personalizables

## 🛠️ Tecnologías Utilizadas

- **Frontend Framework**: React 18.3.1
- **Lenguaje**: TypeScript 5.5.3
- **Build Tool**: Vite 5.4.2
- **Estilos**: Tailwind CSS 3.4.1
- **Iconos**: Lucide React 0.344.0
- **Linting**: ESLint 9.9.1

## 🏗️ Arquitectura del Proyecto

```
src/
├── components/           # Componentes reutilizables
│   ├── Layout/          # Componentes de layout (Header, Sidebar)
│   ├── Pages/           # Páginas principales de la aplicación
│   ├── CategoryChart.tsx
│   ├── LoginForm.tsx
│   ├── SummaryCards.tsx
│   ├── TransactionForm.tsx
│   └── TransactionList.tsx
├── contexts/            # Contextos de React (AuthContext)
├── data/               # Datos mockados y configuraciones
├── hooks/              # Custom hooks (useCashFlow)
├── types/              # Definiciones de tipos TypeScript
├── utils/              # Utilidades y helpers
└── App.tsx             # Componente principal
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Node.js 16+ 
- npm o yarn

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd Front_FC
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Ejecutar en modo desarrollo**
   ```bash
   npm run dev
   ```

4. **Abrir en el navegador**
   ```
   http://localhost:5173
   ```

## 📝 Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Construye la aplicación para producción
- `npm run preview` - Vista previa de la build de producción
- `npm run lint` - Ejecuta el linter para verificar el código

## 🔐 Autenticación

La aplicación incluye un sistema de autenticación simulado. Para acceder utiliza:

- **Email**: `ana@email.com`
- **Contraseña**: `password`

## 🎨 Funcionalidades Principales

### Dashboard
- Visualización de cuentas bancarias por empresa
- Filtros por fecha y moneda
- Resumen de flujo de caja diario
- Exportación de datos

### Transacciones
- Formulario para agregar nuevas transacciones
- Lista completa con filtros y búsqueda
- Edición y eliminación de registros
- Categorización automática

### Flujo Mensual
- Análisis de tendencias mensuales
- Comparación de ingresos vs gastos
- Gráficos interactivos

### Categorías
- Gestión completa de categorías
- Estadísticas por categoría
- Configuración de colores

### Reportes
- Reportes detallados por período
- Análisis de gastos por categoría
- Tendencias y proyecciones

## 🔧 Configuración de Desarrollo

### ESLint
El proyecto incluye configuración de ESLint con:
- Reglas de TypeScript
- Plugins para React Hooks
- Configuración para React Refresh

### Tailwind CSS
Configurado para:
- Purging automático de CSS no utilizado
- Soporte completo para componentes React
- Responsive design

## 📱 Responsive Design

La aplicación está completamente optimizada para:
- 📱 Dispositivos móviles
- 📱 Tablets
- 💻 Escritorio

## 🤝 Contribución

1. Fork el proyecto
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📧 Contacto

Para soporte o consultas sobre el proyecto, contacta al equipo de desarrollo.

---

⚡ **Desarrollado con Vite + React + TypeScript** ⚡
