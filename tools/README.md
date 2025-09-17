# Tools - Herramientas del Proyecto

Esta carpeta contiene herramientas y scripts de utilidad para el mantenimiento y desarrollo del proyecto.

## Estructura

### `/debug/`
Scripts para debug y análisis del sistema:
- Scripts de análisis de transacciones
- Herramientas de debug de consultas
- Verificadores de datos

### `/setup/`
Scripts de configuración inicial y setup:
- `crear_tabla_festivos.py` - Crear tabla de días festivos
- Scripts de migración y configuración inicial

### `/maintenance/`
Scripts de mantenimiento y limpieza:
- `limpiar_y_reprobar.py` - Script de limpieza y re-ejecución de proyecciones
- Scripts de backup y mantenimiento de datos

### Archivos raíz
- `check-project.*` - Scripts para verificar el estado del proyecto

## Uso

Estos scripts deben ejecutarse desde el directorio raíz del proyecto o ajustar las rutas según corresponda.

⚠️ **Importante**: Siempre hacer backup antes de ejecutar scripts de mantenimiento en producción.