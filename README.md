    # 🏦 Sistema de Flujo de Caja - Bolívar

Sistema integral de gestión de flujo de caja desarrollado para Bolívar, que incluye automatización de TRM, dashboards especializados por rol y auditoría completa de operaciones.

## 🏗️ **Estructura del Proyecto**

```
FLUJO_CAJA/
├── 📁 Back-FC/              # Backend - API REST con FastAPI
│   ├── app/                # Código principal de la aplicación
│   ├── tests/              # Tests automatizados (unit + integration)
│   ├── scripts/            # Scripts organizados por funcionalidad
│   │   ├── setup/         # Configuración inicial del sistema
│   │   ├── maintenance/   # Scripts de mantenimiento y corrección
│   │   ├── trm/           # Sistema TRM automático
│   │   ├── utils/         # Utilidades generales
│   │   └── migrations/    # Migraciones de base de datos
│   ├── tools/              # Herramientas de verificación y debug
│   ├── docs/               # Documentación técnica del backend
│   ├── docker/             # Configuración Docker
│   ├── logs/               # Logs del sistema (no versionados)
│   ├── requirements.txt    # Dependencias Python
│   └── README.md          # Documentación del backend
├── 📁 Front-FC/             # Frontend - React + TypeScript
│   ├── src/               # Código fuente React
│   ├── scripts/           # Scripts de build y deploy
│   │   ├── build/         # Scripts de construcción
│   │   ├── deploy/        # Scripts de despliegue
│   │   └── utils/         # Utilidades de análisis
│   ├── docs/              # Documentación del frontend
│   ├── package.json       # Dependencias Node.js
│   └── README.md         # Documentación del frontend
├── 📁 config/               # ⭐ Configuración centralizada
│   ├── docker-compose.yml # Docker Compose para servicios
│   ├── Makefile           # Comandos útiles del proyecto
│   └── README.md         # Documentación de configuración
├── 📁 scripts/              # ⭐ Scripts del proyecto
│   ├── setup/             # Scripts de configuración inicial
│   │   ├── setup.ps1     # Setup para Windows
│   │   └── setup.sh      # Setup para Linux/Mac
│   └── README.md         # Documentación de scripts
├── 📁 tools/                # Herramientas y utilidades
│   ├── debug/             # Scripts de debug y análisis
│   ├── maintenance/       # Scripts de mantenimiento
│   └── README.md         # Documentación de herramientas
├── 📁 docs/                 # Documentación global del proyecto
│   ├── API.md             # Documentación de API
│   ├── GETTING_STARTED.md # Guía de inicio rápido
│   ├── SISTEMA_ROLES_PERMISOS.md # Sistema RBAC
│   ├── SOLUCION_GMF_AUTOCALCULO.md # Sistema GMF
│   ├── api/               # Documentación específica de API
│   ├── architecture/      # Arquitectura del sistema
│   └── development/       # Guías de desarrollo
├── 📁 Excel/                # Archivos Excel para cargue masivo (no versionados)
│   └── README.md          # Documentación de uso
├── 📁 .github/              # Configuración de GitHub (CI/CD, templates)
├── 📁 .venv/               # Entorno virtual Python (local)
├── .editorconfig           # Configuración del editor
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore              # Archivos ignorados por Git
├── CHANGELOG.md            # Historial de cambios
├── CONTRIBUTING.md         # Guía de contribución
├── LICENSE                 # Licencia del proyecto
└── README.md              # Este archivo - Documentación principal
```

## 🚀 **Características Principales**

### 💰 **Sistema TRM Automático**
- ✅ **Actualización diaria** a las 19:00 (7 PM) hora Colombia
- ✅ **Múltiples fuentes** (Portal de datos abiertos + Banco de la República)
- ✅ **Almacenamiento histórico** con precisión DECIMAL(18,6)
- ✅ **API REST** para consulta por fecha, rango y valor actual

### 📊 **Dashboards Especializados**
- 🏛️ **Mesa de Dinero:** Flujo de caja, conciliación, reportes
- 💼 **Pagaduría:** Nómina, pagos a proveedores, usuarios
- 🏦 **Tesorería:** Liquidez, proyecciones, flujo mensual

### 🔐 **Sistema de Autenticación**
- JWT tokens con roles diferenciados
- Gestión segura de sesiones
- Middleware de autorización por endpoints

### 🔍 **Auditoría Completa**
- Log detallado de todas las operaciones
- Trazabilidad de cambios con valores antes/después
- Filtros por usuario, fecha, módulo y acción

## 🛠️ **Stack Tecnológico**

### **Backend (FastAPI)**
- **Python** 3.8+ con FastAPI
- **MySQL** 8.0+ para persistencia
- **SQLAlchemy** ORM para base de datos
- **JWT** para autenticación
- **Schedule** para automatización TRM

### **Frontend (React)**
- **React** 18.3 + TypeScript 5.5
- **Vite** 5.4 como build tool
- **Tailwind CSS** 3.4 para estilos
- **Recharts** para gráficos
- **Lucide React** para iconografía

### **Base de Datos**
- **MySQL** con esquema optimizado
- **Tablas principales:** usuarios, bancos, cuentas_bancarias, trm, transacciones_flujo_caja
- **Relaciones** bien definidas con foreign keys
- **Índices** optimizados para consultas frecuentes

## 🚀 **Inicio Rápido**

### **1. Configuración del Backend**

#### **📋 Prerrequisitos:**
- **Python 3.8+** instalado
- **MySQL 8.0+** corriendo
- **Git** instalado

#### **🚀 Primera vez en un equipo nuevo (Configuración completa):**

```bash
# 1. Clonar repositorio (si no lo has hecho)
git clone <URL_DEL_REPO>
cd FLUJO_CAJA

# 2. Crear entorno virtual en la RAÍZ del proyecto
python -m venv .venv

# 3. Activar entorno virtual (⚠️ IMPORTANTE: desde la raíz del proyecto)
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Git Bash/Linux/Mac:
source .venv/scripts/activate
# Nota: Los warnings "sed: command not found" en Git Bash son normales

# 4. Navegar al backend
cd Back-FC

# 5. Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 9. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de MySQL:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=tu_password
# DB_NAME=flujo_caja
# SECRET_KEY=tu_clave_secreta_muy_larga

# 10. Crear base de datos MySQL
# mysql -u root -p
# CREATE DATABASE flujo_caja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# EXIT;

# 11. Iniciar servidor
python run_server.py
# Backend disponible en: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### **🔄 Uso diario (entorno ya configurado):**
```bash
# Desde la raíz del proyecto FLUJO_CAJA
source .venv/scripts/activate  # Git Bash/Linux/Mac
# O: .venv\Scripts\Activate.ps1  # Windows PowerShell

cd Back-FC
python run_server.py
```

#### **🚨 Solución de Problemas Comunes:**

**Si `pip install -r requirements.txt` falla:**
```bash
# Instalar bcrypt compatible primero
pip install "bcrypt==4.0.1"
# Luego intentar de nuevo
pip install -r requirements.txt
```

**Error "pydantic_settings not found":**
```bash
pip install pydantic pydantic-settings --upgrade
```

**Error de autenticación/login:**
- Verificar que bcrypt sea versión 4.0.1
- Verificar credenciales en la tabla usuarios
- Usar credenciales del README (admin123, etc.)

**Error "No module named 'app'":**
- Verificar que estés en el directorio Back-FC
- Verificar que el entorno virtual esté activado (debe aparecer (.venv))

**Error de conexión MySQL:**
```bash
# Verificar que MySQL esté corriendo
# Windows: services.msc -> MySQL80
# Linux: sudo systemctl status mysql
```

### **2. Configuración del Frontend**
```bash
# Navegar al frontend
cd Front-FC

# Instalar dependencias
npm install

# Verificar configuración
npm run check

# Iniciar desarrollo
npm run dev
# Frontend disponible en: http://localhost:5000
```

### **3. Configuración de Base de Datos**
```sql
-- 1. Conectar a MySQL
mysql -u root -p

-- 2. Crear base de datos
CREATE DATABASE flujo_caja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. Verificar creación
SHOW DATABASES;

-- 4. Salir
EXIT;
```

**Variables de entorno (.env en Back-FC):**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=flujo_caja
SECRET_KEY=tu_clave_secreta_muy_larga_minimo_32_caracteres
```

### **4. Verificación del Sistema**

#### **✅ Verificar que todo funciona:**
```bash
# 1. Verificar backend
curl http://localhost:8000/docs
# Debe abrir Swagger UI

# 2. Verificar autenticación (desde Back-FC con entorno activado)
python scripts/utils/listar_usuarios_api.py

# 3. Verificar TRM
curl http://localhost:8000/api/v1/trm/actual

# 4. Probar login en frontend
# Email: carlos.gomez@flujo.com
# Password: admin123
```

## 🔗 **URLs del Sistema**

### **Desarrollo**
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### **📋 Credenciales de Prueba (Desarrollo - Locales)**

**⚠️ IMPORTANTE:** Estas credenciales solo funcionan después de ejecutar el script de configuración inicial.

| Rol | Usuario | Email | Password | Dashboard |
|-----|---------|-------|----------|-----------|  
| **Administrador** | Carlos Gómez | carlos.gomez@flujo.com | admin123 | Administración completa |
| **Tesorería** | María López | maria.lopez@flujo.com | tesoreria123 | Análisis de liquidez |
| **Pagaduría** | Javier Ruiz | javier.ruiz@flujo.com | pagaduria123 | Gestión de nómina |
| **Mesa de Dinero** | Laura Martínez | laura.martinez@flujo.com | mesa123 | Visualización completa (solo lectura) |

**📝 Crear usuarios iniciales (si no existen):**
```bash
# Desde Back-FC con entorno activado
python scripts/setup/create_initial_data.py
```## 📊 **Funcionalidades por Módulo**

### **🔄 Automatización TRM**
```bash
# Estado actual del servicio
TRM Actual: $4,036.42 COP
Última actualización: Automática 19:00 diaria
Próxima ejecución: Hoy 19:00
Fuentes: Portal Gov + Banco República
```

### **📈 Dashboard Principal**
- Tabla de flujo de caja con **columnas fijas** (código y cuenta)
- Filtros por compañía (Capitalizadora, Bolívar, Comerciales)
- Navegación por fechas con calendario visual
- Resumen automático de ingresos, egresos y saldo neto

### **👥 Gestión de Usuarios**
- CRUD completo (solo administradores)
- Asignación de roles y permisos
- Estados activo/inactivo
- Sistema de auditoría integrado

### **🏢 Gestión de Compañías y Bancos**
- Registro de entidades financieras
- Cuentas bancarias por compañía
- Soporte multi-moneda con conversión TRM

## 🔧 **Scripts y Automatización**

### **Backend Scripts**
```bash
# TRM automático
python scripts/trm/trm_scheduler_simple.py    # Servicio principal
python scripts/trm/test_trm.py                # Pruebas
python scripts/trm/monitor_trm.py             # Monitoreo

# Configuración inicial
python scripts/setup/create_initial_data.py   # Datos iniciales
python scripts/setup/create_test_banks.py     # Bancos de prueba

# Utilidades administrativas
python scripts/utils/listar_usuarios_api.py   # Listar usuarios
python scripts/utils/verify_system_status.py  # Estado del sistema
```

### **Frontend Scripts**
```bash
# Desarrollo
npm run dev              # Servidor desarrollo
npm run check           # Verificar proyecto
npm run lint            # Verificar código

# Producción
npm run build:prod      # Construcción optimizada
npm run analyze         # Analizar bundle
scripts/build/build-prod.bat  # Script Windows
```

## 📚 **Documentación**

### **Documentación del Backend**
- [📖 README Backend](Back-FC/README.md) - Guía completa del backend
- [🔧 Configuración TRM](Back-FC/docs/TRM_CONFIGURACION_FINAL.md) - Sistema TRM
- [📁 Scripts organizados](Back-FC/scripts/) - Documentación por categoría

### **Documentación del Frontend**
- [📖 README Frontend](Front-FC/README.md) - Guía completa del frontend
- [🏗️ Arquitectura](Front-FC/docs/ARQUITECTURA_COMPONENTES.md) - Componentes React
- [💻 Desarrollo](Front-FC/docs/DESARROLLO.md) - Estándares y prácticas

### **Documentación Global**
- [🚀 Guía de Instalación](docs/INSTALACION.md) - Setup completo del sistema
- [🔧 Configuración](docs/CONFIGURACION.md) - Variables y ajustes
- [📊 API Reference](docs/API.md) - Documentación de endpoints

## 🚦 **Estado del Proyecto**

### ✅ **Completado (Desarrollo - Pruebas Locales)**
- [x] Sistema TRM automático (programado 19:00 diario)
- [x] Backend API REST completa con FastAPI
- [x] Frontend React con TypeScript + Vite
- [x] Sistema de autenticación JWT con roles (Admin, Tesorería, Pagaduría, Mesa)
- [x] Dashboards especializados por rol implementados
- [x] Gestión completa de usuarios y auditoría
- [x] Tabla de flujo de caja con columnas fijas optimizadas
- [x] Integración TRM en tiempo real con múltiples fuentes
- [x] Cálculo automático de GMF (4x1000) con persistencia
- [x] Scripts organizados por funcionalidad y documentados
- [x] Base de datos MySQL optimizada con índices
- [x] Sistema de cargue masivo desde Excel
- [x] Migración completada de MySQL (validada y funcional)
- [x] Proyecto reorganizado con estructura profesional

### 🔄 **En Monitoreo**
- Sistema TRM ejecutándose automáticamente
- Logs de auditoría activos
- Performance monitoring activo

### 📈 **Futuras Mejoras**
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Notificaciones push
- [ ] Reportes avanzados
- [ ] PWA (Progressive Web App)

## 🛡️ **Seguridad**

- **Autenticación:** JWT con expiración configurada
- **Autorización:** Middleware por roles
- **Base de datos:** Parámetros preparados (SQL injection protection)
- **Frontend:** Sanitización de inputs
- **CORS:** Configurado para dominios específicos
- **Variables sensibles:** Almacenadas en archivos .env

## 🛠️ **Comandos Útiles de Desarrollo**

### **Backend (desde Back-FC con entorno activado):**
```bash
# Listar usuarios del sistema
python scripts/utils/listar_usuarios_api.py

# Verificar estado del sistema
python scripts/utils/verify_system_status.py

# Probar TRM manualmente
python scripts/trm/test_trm.py

# Crear datos iniciales
python scripts/setup/create_initial_data.py

# Ver logs en tiempo real
tail -f logs/app.log  # Linux/Mac
# Windows: abrir logs/app.log en editor
```

### **Frontend (desde Front-FC):**
```bash
# Verificar configuración
npm run check

# Linter
npm run lint

# Build para producción
npm run build:prod

# Analizar bundle
npm run analyze
```

### **Base de Datos:**
```bash
# Conectar a MySQL
mysql -u root -p flujo_caja

# Ver tablas
SHOW TABLES;

# Ver usuarios
SELECT id, nombre, email, rol FROM usuarios;

# Ver TRM actual
SELECT * FROM trm ORDER BY fecha DESC LIMIT 5;
```

## 📞 **Soporte y Contacto**

### **Desarrollo**
Para consultas técnicas o problemas:
1. **Verificar configuración:** Seguir pasos de "Solución de Problemas Comunes"
2. **Revisar logs:** `Back-FC/logs/app.log`
3. **Verificar servicios:** MySQL corriendo, puertos 8000 y 5000 disponibles
4. **Comandos de diagnóstico:** Scripts en `scripts/utils/`

### **URLs de Acceso**
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Base de datos:** MySQL `flujo_caja` en puerto 3306

### **Estructura de Archivos Importante**
```
FLUJO_CAJA/
├── .venv/                    # ⚠️ Entorno virtual (RAÍZ del proyecto)
├── Back-FC/
│   ├── .env                  # Variables de entorno (crear desde .env.example)
│   ├── logs/app.log         # Logs del sistema
│   └── run_server.py        # Servidor principal
└── Front-FC/
    └── package.json         # Dependencias Node.js
```

---

**Versión:** 1.0.1  
**Última actualización:** 2 de Diciembre de 2025  
**Estado:** 🟢 Desarrollo - Pruebas Locales  
**Autor:** Sistema de Flujo de Caja Bolívar  
**Licencia:** Propietario - Bolívar  

---

## 🎯 **Resumen Ejecutivo**

Este sistema representa una **solución completa** para la gestión automatizada del flujo de caja de Bolívar, con características empresariales como:

- ⚡ **Automatización TRM** para conversiones precisas
- 📊 **Dashboards especializados** por área de negocio  
- 🔐 **Seguridad empresarial** con auditoría completa
- 🚀 **Arquitectura escalable** con tecnologías modernas
- 📱 **Interfaz responsive** optimizada para todos los dispositivos

**Estado actual:** 🟢 **DESARROLLO - PRUEBAS LOCALES** - Sistema completamente funcional en entorno de desarrollo, validado y listo para siguientes fases de testing y despliegue.
