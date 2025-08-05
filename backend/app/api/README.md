# API Endpoints

## Estructura de Endpoints

```
api/
└── v1/
    ├── endpoints/
    │   ├── auth.py          # Autenticación y autorización
    │   ├── users.py         # Gestión de usuarios
    │   ├── cash_flow.py     # Flujo de caja
    │   ├── transactions.py  # Transacciones
    │   ├── categories.py    # Categorías de ingresos/egresos
    │   ├── reports.py       # Reportes y estadísticas
    │   └── projections.py   # Proyecciones financieras
    ├── __init__.py
    └── api.py              # Router principal de la API
```

## Versioning

La API utiliza versionado por URL para mantener compatibilidad:
- `/api/v1/` - Versión actual
- Futuras versiones: `/api/v2/`, etc.
