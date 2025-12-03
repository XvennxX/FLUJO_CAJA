# Estructura y Organización del Proyecto

Este documento define la estructura organizacional y las mejores prácticas para mantener el proyecto limpio y bien organizado.

---

## 📅 **Última Actualización:** 2 de diciembre de 2025
- ✅ Reorganización completa de archivos fuera de lugar
- ✅ Limpieza de archivos temporales y logs
- ✅ Actualización de .gitignore con reglas preventivas
- ✅ Documentación de carpetas actualizada

---

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
│   ├── unit/             # Tests unitarios
│   ├── integration/      # Tests de integración
│   ├── test_*.py         # Tests organizados por funcionalidad
│   └── README.md         # Documentación de tests
├── scripts/               # Scripts organizados por categoría
│   ├── setup/            # Configuración inicial del sistema
│   ├── maintenance/      # Mantenimiento y correcciones
│   ├── trm/              # Sistema TRM automático
│   ├── utils/            # Utilidades generales
│   ├── migration/        # Migraciones de base de datos
│   ├── debug/            # Scripts de debugging
│   └── archive/          # Código histórico archivado
├── tools/                 # Herramientas de verificación
│   ├── check_*.py        # Scripts de verificación de datos
│   ├── debug_*.py        # Scripts de análisis y debug
│   └── README.md         # Documentación de herramientas
├── docs/                  # Documentación específica del backend
│   ├── TRM_SYSTEM_DOCUMENTATION.md
│   ├── MIGRACION_POSTGRESQL.md
│   ├── MIGRACION_COMPLETADA.md
│   └── *.md              # Documentos técnicos
├── docker/                # Configuración Docker y compose
├── logs/                  # Logs del sistema (no versionados)
├── requirements.txt       # Dependencias Python
└── run_server.py         # Punto de entrada del servidor
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
│   ├── build/            # Scripts de construcción
│   ├── deploy/           # Scripts de despliegue
│   └── utils/            # Utilidades de análisis
├── docs/                  # Documentación del frontend
├── dist/                  # Build de producción (no versionado)
└── package.json          # Dependencias y scripts npm
```

### Raíz del Proyecto
```
PROYECTO/
├── Back-FC/              # Backend
├── Front-FC/             # Frontend
├── docs/                 # Documentación global
│   ├── API.md
│   ├── GETTING_STARTED.md
│   ├── SISTEMA_ROLES_PERMISOS.md
│   ├── SOLUCION_GMF_AUTOCALCULO.md
│   └── PROJECT_STRUCTURE.md (este archivo)
├── Excel/                # Archivos Excel para cargue (no versionados)
│   └── README.md
├── config/               # Configuración Docker y Makefile
├── scripts/              # Scripts globales del proyecto
│   └── setup/           # Scripts de setup multi-plataforma
├── tools/                # Herramientas globales
│   ├── debug/           # Debug del proyecto completo
│   ├── maintenance/     # Mantenimiento global
│   └── setup/           # Setup y verificación
├── .github/              # CI/CD y templates de GitHub
├── .gitignore           # Archivos ignorados (actualizado)
├── README.md            # Documentación principal
├── CHANGELOG.md         # Historial de cambios
├── CONTRIBUTING.md      # Guía de contribución
└── LICENSE              # Licencia del proyecto
```

---

## 🚫 Qué NO debe estar en el repositorio

### Archivos temporales
- Scripts de prueba con nombres como `test_temp.py`, `debug_quick.py`
- Archivos de respaldo con extensiones `.bak`, `.backup`
- Logs duplicados en múltiples ubicaciones
- Archivos HTML de debug (`debug_*.html`)

### Archivos de configuración local
- `.env` con credenciales reales (usar `.env.example`)
- Configuraciones específicas del IDE
- Archivos de cache temporal

### Archivos en lugares incorrectos
- ❌ `test_*.py` en raíz de Back-FC → Deben estar en `/tests/`
- ❌ `check_*.py` en raíz de Back-FC → Deben estar en `/tools/`
- ❌ `debug_*.py` en raíz de Back-FC → Deben estar en `/tools/`
- ❌ `*.md` en raíz de Back-FC → Deben estar en `/docs/`
- ❌ `*.log` en cualquier lugar → No versionados, solo en `/logs/`

---

## ✅ Mejores Prácticas

### Nomenclatura de Archivos
- **Tests**: `test_funcionalidad.py` → En `/tests/`
- **Verificación**: `check_funcionalidad.py` → En `/tools/`
- **Debug**: `debug_funcionalidad.py` → En `/tools/`
- **Mantenimiento**: `accion_descripcion.py` → En `/scripts/maintenance/`
- **Componentes**: `PascalCase.tsx`
- **Servicios**: `camelCaseService.ts`

### Organización de Código
1. **Backend**: Separar por funcionalidad (API, modelos, servicios)
2. **Frontend**: Componentes en carpetas por funcionalidad
3. **Tests**: Un archivo de test por módulo/servicio en `/tests/`
4. **Scripts**: Categorizar por propósito en subcarpetas apropiadas
5. **Tools**: Herramientas de verificación separadas del código de producción

### Documentación
- Cada carpeta principal debe tener un `README.md`
- Documentar scripts complejos con comentarios
- Mantener documentación actualizada con cambios importantes
- Documentos técnicos en `/docs/` apropiado (backend o global)

---

## 🧹 Limpieza Regular

### Cada Sprint
- Revisar archivos temporales en `/tools/debug/`
- Eliminar scripts obsoletos
- Actualizar documentación si hay cambios estructurales
- Verificar que no hay archivos en lugares incorrectos

### Cada Release
- Limpiar logs antiguos
- Revisar y organizar tests
- Validar que no hay archivos duplicados
- Actualizar CHANGELOG.md

---

## 🔧 Comandos Útiles

### Encontrar archivos duplicados
```powershell
# PowerShell
Get-ChildItem -Recurse | Group-Object Name | Where-Object {$_.Count -gt 1}
```

### Limpiar archivos temporales
```powershell
# Eliminar archivos .pyc
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Eliminar logs antiguos (más de 30 días)
Get-ChildItem -Path ".\logs" -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item -Force
```

### Verificar archivos fuera de lugar
```powershell
# Buscar test_*.py en raíz de Back-FC
Get-ChildItem -Path ".\Back-FC\test_*.py"

# Buscar check_*.py en raíz de Back-FC
Get-ChildItem -Path ".\Back-FC\check_*.py"
```

---

## 📝 Checklist de Organización

- [x] ¿Los scripts están en la carpeta correcta según su propósito?
- [x] ¿Los tests están en `/tests/`?
- [x] ¿Las herramientas de verificación están en `/tools/`?
- [x] ¿Los documentos markdown están en `/docs/`?
- [x] ¿No hay archivos duplicados innecesarios?
- [x] ¿La documentación está actualizada?
- [x] ¿Los logs no están versionados?
- [x] ¿No hay credenciales en archivos versionados?
- [x] ¿El .gitignore previene archivos fuera de lugar?

---

## 📊 Cambios Recientes (2 de diciembre de 2025)

### ✅ Archivos Movidos

**De `Back-FC/` raíz a `Back-FC/tools/`:**
- `check_areas.py`
- `check_conceptos.py`
- `check_festivos.py`
- `check_tesoreria.py`
- `check_trm_recent.py`
- `debug_cuentas_excel.py`

**De `Back-FC/` raíz a `Back-FC/tests/`:**
- `test_gmf_all.py`
- `test_gmf_debug.py`
- `test_recalculo_saldo_neto.py`
- `test_trm_manual.py`

**De `Back-FC/` raíz a `Back-FC/scripts/maintenance/`:**
- `limpiar_septiembre.py`

**De `Back-FC/` raíz a `Back-FC/docs/`:**
- `MIGRACION_COMPLETADA.md`
- `MIGRACION_POSTGRESQL.md`
- `TRM_SYSTEM_DOCUMENTATION.md`

**De raíz a `docs/`:**
- `SOLUCION_GMF_AUTOCAL CULO.md` → `SOLUCION_GMF_AUTOCALCULO.md` (renombrado)

### 🗑️ Archivos Eliminados

- `Back-FC/trm_scraper.log` - Log que no debería estar versionado
- `Front-FC/debug_sync.html` - Archivo de debug temporal

### 📝 Documentos Actualizados

- `.gitignore` - Reglas preventivas para evitar archivos fuera de lugar
- `README.md` - Estructura actualizada del proyecto
- `Back-FC/README.md` - Organización de carpetas backend
- `docs/PROJECT_STRUCTURE.md` - Este documento actualizado
- `Excel/README.md` - Documentación de carpeta Excel creada

---

## 🎯 Resultado Final

- ✅ **Proyecto limpio y organizado**
- ✅ **Estructura coherente y predecible**
- ✅ **Documentación actualizada**
- ✅ **Reglas de .gitignore preventivas**
- ✅ **Funcionalidad intacta** - Sin cambios en código de producción

---

**Mantenido por:** Equipo de Desarrollo Bolívar  
**Última revisión:** 2 de diciembre de 2025