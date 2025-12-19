# DOCUMENTACIÓN TÉCNICA COMPLETA
## SISTEMA DE FLUJO DE CAJA - BOLÍVAR

---

**Versión**: 1.0.0  
**Fecha de Documentación**: 18 de Diciembre de 2025  
**Estado del Proyecto**: Desarrollo y Pruebas Locales  

---

## 📋 ÍNDICE GENERAL

### Documentos Técnicos

| # | Documento | Descripción | Páginas |
|---|-----------|-------------|---------|
| 01 | [MODELO-ENTIDAD-RELACION.md](01-MODELO-ENTIDAD-RELACION.md) | Diagrama ER, entidades, relaciones, cardinalidades y enums | ~150 |
| 02 | [DEFINICIONES-FISICAS-TABLAS.md](02-DEFINICIONES-FISICAS-TABLAS.md) | DDL completo de todas las tablas, índices y constraints | ~200 |
| 03 | [ARQUITECTURA-BACKEND.md](03-ARQUITECTURA-BACKEND.md) | Servicios, modelos, APIs, autenticación y configuración | ~400 |
| 04 | [ARQUITECTURA-FRONTEND.md](04-ARQUITECTURA-FRONTEND.md) | Componentes React, contextos, hooks y configuración | ~350 |
| 05 | [SCRIPTS-HERRAMIENTAS.md](05-SCRIPTS-HERRAMIENTAS.md) | Scripts de setup, migración, mantenimiento y TRM | ~200 |

---

## 🏢 INFORMACIÓN DEL PROYECTO

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Nombre del Proyecto** | Sistema de Flujo de Caja Diario |
| **Cliente** | Bolívar |
| **Tecnología Backend** | Python 3.9+ / FastAPI 0.104.1+ |
| **Tecnología Frontend** | React 18.3.1 / TypeScript / Vite 5.4.2 |
| **Base de Datos** | MySQL 8.0+ con InnoDB |
| **Autenticación** | JWT (JSON Web Tokens) |
| **Arquitectura** | REST API + SPA |

### Estructura del Repositorio

```
PROYECTO/
├── Back-FC/                    # Backend FastAPI
│   ├── app/                    # Código fuente principal
│   │   ├── api/               # Endpoints REST
│   │   ├── core/              # Configuración y utilidades
│   │   ├── middleware/        # Middlewares de autenticación
│   │   ├── models/            # Modelos SQLAlchemy (14 entidades)
│   │   ├── schemas/           # Schemas Pydantic
│   │   └── services/          # Lógica de negocio
│   ├── scripts/               # Scripts de automatización
│   ├── tests/                 # Pruebas unitarias e integración
│   └── docker/                # Configuración Docker
│
├── Front-FC/                   # Frontend React
│   ├── src/                   # Código fuente
│   │   ├── components/        # Componentes React
│   │   ├── contexts/          # Contextos de estado global
│   │   ├── hooks/             # Hooks personalizados
│   │   ├── pages/             # Páginas/vistas
│   │   ├── services/          # Servicios API
│   │   └── types/             # Tipos TypeScript
│   └── public/                # Archivos estáticos
│
├── config/                     # Configuración Docker y Makefile
├── docs/                       # Documentación general
├── Excel/                      # Plantillas Excel
├── backups/                    # Respaldos de base de datos
└── documentacion-entrega/      # Esta documentación técnica
```

---

## 📊 RESUMEN DEL MODELO DE DATOS

### Entidades Principales (14 tablas)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MODELO ENTIDAD-RELACIÓN                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐     ┌──────────┐     ┌─────────────────────────┐  │
│   │  USUARIOS   │────>│   ROL    │────>│       PERMISOS          │  │
│   │ (14 campos) │     │(7 campos)│     │      (7 campos)         │  │
│   └─────────────┘     └──────────┘     └─────────────────────────┘  │
│          │                                                          │
│          v                                                          │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              TRANSACCIONES_FLUJO_CAJA                       │   │
│   │                    (17 campos)                              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│          │                    │                    │                │
│          v                    v                    v                │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │  CONCEPTOS   │    │   CUENTAS    │    │  COMPAÑÍAS   │         │
│   │ (15 campos)  │    │ BANCARIAS    │    │ (10 campos)  │         │
│   └──────────────┘    │ (15 campos)  │    └──────────────┘         │
│                       └──────────────┘                              │
│                              │                                      │
│                              v                                      │
│                       ┌──────────────┐    ┌──────────────┐          │
│                       │    BANCOS    │    │     TRM      │          │
│                       │ (7 campos)   │    │ (3 campos)   │          │
│                       └──────────────┘    └──────────────┘          │
│                                                                     │
│   Otras entidades: GMF_CONFIG, AUDITORIA, NOTIFICACIONES           │
│                    CUENTA_MONEDA, ROL_PERMISO                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Tipos Enumerados

| Enum | Valores | Uso |
|------|---------|-----|
| `TipoMovimiento` | ingreso, egreso, neutral | Conceptos de flujo |
| `AreaConcepto` | tesoreria, pagaduria, ambas | Áreas de conceptos |
| `TipoDependencia` | copia, suma, resta | Dependencias automáticas |
| `AreaTransaccion` | tesoreria, pagaduria, consolidado | Transacciones |
| `TipoCuenta` | corriente, ahorros, fiducia | Cuentas bancarias |

---

## 🔐 SISTEMA DE SEGURIDAD

### Autenticación JWT

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLUJO DE AUTENTICACIÓN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Login              2. Validación          3. Token          │
│  ┌──────────┐         ┌──────────────┐       ┌─────────────┐   │
│  │ Usuario  │ ──────> │ Verificar    │ ────> │ Generar     │   │
│  │ /password│         │ credenciales │       │ JWT Token   │   │
│  └──────────┘         │ + bcrypt     │       │ (30 min)    │   │
│                       └──────────────┘       └─────────────┘   │
│                                                     │          │
│  4. Uso                5. Renovación               │          │
│  ┌──────────────┐     ┌──────────────┐             │          │
│  │ Incluir      │ <── │ Refresh      │ <───────────┘          │
│  │ Authorization│     │ Token        │                        │
│  │ Header       │     │ (7 días)     │                        │
│  └──────────────┘     └──────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Sistema RBAC (Role-Based Access Control)

| Rol | Código | Permisos | Descripción |
|-----|--------|----------|-------------|
| **Administrador** | ADMIN | 35+ (todos) | Acceso total al sistema |
| **Tesorería** | TESORERIA | 12 | Gestión de tesorería y flujo de caja |
| **Pagaduría** | PAGADURIA | 12 | Gestión de pagaduría y nómina |
| **Mesa de Dinero** | MESA_DINERO | 9 | Operaciones de mesa de dinero |
| **Consulta** | CONSULTA | 7 | Solo visualización |

### Módulos de Permisos

```
usuarios.*       → ver, crear, editar, eliminar, cambiar_estado
roles.*          → ver, crear, editar, eliminar
transacciones.*  → ver, crear, editar, eliminar, aprobar
conceptos.*      → ver, crear, editar, eliminar
cuentas.*        → ver, crear, editar, eliminar
companias.*      → ver, crear, editar, eliminar
reportes.*       → ver, exportar
auditoria.*      → ver
configuracion.*  → ver, editar
trm.*            → ver, editar
```

---

## 🔧 ARQUITECTURA TÉCNICA

### Backend (FastAPI)

```
┌───────────────────────────────────────────────────────────────┐
│                        BACKEND STACK                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐                                          │
│  │    FastAPI      │  Framework web asíncrono                 │
│  │    0.104.1+     │  Documentación automática OpenAPI        │
│  └────────┬────────┘                                          │
│           │                                                   │
│  ┌────────▼────────┐                                          │
│  │   SQLAlchemy    │  ORM para MySQL                          │
│  │     2.0+        │  Modelos declarativos + relaciones       │
│  └────────┬────────┘                                          │
│           │                                                   │
│  ┌────────▼────────┐                                          │
│  │    MySQL 8.0    │  Base de datos relacional                │
│  │    InnoDB       │  Transacciones ACID                      │
│  └─────────────────┘                                          │
│                                                               │
│  Librerías adicionales:                                       │
│  • python-jose (JWT)  • bcrypt (hashing)                      │
│  • pydantic (validación) • aiomysql (async DB)               │
│  • websockets (tiempo real) • openpyxl (Excel)               │
└───────────────────────────────────────────────────────────────┘
```

### Frontend (React)

```
┌───────────────────────────────────────────────────────────────┐
│                        FRONTEND STACK                         │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐                                          │
│  │   React 18.3    │  Biblioteca UI con hooks y contextos     │
│  │   TypeScript    │  Tipado estático para seguridad          │
│  └────────┬────────┘                                          │
│           │                                                   │
│  ┌────────▼────────┐                                          │
│  │   Vite 5.4.2    │  Build tool ultrarrápido                 │
│  │   + HMR         │  Hot Module Replacement                  │
│  └────────┬────────┘                                          │
│           │                                                   │
│  ┌────────▼────────┐                                          │
│  │ Tailwind CSS    │  Estilos utility-first                   │
│  │    3.4.1        │  Dark mode incluido                      │
│  └─────────────────┘                                          │
│                                                               │
│  Librerías adicionales:                                       │
│  • React Router DOM (navegación)                              │
│  • Recharts (gráficos)                                        │
│  • Lucide React (iconos)                                      │
│  • Axios (HTTP client)                                        │
└───────────────────────────────────────────────────────────────┘
```

---

## 📡 API REST

### Endpoints Principales

| Módulo | Base URL | Métodos | Autenticación |
|--------|----------|---------|---------------|
| Auth | `/api/auth/` | POST login, refresh | Público |
| Usuarios | `/api/usuarios/` | GET, POST, PUT, DELETE | JWT + RBAC |
| Roles | `/api/roles/` | GET, POST, PUT, DELETE | JWT + RBAC |
| Transacciones | `/api/transacciones/` | GET, POST, PUT, DELETE | JWT + RBAC |
| Conceptos | `/api/conceptos/` | GET, POST, PUT, DELETE | JWT + RBAC |
| Cuentas | `/api/cuentas-bancarias/` | GET, POST, PUT, DELETE | JWT + RBAC |
| Compañías | `/api/companias/` | GET, POST, PUT, DELETE | JWT + RBAC |
| TRM | `/api/trm/` | GET, POST, PUT | JWT + RBAC |
| Reportes | `/api/reportes/` | GET | JWT + RBAC |
| Dashboard | `/api/dashboard/` | GET | JWT |

### Formato de Respuesta Estándar

```json
{
  "success": true,
  "data": { ... },
  "message": "Operación exitosa",
  "timestamp": "2025-12-18T10:30:00Z"
}
```

### Formato de Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Datos inválidos",
    "details": [...]
  },
  "timestamp": "2025-12-18T10:30:00Z"
}
```

---

## 💱 SISTEMA TRM AUTOMÁTICO

### Flujo de Obtención

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA TRM AUTOMÁTICO                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  7:00 PM           Datos Abiertos             BanRep            │
│  ┌───────┐        ┌─────────────┐         ┌───────────┐        │
│  │ CRON  │──────> │ Fuente 1    │──────── │ Fallback  │        │
│  │ Task  │        │ datos.gov.co│         │ banrep.co │        │
│  └───────┘        └──────┬──────┘         └─────┬─────┘        │
│                          │                      │               │
│                          └──────────┬───────────┘               │
│                                     v                           │
│                          ┌──────────────────┐                   │
│                          │  VALIDACIÓN      │                   │
│                          │  • Fecha oficial │                   │
│                          │  • Valor > 0     │                   │
│                          └────────┬─────────┘                   │
│                                   v                             │
│                          ┌──────────────────┐                   │
│                          │  GUARDAR EN BD   │                   │
│                          │  Tabla: trm      │                   │
│                          └──────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Fuentes de Datos

1. **Datos Abiertos Colombia** (principal)
   - URL: `https://www.datos.gov.co/resource/32sa-8pi3.json`
   - Formato: JSON
   - Actualización: Diaria

2. **Banco de la República** (fallback)
   - URL: API estadísticas económicas
   - Formato: JSON
   - Actualización: Diaria

---

## 📋 REQUISITOS DEL SISTEMA

### Servidor Backend

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 2 GB | 4 GB |
| Disco | 10 GB | 20 GB SSD |
| SO | Ubuntu 20.04+ / Windows Server 2019+ | Ubuntu 22.04 |

### Servidor Base de Datos

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| MySQL | 8.0 | 8.0.35+ |
| RAM dedicada | 1 GB | 4 GB |
| Disco | 20 GB | 50 GB SSD |

### Cliente (Frontend)

| Navegador | Versión Mínima |
|-----------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

---

## 🚀 DESPLIEGUE LOCAL (DESARROLLO)

### Opción 1: Ejecución Directa (Desarrollo)

```bash
# Backend
cd Back-FC
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python run_server.py

# Frontend (otra terminal)
cd Front-FC
npm install
npm run dev
```

### Opción 2: Con Docker

```bash
# Construir imágenes
cd config
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Servicios Docker

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| backend | 8000 | API FastAPI |
| frontend | 3000 | React SPA |
| mysql | 3306 | Base de datos |

### Variables de Entorno (Desarrollo Local)

```env
# Backend (.env)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flujo_caja
SECRET_KEY=clave-desarrollo-local
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=true

# Frontend (.env.local)
VITE_API_URL=http://localhost:8000/api
```

> **Nota**: En ambiente de desarrollo, DEBUG=true habilita logs detallados y documentación Swagger en `/docs`.

---

## 📞 CONTACTO Y SOPORTE

### Equipo de Desarrollo

| Rol | Contacto |
|-----|----------|
| Desarrollo | Equipo Backend/Frontend |
| Infraestructura | Equipo DevOps |
| Base de Datos | DBA |

### Documentación Adicional

- [README Principal](../README.md)
- [Guía de Instalación](../docs/INSTALACION.md)
- [Configuración](../docs/CONFIGURACION.md)
- [API Documentation](../docs/API.md)

---

## 📝 HISTORIAL DE VERSIONES

| Versión | Fecha | Cambios | Estado |
|---------|-------|---------|--------|
| 1.0.0-dev | 2025-12-18 | Documentación técnica completa para entrega | Desarrollo |
| 0.9.0-dev | 2025-12-01 | Sistema RBAC implementado | Desarrollo |
| 0.8.0-dev | 2025-11-15 | Sistema TRM automático | Desarrollo |
| 0.7.0-dev | 2025-11-01 | Frontend React completado | Desarrollo |
| 0.5.0-dev | 2025-10-01 | API REST core | Desarrollo |
| 0.1.0-dev | 2025-08-01 | Modelo de datos inicial | Desarrollo |

> **Estado actual**: El proyecto se encuentra en fase de **desarrollo y pruebas locales**. No ha sido desplegado en ambiente de producción.

---

**Fin de la Documentación Técnica**

*Sistema de Flujo de Caja - Bolívar*  
*Generado: 18 de Diciembre de 2025*