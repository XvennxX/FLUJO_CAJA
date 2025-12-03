# Backend - Flujo de Caja �

Backend API desarrollado con **FastAPI** para el sistema de Flujo de Caja.

## 🏗️ Estructura del Proyecto

```
Back-FC/
├── app/                    # 🚀 Aplicación principal
│   ├── api/               # REST endpoints
│   ├── core/              # Configuración y database
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   └── services/          # Lógica de negocio
├── tests/                 # 🧪 Tests organizados
│   ├── unit/             # Tests unitarios
│   ├── integration/      # Tests de integración
│   ├── test_gmf_*.py     # Tests de GMF
│   ├── test_trm_*.py     # Tests de TRM
│   └── test_*.py         # Tests diversos
├── scripts/              # 🛠️ Scripts organizados
│   ├── setup/            # Configuración inicial
│   ├── maintenance/      # Mantenimiento y correcciones
│   ├── trm/              # Sistema TRM
│   ├── utils/            # Utilidades generales
│   ├── migration/        # Migraciones de DB
│   ├── debug/            # Scripts de debugging
│   └── tests/            # Scripts de prueba
├── tools/                # 🔧 Herramientas de verificación
│   ├── check_*.py        # Scripts de verificación
│   ├── debug_*.py        # Scripts de debug
│   └── README.md         # Documentación de herramientas
├── docs/                 # 📚 Documentación
│   ├── TRM_SYSTEM_DOCUMENTATION.md
│   ├── MIGRACION_POSTGRESQL.md
│   └── *.md              # Documentos técnicos
├── logs/                 # 📋 Archivos de log (no versionados)
└── docker/               # 🐳 Configuración Docker
```

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Iniciar servidor
python run_server.py
```

## � Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unitarios
pytest tests/unit/

# Con coverage
pytest --cov=app tests/
```

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
- **Testing:** Tests en `/tests/` - Ejecutar con `pytest`
- **Scripts:**
  - `/scripts/setup/` - Configuración inicial del sistema
  - `/scripts/maintenance/` - Tareas de mantenimiento
  - `/scripts/trm/` - Sistema TRM automático
  - `/scripts/utils/` - Utilidades diversas
- **Tools:** Scripts de verificación en `/tools/`
- **Consulta histórica:** Código archivado en `/scripts/archive/`

## 🗂️ Organización de Archivos

### ✅ **Lo que DEBE estar en cada carpeta:**

- **`/app/`**: Solo código de producción de la aplicación
- **`/tests/`**: Todos los archivos `test_*.py`
- **`/scripts/`**: Scripts organizados por categoría
- **`/tools/`**: Scripts de verificación (`check_*.py`, `debug_*.py`)
- **`/docs/`**: Toda la documentación markdown
- **`/logs/`**: Archivos de log (no versionados)

### ❌ **Lo que NO debe estar en la raíz:**

- Archivos `test_*.py` → Mover a `/tests/`
- Archivos `check_*.py` → Mover a `/tools/`
- Archivos `debug_*.py` → Mover a `/tools/`
- Archivos `.md` (excepto README.md) → Mover a `/docs/`
- Archivos `.log` → Eliminados (no versionados)