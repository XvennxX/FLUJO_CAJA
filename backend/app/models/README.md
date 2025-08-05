# Modelos de Datos

Modelos SQLAlchemy para el sistema de flujo de caja.

## Modelos Principales

```
models/
├── __init__.py
├── base.py              # Modelo base
├── user.py              # Usuario del sistema
├── company.py           # Empresa
├── transaction.py       # Transacciones financieras
├── category.py          # Categorías
├── cash_flow.py         # Flujo de caja
├── projection.py        # Proyecciones
└── report.py           # Reportes
```

## Relaciones

- Un **Usuario** puede pertenecer a múltiples **Empresas**
- Una **Empresa** tiene múltiples **Transacciones**
- Las **Transacciones** se clasifican por **Categorías**
- El **Flujo de Caja** se calcula basado en las **Transacciones**
- Las **Proyecciones** se basan en datos históricos
