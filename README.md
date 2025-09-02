# 🏦 Sistema de Flujo de Caja - Bolívar

Sistema integral de gestión de flujo de caja desarrollado para Bolívar, que incluye automatización de TRM, dashboards especializados por rol y auditoría completa de operaciones.

## 🏗️ **Estructura del Proyecto**

```
FLUJO_CAJA/
├── 📁 Back-FC/              # Backend - API REST con FastAPI
│   ├── app/                # Código principal de la aplicación
│   ├── scripts/            # Scripts organizados (TRM, setup, utils)
│   ├── docs/               # Documentación del backend
│   ├── requirements.txt    # Dependencias Python
│   └── README.md          # Documentación del backend
├── 📁 Front-FC/             # Frontend - React + TypeScript
│   ├── src/               # Código fuente React
│   ├── scripts/           # Scripts de build y deploy
│   ├── docs/              # Documentación del frontend
│   ├── package.json       # Dependencias Node.js
│   └── README.md         # Documentación del frontend
├── 📁 docs/                 # Documentación global del proyecto
├── 📁 .venv/               # Entorno virtual Python (local)
├── .gitignore              # Archivos ignorados por Git
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
```bash
# Navegar al backend
cd Back-FC

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (crear .env con credenciales)
python scripts/setup/create_initial_data.py

# Iniciar servidor
python run_server.py
# Backend disponible en: http://localhost:8000
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
-- Crear base de datos
CREATE DATABASE flujo_caja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Variables de entorno (.env en Back-FC)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=flujo_caja
SECRET_KEY=tu_clave_secreta
```

## 🔗 **URLs del Sistema**

### **Desarrollo**
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### **Usuarios de Prueba**
| Rol | Email | Password | Dashboard |
|-----|-------|----------|-----------|
| Mesa de Dinero | mesadinero@bolivar.com | mesa123 | Flujo de caja principal |
| Pagaduría | pagaduria@bolivar.com | pagaduria123 | Gestión de nómina |
| Tesorería | tesoreria@bolivar.com | tesoreria123 | Análisis de liquidez |

## 📊 **Funcionalidades por Módulo**

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

### ✅ **Completado (Producción Ready)**
- [x] Sistema TRM automático (programado 19:00 diario)
- [x] Backend API REST completa
- [x] Frontend React con TypeScript
- [x] Sistema de autenticación JWT
- [x] Dashboards por rol implementados
- [x] Gestión de usuarios y auditoría
- [x] Tabla de flujo con columnas fijas
- [x] Integración TRM en tiempo real
- [x] Scripts organizados y documentados
- [x] Base de datos optimizada

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

## 📞 **Soporte y Contacto**

### **Desarrollo**
Para consultas técnicas o problemas:
1. Revisar documentación específica en `/docs`
2. Ejecutar scripts de verificación (`npm run check`, etc.)
3. Consultar logs del sistema
4. Verificar conectividad backend-frontend

### **Datos de Contacto del Sistema**
- **TRM Service:** Automático 19:00 diaria
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5000
- **Base de datos:** MySQL flujo_caja

---

**Versión:** 1.0.0  
**Última actualización:** Agosto 2025  
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

**Estado actual:** ✅ **PRODUCCIÓN READY** - Sistema configurado y funcionando automáticamente.
