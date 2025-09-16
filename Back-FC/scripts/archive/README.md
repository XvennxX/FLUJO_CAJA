# Sistema de Flujo de Caja - Backend

API REST desarrollada con FastAPI para el sistema de flujo de caja de Bolívar.

## 🏗️ **Estructura del Proyecto**

```
Back-FC/
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints de la API
│   ├── core/              # Configuración y base de datos
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   ├── services/          # Lógica de negocio
│   └── main.py           # Aplicación principal FastAPI
├── scripts/               # Scripts organizados por funcionalidad
│   ├── trm/              # Scripts de TRM (automatización)
│   ├── setup/            # Configuración inicial
│   ├── migrations/       # Migraciones SQL
│   └── utils/            # Utilidades de administración
├── docs/                  # Documentación del proyecto
├── docker/                # Configuración Docker
├── .env                   # Variables de entorno
├── requirements.txt       # Dependencias Python
└── run_server.py         # Servidor de desarrollo
```

## 🚀 **Inicio Rápido**

### 1. Configuración del entorno
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de base de datos
```bash
# Configurar variables de entorno en .env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/flujo_caja

# Crear datos iniciales
python scripts/setup/create_initial_data.py
```

### 3. Ejecutar servidor
```bash
# Desarrollo
python run_server.py

# O usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 **Características Principales**

### 🔐 **Autenticación y Autorización**
- JWT tokens para autenticación
- Roles de usuario (Mesa, Pagaduría, Tesorería)
- Middleware de seguridad

### 🏦 **Gestión Bancaria**
- CRUD completo de bancos
- Gestión de cuentas bancarias
- Soporte para múltiples monedas
- Integración con compañías

### 📈 **TRM Automática**
- Obtención automática diaria de TRM
- Múltiples fuentes oficiales (Gobierno + Banco de la República)
- Almacenamiento histórico
- Scheduler para ejecución a las 7 PM

### 🏢 **Gestión de Compañías**
- CRUD de compañías
- Relación con cuentas bancarias
- Dashboard de flujo de caja

## 🔧 **API Endpoints**

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Renovar token

### Usuarios
- `GET /api/v1/users/` - Listar usuarios
- `POST /api/v1/users/` - Crear usuario
- `PUT /api/v1/users/{id}` - Actualizar usuario

### Bancos
- `GET /api/v1/banks/` - Listar bancos
- `POST /api/v1/banks/` - Crear banco

### Cuentas Bancarias
- `GET /api/v1/bank-accounts/all` - Todas las cuentas con relaciones
- `POST /api/v1/bank-accounts/` - Crear cuenta bancaria

### TRM
- `GET /api/v1/trm/current` - TRM actual
- `GET /api/v1/trm/by-date/{fecha}` - TRM por fecha
- `GET /api/v1/trm/range` - Rango de TRMs

## 🤖 **Automatización TRM**

### Configuración diaria
```bash
# Iniciar servicio automático (Windows)
scripts/trm/start_trm_service.bat

# Actualización manual
scripts/trm/update_trm_now.bat
```

- **Horario**: Diario a las 19:00 (7 PM) hora Colombia
- **Objetivo**: Obtener TRM del día siguiente
- **Fuentes**: Portal de datos abiertos + Banco de la República

## 📚 **Documentación**

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **TRM System**: [docs/TRM_CONFIGURACION_FINAL.md](docs/TRM_CONFIGURACION_FINAL.md)

## 🛠️ **Desarrollo**

### Testing
```bash
# Ejecutar pruebas TRM
python scripts/trm/test_trm.py

# Verificar usuarios
python scripts/utils/listar_usuarios_api.py
```

### Base de datos
```bash
# Migraciones SQL
mysql -u usuario -p flujo_caja < scripts/migrations/archivo.sql
```

## 🔒 **Seguridad**

- Passwords hasheados con bcrypt
- JWT tokens con expiración
- CORS configurado para frontend
- Variables de entorno para datos sensibles

## 📦 **Dependencias Principales**

- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **PyMySQL** - Conector MySQL
- **python-jose** - JWT tokens
- **passlib** - Hashing de passwords
- **schedule** - Programación de tareas

## 🚦 **Estado del Proyecto**

✅ **Funcionalidades Completadas:**
- [x] Autenticación JWT
- [x] CRUD completo de usuarios, bancos y cuentas
- [x] Sistema TRM automático
- [x] API REST completa
- [x] Integración con frontend
- [x] Documentación completa

## 📞 **Soporte**

Para soporte técnico o preguntas sobre el desarrollo, consultar la documentación en la carpeta `docs/` o revisar los logs del sistema.
