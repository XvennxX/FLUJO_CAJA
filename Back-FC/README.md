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
│   └── integration/      # Tests de integración
├── scripts/              # 🛠️ Scripts organizados
│   ├── dev/              # Desarrollo y debug
│   ├── setup/            # Configuración inicial
│   ├── maintenance/      # Mantenimiento
│   └── migration/        # Migraciones
├── tools/                # 🔧 Herramientas de verificación
├── docs/                 # 📚 Documentación
├── logs/                 # 📋 Archivos de log
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
- **Testing:** Scripts disponibles en `/scripts/tests/`
- **Debug:** Herramientas en `/scripts/debug/`
- **Mantenimiento:** Scripts en `/scripts/maintenance/`
- **Consulta histórica:** Código archivado en `/scripts/archive/`