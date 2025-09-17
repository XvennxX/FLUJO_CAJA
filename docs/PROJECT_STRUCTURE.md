# Estructura y Organización del Proyecto

Este documento define la estructura organizacional y las mejores prácticas para mantener el proyecto limpio y bien organizado.

## 📁 Estructura de Directorios

### Backend (`Back-FC/`)
```
Back-FC/
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints REST organizados por funcionalidad
│   ├── core/              # Configuración, database, dependencies
│   ├── models/            # Modelos de base de datos (SQLAlchemy)
│   ├── schemas/           # Esquemas Pydantic para validación
│   └── services/          # Lógica de negocio
├── tests/                 # Tests automatizados
│   ├── test_*.py         # Tests organizados por funcionalidad
│   └── README.md         # Documentación de tests
├── scripts/               # Scripts de migración y configuración DB
├── docs/                  # Documentación específica del backend
├── docker/                # Configuración Docker y compose
└── logs/                  # Logs del sistema (no versionados)
```

### Frontend (`Front-FC/`)
```
Front-FC/
├── src/
│   ├── components/        # Componentes React organizados
│   ├── contexts/          # Contextos de React
│   ├── hooks/             # Custom hooks
│   ├── services/          # Servicios para comunicación con API
│   ├── types/             # Tipos TypeScript
│   └── utils/            # Utilidades y helpers
├── scripts/               # Scripts de build y deploy
└── docs/                  # Documentación del frontend
```

### Herramientas (`tools/`)
```
tools/
├── debug/                 # Scripts de análisis y debug
├── setup/                 # Scripts de configuración inicial
├── maintenance/           # Scripts de mantenimiento y limpieza
└── README.md             # Documentación de herramientas
```

## 🚫 Qué NO debe estar en el repositorio

### Archivos temporales
- Scripts de prueba con nombres como `test_temp.py`, `debug_quick.py`
- Archivos de respaldo con extensiones `.bak`, `.backup`
- Logs duplicados en múltiples ubicaciones

### Archivos de configuración local
- `.env` con credenciales reales (usar `.env.example`)
- Configuraciones específicas del IDE
- Archivos de cache temporal

## ✅ Mejores Prácticas

### Nomenclatura de Archivos
- **Tests**: `test_funcionalidad.py`
- **Scripts**: `accion_descripcion.py` (ej: `crear_tabla_festivos.py`)
- **Componentes**: `PascalCase.tsx`
- **Servicios**: `camelCaseService.ts`

### Organización de Código
1. **Backend**: Separar por funcionalidad (API, modelos, servicios)
2. **Frontend**: Componentes en carpetas por funcionalidad
3. **Tests**: Un archivo de test por módulo/servicio
4. **Scripts**: Categorizar por propósito (setup, maintenance, debug)

### Documentación
- Cada carpeta principal debe tener un `README.md`
- Documentar scripts complejos con comentarios
- Mantener documentación actualizada con cambios importantes

## 🧹 Limpieza Regular

### Cada Sprint
- Revisar archivos temporales en `/tools/debug/`
- Eliminar scripts obsoletos
- Actualizar documentación si hay cambios estructurales

### Cada Release
- Limpiar logs antiguos
- Revisar y organizar tests
- Validar que no hay archivos duplicados

## 🔧 Comandos Útiles

### Encontrar archivos duplicados
```bash
# PowerShell
Get-ChildItem -Recurse | Group-Object Name | Where-Object {$_.Count -gt 1}
```

### Limpiar archivos temporales
```bash
# Eliminar archivos .pyc
find . -name "*.pyc" -delete
# Eliminar logs antiguos (más de 30 días)
find ./logs -name "*.log" -mtime +30 -delete
```

## 📝 Checklist de Organización

- [ ] ¿Los scripts están en la carpeta correcta según su propósito?
- [ ] ¿Los tests están organizados por funcionalidad?
- [ ] ¿No hay archivos duplicados innecesarios?
- [ ] ¿La documentación está actualizada?
- [ ] ¿Los logs no están versionados?
- [ ] ¿No hay credenciales en archivos versionados?