# Visión General del Sistema

Sistema de Flujo de Caja - Bolívar es una aplicación web completa para la gestión y proyección del flujo de caja empresarial, diseñada específicamente para el Banco Bolívar.

## 🎯 Propósito

El sistema permite:
- **Gestión de transacciones financieras** por áreas (Pagaduría, Tesorería, Mesa de Dinero)
- **Proyecciones de flujo de caja** con diferentes horizontes temporales
- **Seguimiento de saldos** en tiempo real
- **Reportes y análisis** financieros
- **Control de usuarios y permisos** basado en roles

## 🏗️ Arquitectura General

### Arquitectura de 3 Capas

```
┌─────────────────────────────────────────────┐
│           FRONTEND (React + TS)             │
│  ┌─────────────────────────────────────┐   │
│  │  Components / Pages / Services      │   │
│  │  Estado: Contexts + Local State     │   │
│  │  Routing: React Router              │   │
│  └─────────────────────────────────────┘   │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST + WebSocket
                  │
┌─────────────────▼───────────────────────────┐
│        BACKEND (FastAPI + Python)           │
│  ┌─────────────────────────────────────┐   │
│  │  API Endpoints (REST)               │   │
│  │  Business Logic (Services)          │   │
│  │  Authentication (JWT)               │   │
│  │  WebSocket (Real-time updates)      │   │
│  └─────────────────────────────────────┘   │
└─────────────────┬───────────────────────────┘
                  │ SQLAlchemy ORM
                  │
┌─────────────────▼───────────────────────────┐
│         BASE DE DATOS (PostgreSQL)          │
│  ┌─────────────────────────────────────┐   │
│  │  Tablas: usuarios, empresas,        │   │
│  │  transacciones, conceptos, etc.     │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## 🎨 Frontend

### Tecnologías
- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **TailwindCSS** - Framework CSS
- **React Router** - Navegación
- **Axios** - Cliente HTTP

### Estructura
```
src/
├── components/        # Componentes reutilizables
│   ├── Layout/       # Layout principal, sidebar, navbar
│   ├── Modals/       # Modales (crear, editar)
│   └── Common/       # Botones, inputs, tablas
├── pages/            # Páginas principales
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Users.tsx
│   ├── Transactions.tsx
│   └── ...
├── contexts/         # Context API (AuthContext, etc.)
├── services/         # Servicios de API
├── hooks/            # Custom hooks
├── types/            # Definiciones TypeScript
├── utils/            # Utilidades
└── config/           # Configuración (API endpoints)
```

### Flujo de Autenticación

```
Usuario ingresa credenciales
         ↓
Login.tsx → AuthContext.login()
         ↓
POST /auth/login (Backend)
         ↓
Backend valida y retorna JWT token
         ↓
Token guardado en localStorage
         ↓
AuthContext actualiza estado (user, isAuthenticated)
         ↓
PrivateRoute permite acceso
```

## 🔧 Backend

### Tecnologías
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de datos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación
- **bcrypt** - Hash de contraseñas
- **WebSockets** - Comunicación en tiempo real

### Estructura
```
app/
├── api/              # Endpoints REST
│   ├── auth.py
│   ├── users.py
│   ├── transacciones.py
│   └── ...
├── core/             # Configuración central
│   ├── config.py     # Settings
│   ├── security.py   # JWT, hashing
│   └── database.py   # Conexión DB
├── models/           # Modelos SQLAlchemy
│   ├── usuario.py
│   ├── empresa.py
│   └── ...
├── schemas/          # Schemas Pydantic
├── services/         # Lógica de negocio
└── main.py           # Aplicación FastAPI
```

### Endpoints Principales

#### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/refresh` - Renovar token

#### Usuarios
- `GET /users` - Listar usuarios
- `POST /users` - Crear usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

#### Transacciones
- `GET /transacciones` - Listar transacciones
- `POST /transacciones` - Crear transacción
- `GET /transacciones/{id}` - Obtener transacción
- `PUT /transacciones/{id}` - Actualizar transacción
- `DELETE /transacciones/{id}` - Eliminar transacción

#### Proyecciones
- `GET /proyecciones/flujo-caja` - Proyección de flujo de caja
- `GET /proyecciones/saldos` - Proyección de saldos

#### WebSocket
- `WS /ws` - Conexión WebSocket para actualizaciones en tiempo real

## 🗄️ Base de Datos

### Modelo de Datos Principal

```
Usuario
├── id (PK)
├── email
├── nombre
├── apellido
├── password_hash
├── rol_id (FK)
└── empresa_id (FK)

Empresa
├── id (PK)
├── nombre
├── codigo
└── activa

Transaccion
├── id (PK)
├── concepto_id (FK)
├── empresa_id (FK)
├── monto
├── fecha
├── area (Pagaduría, Tesorería, etc.)
└── estado

Concepto
├── id (PK)
├── nombre
├── tipo (Ingreso, Egreso)
├── area
└── activo
```

### Relaciones
- Usuario **pertenece a** una Empresa
- Usuario **tiene** un Rol
- Transacción **tiene** un Concepto
- Transacción **pertenece a** una Empresa

## 🔐 Seguridad

### Autenticación
- **JWT (JSON Web Tokens)** para autenticación stateless
- Tokens con expiración configurable
- Refresh tokens para renovación

### Autorización
- **Roles**: Administrador, Tesorería, Pagaduría, Mesa de Dinero
- **Permisos** basados en roles
- Validación en backend para cada endpoint

### Protección de Datos
- Contraseñas hasheadas con bcrypt
- Variables sensibles en archivos .env (no versionados)
- CORS configurado para dominios específicos
- HTTPS en producción

## 🔄 Flujo de Datos Típico

### Crear Transacción

```
1. Usuario completa formulario en frontend
   └→ TransactionForm.tsx

2. Frontend valida datos
   └→ Validación de campos requeridos

3. Frontend envía POST request
   └→ axios.post('/transacciones', data, { headers })

4. Backend recibe request
   └→ Middleware de autenticación valida JWT
   └→ Endpoint valida permisos del usuario
   └→ Service valida datos con Pydantic schema
   └→ Service ejecuta lógica de negocio
   └→ ORM guarda en base de datos

5. Backend retorna respuesta
   └→ Status 201 + datos de transacción creada

6. Frontend actualiza UI
   └→ Agrega transacción a lista local
   └→ Muestra notificación de éxito
   └→ WebSocket notifica a otros usuarios conectados
```

## 📊 Funcionalidades Clave

### 1. Dashboard
- Resumen financiero general
- Gráficos de flujo de caja
- Alertas y notificaciones

### 2. Gestión de Transacciones
- CRUD completo de transacciones
- Filtros por fecha, área, concepto
- Importación/exportación de datos

### 3. Proyecciones
- Proyección de flujo de caja por períodos
- Proyección de saldos
- Diferentes escenarios

### 4. Reportes
- Reportes consolidados
- Exportación a Excel/PDF
- Filtros personalizables

### 5. Administración
- Gestión de usuarios
- Gestión de empresas
- Gestión de conceptos
- Auditoría de cambios

## 🚀 Despliegue

### Desarrollo
- Frontend: `npm run dev` (puerto 5173)
- Backend: `python run_server.py` (puerto 8000)
- Base de datos: PostgreSQL local

### Producción
- Frontend: Build estático servido por Nginx
- Backend: Uvicorn + Gunicorn
- Base de datos: PostgreSQL en servidor dedicado
- Proxy reverso: Nginx
- SSL: Let's Encrypt

## 🔧 Configuración

### Variables de Entorno

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend (.env)**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

## 📈 Escalabilidad

### Estrategias Implementadas
- **Paginación** en listados grandes
- **Caché** de queries frecuentes (futuro)
- **Índices** en base de datos
- **Lazy loading** de componentes
- **Debouncing** en búsquedas

### Mejoras Futuras
- Redis para caché
- CDN para assets estáticos
- Load balancer para backend
- Microservicios por área funcional
- Message queue (RabbitMQ/Celery)

## 🧪 Testing

### Backend
- Pruebas unitarias con pytest
- Pruebas de integración
- Coverage objetivo: >80%

### Frontend
- Pruebas de componentes con Vitest
- Pruebas E2E con Playwright (futuro)
- Coverage objetivo: >70%

## 📚 Recursos Adicionales

- [Guía de Inicio Rápido](./GETTING_STARTED.md)
- [Documentación de API](./api/API.md)
- [Arquitectura Detallada](./architecture/PROJECT_STRUCTURE.md)
- [Guía de Contribución](../CONTRIBUTING.md)

---

Este documento proporciona una visión general del sistema. Para detalles específicos, consulta la documentación técnica correspondiente.
