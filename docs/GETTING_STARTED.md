# Guía de Inicio Rápido

Esta guía te ayudará a configurar y ejecutar el Sistema de Flujo de Caja - Bolívar en tu entorno local.

## 📋 Requisitos Previos

### Software Necesario

- **Python 3.12+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** - [Descargar](https://nodejs.org/)
- **PostgreSQL 15+** - [Descargar](https://www.postgresql.org/download/)
- **Git** - [Descargar](https://git-scm.com/downloads/)

### Verificar Instalaciones

```bash
python --version  # Debe ser 3.12 o superior
node --version    # Debe ser 18.x o superior
npm --version     # Incluido con Node.js
psql --version    # PostgreSQL 15 o superior
git --version
```

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd PROYECTO
```

### 2. Configurar Backend

```bash
cd Back-FC

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tu configuración
# Configurar DATABASE_URL, SECRET_KEY, etc.
```

### 3. Configurar Base de Datos

```bash
# Crear base de datos PostgreSQL
psql -U postgres
CREATE DATABASE flujo_caja_db;
CREATE USER fc_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE flujo_caja_db TO fc_user;
\q

# Ejecutar migraciones
cd Back-FC
alembic upgrade head
```

### 4. Configurar Frontend

```bash
cd Front-FC

# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Editar .env
# VITE_API_BASE_URL=http://localhost:8000
```

## ▶️ Ejecutar el Proyecto

### Opción 1: Ejecutar Manualmente

**Terminal 1 - Backend:**
```bash
cd Back-FC
python run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd Front-FC
npm run dev
```

### Opción 2: Usando Scripts (próximamente)

```bash
# Raíz del proyecto
npm run dev    # Ejecuta backend y frontend
npm run backend
npm run frontend
```

## 🌐 Acceder a la Aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Credenciales de Prueba

```
Email: admin@bolivar.com
Password: admin123
```

## ✅ Verificar Instalación

### Backend

```bash
cd Back-FC

# Ejecutar tests
pytest

# Verificar API
curl http://localhost:8000/health
```

### Frontend

```bash
cd Front-FC

# Ejecutar tests
npm test

# Verificar build
npm run build
```

## 🛠️ Desarrollo

### Estructura del Proyecto

```
PROYECTO/
├── Back-FC/           # Backend FastAPI
│   ├── app/
│   │   ├── api/       # Endpoints
│   │   ├── core/      # Configuración
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── schemas/   # Schemas Pydantic
│   │   └── services/  # Lógica de negocio
│   ├── tests/         # Pruebas
│   └── run_server.py
├── Front-FC/          # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── public/
└── docs/              # Documentación
```

### Comandos Útiles

#### Backend

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar servidor en desarrollo
python run_server.py

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=app

# Formatear código
black app/

# Linting
flake8 app/

# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head
```

#### Frontend

```bash
# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build

# Preview de producción
npm run preview

# Ejecutar tests
npm test

# Linting
npm run lint

# Formatear código
npm run format
```

## 🐛 Solución de Problemas

### Backend no inicia

**Error: ModuleNotFoundError**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

**Error: Database connection**
```bash
# Verificar PostgreSQL está corriendo
# Verificar DATABASE_URL en .env
# Verificar usuario y permisos en PostgreSQL
```

### Frontend no compila

**Error: Module not found**
```bash
# Limpiar caché y reinstalar
rm -rf node_modules package-lock.json
npm install
```

**Error: API connection**
```bash
# Verificar VITE_API_BASE_URL en .env
# Verificar backend está corriendo en puerto 8000
```

### Base de Datos

**Resetear base de datos**
```bash
# CUIDADO: Esto borrará todos los datos
dropdb flujo_caja_db
createdb flujo_caja_db
cd Back-FC
alembic upgrade head
python scripts/seed_database.py  # Si existe script de seed
```

## 📚 Próximos Pasos

1. **Explorar la aplicación**: Navega por todas las funcionalidades
2. **Leer documentación**: Revisa `/docs` para más detalles
3. **Configurar IDE**: Instala extensiones recomendadas
4. **Contribuir**: Lee `CONTRIBUTING.md` para contribuir

## 🔗 Enlaces Útiles

- [Documentación Completa](/docs)
- [Guía de API](/docs/api/API.md)
- [Arquitectura](/docs/architecture/PROJECT_STRUCTURE.md)
- [Guía de Seguridad](/docs/security/GUIA_IMPLEMENTACION_SEGURIDAD.md)
- [Migración PostgreSQL](/docs/migrations/MIGRACION_POSTGRESQL.md)

## 💬 Soporte

Si tienes problemas:
1. Revisa la sección de solución de problemas arriba
2. Busca en issues existentes del repositorio
3. Crea un nuevo issue con el template de bug report

---

¡Listo! Ahora deberías tener el sistema corriendo localmente. 🎉
