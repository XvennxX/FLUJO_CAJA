# Servicios de Negocio

Lógica de negocio del sistema de flujo de caja.

## Estructura

```
services/
├── __init__.py
├── auth_service.py         # Autenticación y autorización
├── user_service.py         # Gestión de usuarios
├── company_service.py      # Gestión de empresas
├── transaction_service.py  # Procesamiento de transacciones
├── cash_flow_service.py    # Cálculos de flujo de caja
├── report_service.py       # Generación de reportes
├── projection_service.py   # Proyecciones financieras
└── notification_service.py # Notificaciones y alertas
```

## Responsabilidades

### Auth Service
- Login/logout de usuarios
- Validación de tokens JWT
- Gestión de permisos

### Cash Flow Service
- Cálculo de flujo de caja por períodos
- Análisis de tendencias
- Detección de patrones

### Report Service
- Generación de reportes financieros
- Exportación a PDF/Excel
- Visualización de datos

### Projection Service
- Proyecciones basadas en datos históricos
- Modelos predictivos
- Escenarios financieros
