# Backend - API REST

Backend del sistema de flujo de caja desarrollado en Python.

## Estructura

```
Backend/
├── app/
│   ├── api/                # Endpoints de la API
│   │   └── v1/            # Versión 1 de la API
│   │       └── endpoints/ # Controladores específicos
│   ├── core/              # Configuración principal
│   ├── models/            # Modelos de datos (SQLAlchemy)
│   ├── schemas/           # Schemas de Pydantic
│   ├── services/          # Lógica de negocio
│   ├── crud/              # Operaciones CRUD
│   ├── utils/             # Utilidades y helpers
│   └── middleware/        # Middleware personalizado
├── tests/                 # Pruebas unitarias e integración
├── migrations/            # Migraciones de base de datos
├── requirements.txt       # Dependencias de Python
└── main.py               # Punto de entrada de la aplicación
```

## Funcionalidades

- Gestión de ingresos y egresos
- Proyecciones de flujo de caja
- Reportes financieros
- Autenticación y autorización
- API RESTful con documentación automática

## Instalación

```bash
# 1. Navegar al directorio del backend
cd Backend

# 2. Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy ..\config\development.env .env  # Windows
# cp ../config/development.env .env  # Linux/Mac

# 5. Ejecutar servidor
python main.py
```

## URLs Importantes

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Configuración de Base de Datos

Para usar las funcionalidades completas, configura MySQL:

```bash
# 1. Editar archivo .env con tus credenciales de MySQL
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña

# 2. Ejecutar scripts de base de datos
mysql -u root -p < ../Database/scripts/create_database.sql
mysql -u root -p < ../Database/scripts/tables.sql
mysql -u root -p < ../Database/scripts/indexes.sql
mysql -u root -p < ../Database/scripts/views.sql
mysql -u root -p < ../Database/seeds/initial_data.sql
```
