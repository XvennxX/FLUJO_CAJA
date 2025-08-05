# 🚀 Comandos Útiles para Desarrollo

## 📋 Comandos Básicos

### Iniciar Servidor
```bash
# Desde el directorio Backend/
python main.py

# O con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

## 🗄️ Comandos de Base de Datos

### Configurar Base de Datos desde Cero
```bash
# 1. Crear base de datos
mysql -u root -p < ../Database/scripts/create_database.sql

# 2. Crear tablas
mysql -u root -p < ../Database/scripts/tables.sql

# 3. Crear índices
mysql -u root -p < ../Database/scripts/indexes.sql

# 4. Crear vistas
mysql -u root -p < ../Database/scripts/views.sql

# 5. Cargar datos iniciales
mysql -u root -p < ../Database/seeds/initial_data.sql
```

### Verificar Conexión a BD
```python
# Probar conexión desde Python
python -c "
from app.core.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('✅ Conexión exitosa a MySQL')
except Exception as e:
    print(f'❌ Error de conexión: {e}')
"
```

## 🧪 Comandos de Testing

### Ejecutar Pruebas
```bash
# Todas las pruebas
pytest

# Con cobertura
pytest --cov=app

# Solo pruebas unitarias
pytest tests/unit/

# Solo pruebas de integración
pytest tests/integration/
```

### Probar Endpoints con curl
```bash
# Health check
curl http://localhost:8000/health

# Información de la API
curl http://localhost:8000/

# Login (requiere BD configurada)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@empresa.com&password=admin123"

# Listar usuarios (requiere BD configurada)
curl http://localhost:8000/api/v1/usuarios

# Listar roles (requiere BD configurada)
curl http://localhost:8000/api/v1/roles
```

## 🔧 Comandos de Desarrollo

### Verificar Formato de Código
```bash
# Instalar herramientas de desarrollo
pip install black flake8 isort

# Formatear código
black app/

# Verificar estilo
flake8 app/

# Ordenar imports
isort app/
```

### Generar Requirements
```bash
# Generar requirements.txt actualizado
pip freeze > requirements.txt
```

### Ver Logs en Tiempo Real
```bash
# Con uvicorn y logging detallado
uvicorn main:app --reload --log-level debug
```

## 🐳 Comandos Docker

### Construir Imagen
```bash
# Desde el directorio raíz del proyecto
docker build -f docker/Dockerfile.backend -t flujo-caja-backend .
```

### Ejecutar con Docker Compose
```bash
# Desde el directorio raíz del proyecto
docker-compose -f docker/docker-compose.yml up -d
```

## 📊 URLs de Desarrollo

- **API Base**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔍 Solución de Problemas

### Error de CORS
```bash
# Verificar configuración en .env
echo $BACKEND_CORS_ORIGINS
```

### Error de Módulos
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error de Base de Datos
```bash
# Verificar variables de entorno
cat .env | grep DB_
```

### Reiniciar Servidor con Cambios
```bash
# Ctrl+C para detener, luego:
python main.py
```
