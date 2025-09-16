# 📁 Estructura del Proyecto - Back-FC

## 🏗️ Directorios Principales

### `/app/` - **Código Principal de la Aplicación**
- `api/` - Endpoints REST
- `core/` - Configuración y base de datos  
- `models/` - Modelos SQLAlchemy
- `schemas/` - Esquemas Pydantic
- `services/` - Lógica de negocio

### `/scripts/` - **Scripts de Utilidad**
- `utils/` - Herramientas útiles (ej: `update_trm_now.py`)
- `tests/` - Scripts de pruebas y testing
- `debug/` - Herramientas de análisis y debugging  
- `maintenance/` - Scripts de mantenimiento y fixes
- `archive/` - Código experimental/obsoleto archivado
- `migrations/` - Migraciones de base de datos
- `setup/` - Scripts de configuración inicial

### `/docs/` - **Documentación**
- Documentación técnica del sistema
- Configuración TRM
- Guías de sistema

### `/docker/` - **Configuración de Contenedores**
- Archivos Docker para despliegue

### `/logs/` - **Archivos de Log**
- Logs del sistema y aplicación

## 🚀 Archivos en Raíz

- `run_server.py` - **Script principal para iniciar el servidor**
- `requirements.txt` - Dependencias Python
- `.env` - Variables de entorno (no versionado)
- `.gitignore` - Archivos ignorados por git

## 🧹 Reorganización Completada

✅ **Movidos a `/scripts/tests/`:**
- Todos los archivos `test_*.py`
- Scripts de bash `test_completo.*`

✅ **Movidos a `/scripts/debug/`:**
- Archivos `debug_*.py`
- Archivos `diagnostico*.py`
- Archivos `analizar*.py`
- Archivos `verificar*.py`
- Archivos `ver_*.py`

✅ **Movidos a `/scripts/maintenance/`:**
- Archivos `fix_*.py`
- Archivos `arreglar*.py`
- Archivos `recalcular*.py`
- Archivos `limpiar*.py`

✅ **Movidos a `/scripts/archive/`:**
- Archivos `implementar*.py`
- Archivos `configurar*.py`  
- Archivos `probar*.py`
- Archivos `crear*.py`
- Documentos temporales `*.md`

✅ **Movidos a `/scripts/utils/`:**
- `update_trm_now.py` - Actualización manual de TRM

✅ **Movidos a `/logs/`:**
- Todos los archivos `*.log`

## 📝 Notas de Uso

- **Desarrollo diario:** Usar solo archivos en `/app/` y `run_server.py`
- **Testing:** Scripts disponibles en `/scripts/tests/`
- **Debug:** Herramientas en `/scripts/debug/`
- **Mantenimiento:** Scripts en `/scripts/maintenance/`
- **Consulta histórica:** Código archivado en `/scripts/archive/`