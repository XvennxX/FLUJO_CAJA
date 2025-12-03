# 📝 Changelog

Registro de todos los cambios notables del Sistema de Flujo de Caja de Bolívar.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-02

### 🧹 Reorganización del Proyecto

#### ♻️ Reorganizado
- **Estructura de archivos Backend**
  - Movidos archivos `check_*.py` desde `Back-FC/` raíz a `Back-FC/tools/`
  - Movidos archivos `test_*.py` desde `Back-FC/` raíz a `Back-FC/tests/`
  - Movido `debug_cuentas_excel.py` a `Back-FC/tools/`
  - Movido `limpiar_septiembre.py` a `Back-FC/scripts/maintenance/`
  - Movidos documentos `.md` desde `Back-FC/` raíz a `Back-FC/docs/`
    - `MIGRACION_COMPLETADA.md`
    - `MIGRACION_POSTGRESQL.md`
    - `TRM_SYSTEM_DOCUMENTATION.md`

- **Estructura de archivos raíz**
  - Movido `SOLUCION_GMF_AUTOCAL CULO.md` a `docs/SOLUCION_GMF_AUTOCALCULO.md`
  - Eliminado espacio en nombre de archivo

- **Carpeta Excel**
  - Agregado `README.md` con documentación de uso
  - Documentado propósito y formato de archivos

#### 🗑️ Eliminado
- `Back-FC/trm_scraper.log` - Archivo de log que no debería estar versionado
- `Front-FC/debug_sync.html` - Archivo de debug temporal

#### 📝 Actualizado
- **Documentación**
  - `README.md` - Estructura actualizada del proyecto
  - `Back-FC/README.md` - Organización de carpetas backend
  - `docs/PROJECT_STRUCTURE.md` - Documentación completa de estructura
  - `Excel/README.md` - Documentación nueva

- **Configuración**
  - `.gitignore` - Reglas preventivas agregadas:
    - Excluir archivos Excel de cargue (excepto plantillas)
    - Prevenir archivos `debug_*.html/js/py`
    - Prevenir archivos `check_*.py` en raíz de Back-FC
    - Prevenir archivos `test_*.py` en raíz de Back-FC
    - Prevenir archivos `.md` en raíz de Back-FC (excepto README.md)
    - Prevenir archivos `.log` en raíz

#### ✅ Resultado
- Proyecto completamente reorganizado y limpio
- Estructura coherente y predecible
- Documentación actualizada
- Funcionalidad intacta (sin cambios en código de producción)
- Reglas preventivas para mantener organización

---

## [1.0.0] - 2025-08-20

### 🎉 Lanzamiento Inicial

#### ✨ Agregado
- **Sistema TRM Automático**
  - Obtención automática diaria de TRM a las 19:00
  - Múltiples fuentes de datos (Portal gobierno + Banco de la República)
  - Almacenamiento histórico con precisión DECIMAL(18,6)
  - API REST completa para consulta de TRM

- **Backend API REST (FastAPI)**
  - Sistema de autenticación JWT con roles
  - CRUD completo de usuarios, bancos y compañías
  - Gestión de cuentas bancarias con soporte multi-moneda
  - Sistema de auditoría completo
  - Endpoints de flujo de caja con conversión automática TRM
  - Health checks y monitoreo

- **Frontend React + TypeScript**
  - Dashboard principal con tabla de flujo de caja
  - Columnas fijas (sticky) para código y cuenta
  - Dashboards especializados por rol (Mesa, Pagaduría, Tesorería)
  - Sistema de autenticación integrado
  - Modo oscuro/claro con persistencia
  - Responsive design para todos los dispositivos

- **Gestión de Usuarios y Roles**
  - Tres roles principales: Mesa de Dinero, Pagaduría, Tesorería
  - Sistema de permisos granular
  - Gestión de usuarios solo para administradores
  - Auditoría de todas las acciones de usuario

- **Base de Datos Optimizada**
  - Esquema MySQL con relaciones bien definidas
  - Índices optimizados para consultas frecuentes
  - Soporte para múltiples compañías y bancos
  - Historial completo de transacciones

- **Automatización y Scripts**
  - Scripts organizados por categoría (TRM, setup, migrations, utils)
  - Automatización de construcción y despliegue
  - Scripts de verificación y análisis
  - Documentación completa de cada script

- **Documentación Completa**
  - README detallado para cada componente
  - Guías de instalación paso a paso
  - Documentación de API con ejemplos
  - Arquitectura de componentes documentada
  - Estándares de desarrollo definidos

#### 🔧 Configuración
- Variables de entorno para desarrollo y producción
- Configuración optimizada de base de datos
- Settings de VS Code para desarrollo
- Configuración de linting y formateo automático
- .gitignore comprehensivo para ambos proyectos

#### 🛡️ Seguridad
- Autenticación JWT con expiración configurable
- Passwords hasheados con bcrypt
- Middleware de autorización por roles
- CORS configurado para dominios específicos
- Variables sensibles en archivos .env

#### 📊 Características del Dashboard
- Visualización de flujo de caja diario
- Filtros por compañía y banco
- Navegación por fechas con calendario
- Resumen automático de ingresos, egresos y saldo
- Gráficos interactivos con Recharts
- Tabla responsive con scroll horizontal

#### 🔄 Automatización TRM
- Scheduler programado para ejecución diaria
- Fallback automático entre fuentes de datos
- Logs detallados de ejecución
- Monitoreo y alertas de funcionamiento
- API para consulta manual y actualización

#### 🏗️ Arquitectura
- Separación clara Frontend/Backend
- API REST stateless
- Componentes React reutilizables
- Hooks personalizados para lógica de negocio
- Contextos para estado global
- Utilidades organizadas por funcionalidad

#### 📱 UX/UI
- Diseño responsive mobile-first
- Tema corporativo Bolívar
- Iconografía consistente con Lucide React
- Animaciones sutiles y transiciones
- Feedback visual para todas las acciones
- Estados de carga y error bien manejados

#### 🧪 Testing y Calidad
- Linting automático con ESLint
- Scripts de verificación de proyecto
- Análisis de bundle para optimización
- Health checks del sistema
- Monitoreo de performance

### 📋 Usuarios de Prueba Incluidos
- **Mesa de Dinero:** mesadinero@bolivar.com / mesa123
- **Pagaduría:** pagaduria@bolivar.com / pagaduria123
- **Tesorería:** tesoreria@bolivar.com / tesoreria123

### 🗄️ Base de Datos Inicial
- Bancos principales de Colombia configurados
- Compañías: Capitalizadora, Bolívar, Comerciales
- Conceptos de flujo de caja predefinidos
- Estructura optimizada para performance

### 🚀 URLs del Sistema
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## [Unreleased] - Próximas Funcionalidades

### 🔮 Planificado
- [ ] Tests unitarios e integración automatizados
- [ ] CI/CD pipeline con GitHub Actions
- [ ] Notificaciones push en tiempo real
- [ ] Reportes avanzados con exportación
- [ ] PWA (Progressive Web App)
- [ ] Caché con Redis para mejor performance
- [ ] Integración con servicios bancarios externos
- [ ] Dashboard de analytics avanzado
- [ ] Alertas automáticas por email
- [ ] Backup automático a la nube

### 🔄 En Consideración
- [ ] Módulo de presupuestos
- [ ] Proyecciones de flujo de caja
- [ ] Integración con sistemas contables
- [ ] App móvil nativa
- [ ] Módulo de conciliación bancaria automática
- [ ] Integración con APIs bancarias

---

## Formato de Versiones

- **MAJOR.MINOR.PATCH** (ej: 1.2.3)
- **MAJOR:** Cambios incompatibles con versiones anteriores
- **MINOR:** Nuevas funcionalidades compatibles con versiones anteriores
- **PATCH:** Correcciones de bugs compatibles

## Tipos de Cambios

- `✨ Agregado` - Nuevas funcionalidades
- `🔄 Cambiado` - Cambios en funcionalidades existentes
- `🚫 Depreciado` - Funcionalidades que serán eliminadas
- `❌ Eliminado` - Funcionalidades eliminadas
- `🔧 Corregido` - Corrección de bugs
- `🛡️ Seguridad` - Mejoras de seguridad

---

**Nota:** Este archivo se actualiza con cada release. Para ver el progreso actual, revisar la sección [Unreleased].
