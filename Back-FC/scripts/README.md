# Scripts del Sistema de Flujo de Caja

Este directorio contiene todos los scripts organizados por funcionalidad.

## 📁 **Estructura:**

### 📊 **`trm/`**
Scripts relacionados con la Tasa Representativa del Mercado (TRM):
- Automatización diaria de TRM
- Obtención desde fuentes oficiales
- Monitoreo y testing

### ⚙️ **`setup/`**
Scripts de configuración inicial:
- Creación de datos iniciales
- Configuración de bancos y compañías
- Generación de hashes de seguridad

### 🗄️ **`migrations/`**
Archivos SQL para migraciones de base de datos:
- Cambios en estructura de tablas
- Actualizaciones de esquema
- Scripts de migración

### 🔧 **`utils/`**
Utilidades de administración:
- Gestión de usuarios
- Scripts de diagnóstico
- Herramientas de mantenimiento

## 🚀 **Uso Rápido:**

```bash
# TRM automática
scripts/trm/start_trm_service.bat

# Configuración inicial
python scripts/setup/create_initial_data.py

# Ver usuarios
python scripts/utils/listar_usuarios_api.py
```

Para más detalles, consulta el README.md de cada subdirectorio.
