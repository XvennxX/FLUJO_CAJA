# 📡 API Reference

Documentación completa de la API REST del Sistema de Flujo de Caja de Bolívar.

## 🔗 **Base URL**

```
Desarrollo: http://localhost:8000/api/v1
Producción: https://tu-dominio.com/api/v1
```

## 🔐 **Autenticación**

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### **Obtener Token**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@bolivar.com",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "Nombre Usuario",
    "email": "usuario@bolivar.com",
    "role": "mesa"
  }
}
```

### **Usar Token en Requests**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 🏛️ **Endpoints de Autenticación**

### **POST /auth/login**
Iniciar sesión y obtener token JWT.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "string",
    "email": "string",
    "role": "mesa|pagaduria|tesoreria"
  }
}
```

### **POST /auth/refresh**
Renovar token JWT.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### **GET /auth/me**
Obtener información del usuario actual.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "string",
  "activo": true,
  "fecha_creacion": "2025-08-20T10:00:00"
}
```

## 👥 **Endpoints de Usuarios**

### **GET /users/**
Listar todos los usuarios (solo administradores).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int): Número de registros a omitir (default: 0)
- `limit` (int): Número máximo de registros (default: 100)
- `role` (string): Filtrar por rol
- `activo` (bool): Filtrar por estado activo

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "string",
    "email": "string",
    "role": "string",
    "activo": true,
    "fecha_creacion": "2025-08-20T10:00:00",
    "ultimo_acceso": "2025-08-20T15:30:00"
  }
]
```

### **POST /users/**
Crear nuevo usuario (solo administradores).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "role": "mesa|pagaduria|tesoreria",
  "activo": true
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "string",
  "activo": true,
  "fecha_creacion": "2025-08-20T10:00:00"
}
```

### **GET /users/{user_id}**
Obtener usuario específico.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "string",
  "activo": true,
  "fecha_creacion": "2025-08-20T10:00:00",
  "ultimo_acceso": "2025-08-20T15:30:00"
}
```

### **PUT /users/{user_id}**
Actualizar usuario.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "role": "mesa|pagaduria|tesoreria",
  "activo": true
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "string",
  "activo": true,
  "fecha_actualizacion": "2025-08-20T16:00:00"
}
```

### **DELETE /users/{user_id}**
Eliminar usuario (soft delete).

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

## 🏦 **Endpoints de Bancos**

### **GET /banks/**
Listar todos los bancos.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "nombre": "Banco de Bogotá",
    "codigo": "001",
    "activo": true,
    "fecha_creacion": "2025-08-20T10:00:00"
  }
]
```

### **POST /banks/**
Crear nuevo banco.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "nombre": "string",
  "codigo": "string",
  "activo": true
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "nombre": "string",
  "codigo": "string",
  "activo": true,
  "fecha_creacion": "2025-08-20T10:00:00"
}
```

### **GET /banks/{bank_id}**
Obtener banco específico.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "nombre": "string",
  "codigo": "string",
  "activo": true,
  "cuentas_bancarias": [
    {
      "id": 1,
      "numero_cuenta": "string",
      "tipo_cuenta": "string",
      "compania": {
        "id": 1,
        "nombre": "string"
      }
    }
  ]
}
```

## 🏢 **Endpoints de Compañías**

### **GET /companies/**
Listar todas las compañías.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "nombre": "Capitalizadora Bolívar",
    "codigo": "CAP",
    "activo": true,
    "fecha_creacion": "2025-08-20T10:00:00"
  }
]
```

### **POST /companies/**
Crear nueva compañía.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "nombre": "string",
  "codigo": "string",
  "activo": true
}
```

## 💳 **Endpoints de Cuentas Bancarias**

### **GET /bank-accounts/all**
Obtener todas las cuentas bancarias con relaciones.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "numero_cuenta": "123456789",
    "tipo_cuenta": "AHORROS",
    "moneda": "COP",
    "saldo_actual": 1000000.00,
    "activo": true,
    "banco": {
      "id": 1,
      "nombre": "Banco de Bogotá",
      "codigo": "001"
    },
    "compania": {
      "id": 1,
      "nombre": "Capitalizadora Bolívar",
      "codigo": "CAP"
    }
  }
]
```

### **GET /bank-accounts/**
Listar cuentas bancarias con filtros.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `banco_id` (int): Filtrar por banco
- `compania_id` (int): Filtrar por compañía
- `moneda` (string): Filtrar por moneda (COP, USD)
- `activo` (bool): Filtrar por estado activo

### **POST /bank-accounts/**
Crear nueva cuenta bancaria.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "numero_cuenta": "string",
  "tipo_cuenta": "AHORROS|CORRIENTE",
  "moneda": "COP|USD",
  "saldo_inicial": 0.0,
  "banco_id": 1,
  "compania_id": 1,
  "activo": true
}
```

## 💰 **Endpoints de TRM (Tasa Representativa del Mercado)**

### **GET /trm/current**
Obtener TRM actual (más reciente).

**Response:** `200 OK`
```json
{
  "fecha": "2025-08-20",
  "valor": 4036.42,
  "fuente": "Portal de datos abiertos",
  "fecha_actualizacion": "2025-08-20T19:00:00"
}
```

### **GET /trm/by-date/{fecha}**
Obtener TRM por fecha específica.

**Parameters:**
- `fecha` (string): Fecha en formato YYYY-MM-DD

**Response:** `200 OK`
```json
{
  "fecha": "2025-08-20",
  "valor": 4036.42,
  "fuente": "Portal de datos abiertos",
  "fecha_actualizacion": "2025-08-20T19:00:00"
}
```

### **GET /trm/range**
Obtener TRM en un rango de fechas.

**Query Parameters:**
- `fecha_inicio` (string): Fecha inicio (YYYY-MM-DD)
- `fecha_fin` (string): Fecha fin (YYYY-MM-DD)
- `limit` (int): Número máximo de registros (default: 100)

**Response:** `200 OK`
```json
[
  {
    "fecha": "2025-08-20",
    "valor": 4036.42,
    "fuente": "Portal de datos abiertos",
    "fecha_actualizacion": "2025-08-20T19:00:00"
  },
  {
    "fecha": "2025-08-19",
    "valor": 4035.20,
    "fuente": "Banco de la República",
    "fecha_actualizacion": "2025-08-19T19:00:00"
  }
]
```

### **POST /trm/**
Crear registro TRM manualmente (solo administradores).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "fecha": "2025-08-20",
  "valor": 4036.42,
  "fuente": "Manual"
}
```

### **DELETE /trm/{fecha}**
Eliminar registro TRM (solo administradores).

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

## 📊 **Endpoints de Transacciones de Flujo de Caja**

### **GET /cash-flow/transactions**
Obtener transacciones de flujo de caja.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `fecha` (string): Fecha específica (YYYY-MM-DD)
- `fecha_inicio` (string): Fecha inicio del rango
- `fecha_fin` (string): Fecha fin del rango
- `compania_id` (int): Filtrar por compañía
- `cuenta_bancaria_id` (int): Filtrar por cuenta bancaria
- `concepto_id` (int): Filtrar por concepto
- `limit` (int): Número máximo de registros

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "fecha": "2025-08-20",
    "concepto": "INGRESOS OPERACIONALES",
    "valor_cop": 1000000.00,
    "valor_usd": 247.70,
    "tipo": "INGRESO",
    "compania": {
      "id": 1,
      "nombre": "Capitalizadora Bolívar",
      "codigo": "CAP"
    },
    "cuenta_bancaria": {
      "id": 1,
      "numero_cuenta": "123456789",
      "banco": {
        "nombre": "Banco de Bogotá"
      }
    },
    "trm_utilizada": 4036.42,
    "fecha_creacion": "2025-08-20T10:00:00"
  }
]
```

### **POST /cash-flow/transactions**
Crear nueva transacción.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "fecha": "2025-08-20",
  "concepto_id": 1,
  "valor": 1000000.00,
  "moneda": "COP",
  "compania_id": 1,
  "cuenta_bancaria_id": 1,
  "observaciones": "string"
}
```

### **GET /cash-flow/summary/{fecha}**
Obtener resumen del flujo de caja por fecha.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "fecha": "2025-08-20",
  "total_ingresos_cop": 5000000.00,
  "total_egresos_cop": 3000000.00,
  "saldo_neto_cop": 2000000.00,
  "total_ingresos_usd": 1238.50,
  "total_egresos_usd": 743.10,
  "saldo_neto_usd": 495.40,
  "trm_utilizada": 4036.42,
  "transacciones_count": 25
}
```

## 🔍 **Endpoints de Auditoría**

### **GET /audit/logs**
Obtener logs de auditoría.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `usuario_id` (int): Filtrar por usuario
- `modulo` (string): Filtrar por módulo
- `accion` (string): Filtrar por acción (CREATE, UPDATE, DELETE)
- `fecha_inicio` (string): Fecha inicio del rango
- `fecha_fin` (string): Fecha fin del rango
- `limit` (int): Número máximo de registros

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "usuario_nombre": "Nombre Usuario",
    "modulo": "usuarios",
    "accion": "CREATE",
    "descripcion": "Usuario creado",
    "valor_anterior": null,
    "valor_nuevo": {
      "name": "Nuevo Usuario",
      "email": "nuevo@bolivar.com",
      "role": "mesa"
    },
    "ip": "192.168.1.100",
    "timestamp": "2025-08-20T10:00:00"
  }
]
```

## 🏥 **Endpoints de Health Check**

### **GET /health**
Verificar estado del sistema.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-08-20T10:00:00",
  "database": "connected",
  "trm_service": "operational",
  "version": "1.0.0",
  "uptime": "72h 30m 15s"
}
```

### **GET /health/detailed**
Estado detallado del sistema.

**Headers:** `Authorization: Bearer <token>` (solo administradores)

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-08-20T10:00:00",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15,
      "connections": {
        "active": 5,
        "total": 200
      }
    },
    "trm_service": {
      "status": "operational",
      "last_update": "2025-08-20T19:00:00",
      "next_update": "2025-08-21T19:00:00",
      "current_trm": 4036.42
    },
    "cache": {
      "status": "healthy",
      "hit_rate": 0.85,
      "memory_usage": "45%"
    }
  },
  "metrics": {
    "requests_per_minute": 120,
    "average_response_time_ms": 250,
    "error_rate": 0.02
  }
}
```

## ⚠️ **Códigos de Error**

### **Códigos HTTP Comunes**

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado |
| 204 | No Content | Recurso eliminado |
| 400 | Bad Request | Datos inválidos |
| 401 | Unauthorized | Token inválido/expirado |
| 403 | Forbidden | Sin permisos |
| 404 | Not Found | Recurso no encontrado |
| 422 | Unprocessable Entity | Error de validación |
| 500 | Internal Server Error | Error del servidor |

### **Estructura de Errores**
```json
{
  "detail": "Descripción del error",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-08-20T10:00:00",
  "path": "/api/v1/users/",
  "errors": [
    {
      "field": "email",
      "message": "El email ya está registrado"
    }
  ]
}
```

## 📝 **Ejemplos de Uso con cURL**

### **Login y obtener token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mesadinero@bolivar.com",
    "password": "mesa123"
  }'
```

### **Obtener TRM actual**
```bash
curl -X GET "http://localhost:8000/api/v1/trm/current"
```

### **Listar usuarios (con token)**
```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### **Crear transacción**
```bash
curl -X POST "http://localhost:8000/api/v1/cash-flow/transactions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-08-20",
    "concepto_id": 1,
    "valor": 1000000.00,
    "moneda": "COP",
    "compania_id": 1,
    "cuenta_bancaria_id": 1
  }'
```

## 🔄 **Rate Limiting**

La API implementa rate limiting para prevenir abuso:

- **Requests por minuto:** 60 por IP
- **Requests por hora:** 1000 por usuario autenticado
- **Headers de respuesta:**
  - `X-RateLimit-Limit`: Límite por ventana
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

## 📊 **Paginación**

Los endpoints que retornan listas soportan paginación:

**Query Parameters:**
- `skip` (int): Registros a omitir (default: 0)
- `limit` (int): Máximo registros por página (default: 100, max: 1000)

**Headers de Respuesta:**
- `X-Total-Count`: Total de registros
- `X-Page-Count`: Total de páginas
- `Link`: Enlaces a páginas anterior/siguiente

## 🔍 **Filtros y Búsqueda**

Muchos endpoints soportan filtros avanzados:

```http
GET /api/v1/cash-flow/transactions?fecha_inicio=2025-08-01&fecha_fin=2025-08-31&compania_id=1&limit=50
```

**Operadores soportados:**
- `eq` (igual): `?campo=valor`
- `gte` (mayor o igual): `?fecha_inicio=2025-08-01`
- `lte` (menor o igual): `?fecha_fin=2025-08-31`
- `like` (contiene): `?search=texto`

---

**Documentación interactiva disponible en:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
