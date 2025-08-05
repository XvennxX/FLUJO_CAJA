# Schemas de Pydantic

Esquemas de validación y serialización de datos.

## Estructura

```
schemas/
├── __init__.py
├── user.py                # Esquemas de usuario
├── company.py             # Esquemas de empresa
├── transaction.py         # Esquemas de transacciones
├── category.py            # Esquemas de categorías
├── cash_flow.py           # Esquemas de flujo de caja
├── report.py              # Esquemas de reportes
├── projection.py          # Esquemas de proyecciones
└── common.py              # Esquemas comunes (paginación, etc.)
```

## Tipos de Schemas

### Request Schemas
- Validación de datos de entrada
- Transformación de tipos
- Validaciones personalizadas

### Response Schemas
- Formato de datos de salida
- Exclusión de campos sensibles
- Serialización consistente

### Internal Schemas
- Transferencia entre capas
- Validaciones internas
- Transformaciones de datos
