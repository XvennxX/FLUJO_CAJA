# 🧪 Guía de Pruebas del API

## 🚀 Estado Actual

✅ **Servidor funcionando**: http://localhost:8000
✅ **Documentación**: http://localhost:8000/docs
✅ **Endpoints básicos implementados**

## 🔗 Endpoints Disponibles para Prueba

### 1. Health Check
```bash
GET http://localhost:8000/health
```

### 2. Información de la API
```bash
GET http://localhost:8000/
```

### 3. Listar Roles
```bash
GET http://localhost:8000/api/v1/roles
```
**Nota**: Este endpoint requiere que la base de datos esté configurada.

### 4. Listar Usuarios
```bash
GET http://localhost:8000/api/v1/usuarios
```
**Nota**: Este endpoint requiere que la base de datos esté configurada.

## 📋 Próximos Pasos

### 1. Configurar Base de Datos MySQL
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

### 2. Actualizar Variables de Entorno
Editar el archivo `.env` en la carpeta Backend con tus credenciales de MySQL:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=flujo_caja
```

### 3. Probar Login (Después de configurar BD)
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@empresa.com&password=admin123
```

## 🛠️ Herramientas Recomendadas

- **Swagger UI**: http://localhost:8000/docs (integrado)
- **ReDoc**: http://localhost:8000/redoc (integrado)
- **Postman**: Para pruebas manuales
- **curl**: Para pruebas rápidas desde terminal

## 📊 Funcionalidades Implementadas

### ✅ Completas
- Sistema de autenticación JWT
- CRUD de usuarios
- Listado de roles
- Validación de datos con Pydantic
- Documentación automática

### 🚧 En Desarrollo
- CRUD de ingresos/egresos
- Gestión de conceptos y cuentas
- Sistema de reportes
- Auditoría completa

## 🐛 Solución de Problemas

### Error de Conexión a BD
Si obtienes errores de conexión a la base de datos:
1. Verifica que MySQL esté ejecutándose
2. Confirma las credenciales en el archivo `.env`
3. Asegúrate de que la base de datos `flujo_caja` exista

### Error de Importaciones
Si hay errores de importación de módulos:
1. Verifica que todas las dependencias estén instaladas
2. Ejecuta desde el directorio `Backend/`
3. Asegúrate de que todos los archivos `__init__.py` existan
