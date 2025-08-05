# 💰 Sistema de Flujo de Caja Empresarial

Sistema completo para gestión de flujo de caja empresarial desarrollado con **React** (Frontend), **FastAPI** (Backend) y **MySQL** (Base de datos).

## 🏗️ Arquitectura del Proyecto

```
FLUJO_CAJA/
├── Front-FC/          # 🎨 Frontend - React
├── Backend/           # 🐍 Backend - FastAPI (Python)
├── Database/          # 🗄️ Scripts y configuración MySQL
├── docs/              # 📚 Documentación
├── docker/            # 🐳 Configuración Docker
└── config/            # ⚙️ Configuraciones
```

## ✨ Funcionalidades

### 🔐 Autenticación y Usuarios
- Sistema de login/logout con JWT
- Gestión de usuarios y roles
- Control de permisos por rol

### 💰 Gestión Financiera
- **Ingresos**: Registro y seguimiento de entradas de dinero
- **Egresos**: Control de gastos y salidas de dinero
- **Conceptos**: Categorización de transacciones
- **Cuentas**: Múltiples cajas/cuentas bancarias

### 📊 Reportes y Análisis
- Resumen diario de movimientos
- Reportes mensuales y comparativos
- Flujo de caja por períodos
- Exportación a PDF/Excel

### 🔍 Auditoría
- Registro de todas las acciones
- Trazabilidad por usuario
- Historial de cambios

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/XvennxX/FLUJO_CAJA.git
cd FLUJO_CAJA
```

### 2. Configurar Base de Datos MySQL
```bash
# 1. Crear la base de datos
mysql -u root -p < Database/scripts/create_database.sql

# 2. Crear las tablas
mysql -u root -p < Database/scripts/tables.sql

# 3. Crear índices
mysql -u root -p < Database/scripts/indexes.sql

# 4. Crear vistas
mysql -u root -p < Database/scripts/views.sql

# 5. Cargar datos iniciales
mysql -u root -p < Database/seeds/initial_data.sql
```

### 3. Configurar Backend (FastAPI)
```bash
cd Backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy ..\config\development.env .env

# Ejecutar servidor de desarrollo
python main.py
```

### 4. Configurar Frontend (React)
```bash
cd Front-FC

# Instalar dependencias
npm install

# Configurar variables de entorno
# Crear archivo .env.local con:
# REACT_APP_API_URL=http://localhost:8000

# Ejecutar servidor de desarrollo
npm start
```

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos
- **JWT**: Autenticación segura
- **MySQL**: Base de datos relacional

### Frontend
- **React**: Librería para interfaces de usuario
- **TypeScript**: Tipado estático
- **Material-UI**: Componentes de interfaz
- **Axios**: Cliente HTTP

### DevOps
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación de servicios
- **Git**: Control de versiones

## 📊 API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/logout` - Cerrar sesión

### Usuarios
- `GET /api/v1/usuarios` - Listar usuarios
- `POST /api/v1/usuarios` - Crear usuario
- `GET /api/v1/usuarios/{id}` - Obtener usuario
- `PUT /api/v1/usuarios/{id}` - Actualizar usuario
- `PATCH /api/v1/usuarios/{id}/estado` - Cambiar estado

### Transacciones
- `GET/POST /api/v1/ingresos` - Gestionar ingresos
- `GET/POST /api/v1/egresos` - Gestionar egresos
- `GET/POST /api/v1/conceptos` - Gestionar conceptos
- `GET/POST /api/v1/cuentas` - Gestionar cuentas

### Reportes
- `GET /api/v1/reportes/diario` - Resumen diario
- `GET /api/v1/reportes/mensual` - Resumen mensual
- `GET /api/v1/reportes/flujo` - Flujo de caja
- `GET /api/v1/reportes/exportar` - Exportar datos

## 🧪 Testing

```bash
# Backend
cd Backend
pytest

# Frontend
cd Front-FC
npm test
```

## 📖 Documentación

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Documentación técnica**: `docs/` folder

## 🐳 Docker

```bash
# Desarrollo
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up

# Producción
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d
```

## 👥 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Contacto

- **Autor**: XvennxX
- **Repositorio**: https://github.com/XvennxX/FLUJO_CAJA
- **Issues**: https://github.com/XvennxX/FLUJO_CAJA/issues

---

⭐ Si este proyecto te resulta útil, ¡dale una estrella!
