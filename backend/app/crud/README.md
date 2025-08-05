# CRUD Operations

Operaciones de base de datos para cada entidad.

## Estructura

```
crud/
├── __init__.py
├── base.py                # CRUD base genérico
├── user.py                # CRUD para usuarios
├── company.py             # CRUD para empresas
├── transaction.py         # CRUD para transacciones
├── category.py            # CRUD para categorías
├── cash_flow.py           # CRUD para flujo de caja
└── report.py              # CRUD para reportes
```

## Patrón CRUD Base

Cada archivo implementa las operaciones estándar:

- **Create**: Crear nuevos registros
- **Read**: Obtener registros (uno o múltiples)
- **Update**: Actualizar registros existentes
- **Delete**: Eliminar registros

## Funcionalidades Adicionales

- Filtros y búsquedas
- Paginación
- Ordenamiento
- Validaciones de integridad
- Soft delete cuando sea necesario
