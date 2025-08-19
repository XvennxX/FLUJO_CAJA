# 🏦 Sistema de Flujo de Caja - Backend API

API REST desarrollada con FastAPI para el sistema de gestión de flujo de caja de Bolívar.

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos
1. Crear base de datos MySQL:
```sql
CREATE DATABASE flujo_caja CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Configurar variables de entorno en `.env`:
```properties
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=flujo_caja
SECRET_KEY=tu_clave_secreta_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Crear datos iniciales
```bash
python scripts/create_initial_data.py
```

### 4. Iniciar servidor
```bash
python run_server.py
```

## 📊 Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Usuarios de Prueba

| Rol | Email | Password |
|-----|-------|----------|
| Administrador | admin@bolivar.com | admin123 |
| Tesorería | tesoreria@bolivar.com | tesoreria123 |
| Pagaduría | pagaduria@bolivar.com | pagaduria123 |
| Mesa de Dinero | mesadinero@bolivar.com | mesa123 |

## 🗄️ Estructura de Base de Datos

### Tablas Principales:
- `usuarios` - Gestión de usuarios y roles
- `bancos` - Entidades bancarias
- `companias` - Empresas (Capitalizadora, Bolívar, Comerciales)
- `cuentas_bancarias` - Cuentas por empresa y banco
- `conceptos_flujo_caja` - Categorías de movimientos
- `transacciones_flujo_caja` - Movimientos diarios
- `notificaciones` - Sistema de alertas

## 🔗 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `GET /api/v1/auth/me` - Perfil actual
- `POST /api/v1/auth/logout` - Cerrar sesión

### Usuarios (Solo Administradores)
- `GET /api/v1/users/` - Listar usuarios
- `GET /api/v1/users/{id}` - Obtener usuario
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

## 🏗️ Arquitectura

```
app/
├── api/              # Endpoints REST
├── core/             # Configuración central
├── models/           # Modelos SQLAlchemy
├── schemas/          # Validación Pydantic
├── services/         # Lógica de negocio
└── utils/            # Utilidades
```

## 🔧 Tecnologías

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **MySQL** - Base de datos
- **JWT** - Autenticación
- **BCrypt** - Encriptación de contraseñas
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 📝 Estado del Proyecto

✅ **Completado:**
- Modelos de base de datos
- Sistema de autenticación
- APIs básicas de usuarios
- Configuración de CORS
- Documentación automática

🚧 **En desarrollo:**
- APIs de flujo de caja
- Sistema de notificaciones
- Auditoría y logging
- Reportes y analytics
