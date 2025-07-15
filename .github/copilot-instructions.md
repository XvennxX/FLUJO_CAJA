# Copilot Instructions - Sistema de Flujo de Caja

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Contexto del Proyecto
Este es un sistema web de flujo de caja que digitaliza hojas de Excel existentes (CUADROFLUJOMAYO2025.xlsx, JUNIO2025.xlsx). El sistema mantiene la lógica contable original pero añade automatización, control de acceso y reportes avanzados.

## Tecnologías Principales
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Python 3.11+
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Base de Datos**: PostgreSQL con migraciones Alembic
- **Autenticación**: JWT tokens con roles diferenciados
- **Contenización**: Docker y Docker Compose

## Estructura de Datos Clave

### Modelos Principales:
1. **Usuario**: Con roles (Tesorería, Pagaduría, Mesa de Dinero)
2. **Categoría**: Clasificación de ingresos/egresos
3. **Transacción**: Movimientos diarios con fecha, monto, categoría
4. **MesFlujo**: Control mensual con saldos iniciales/finales

### Lógica de Negocio:
- Cálculo automático de saldos diarios: `saldo_anterior + flujo_neto`
- Flujo neto = ingresos - egresos del día
- Categorización automática por tipo (ingreso/egreso)
- Validaciones de permisos por rol de usuario

## Roles y Permisos:
- **Tesorería**: Acceso completo, puede ver/editar todo
- **Pagaduría**: Solo egresos (nómina, proveedores)
- **Mesa de Dinero**: Solo consulta y reportes

## Patrones de Código:
- Usar Repository Pattern para acceso a datos
- DTOs/Schemas con Pydantic para validaciones
- Dependency Injection para servicios
- Manejo centralizado de errores
- Logging estructurado
- Tests unitarios con pytest

## Convenciones:
- Nombres en español para entidades de negocio
- Código y comentarios en español
- APIs RESTful con nomenclatura clara
- Componentes React funcionales con hooks
- Estado global con Context API o Zustand

## Funcionalidades Clave:
1. Vista calendario/tabla tipo Excel por mes
2. Registro de transacciones con validaciones
3. Cálculos automáticos de saldos y totales
4. Importación de archivos Excel históricos
5. Exportación de reportes (PDF, Excel)
6. Dashboard con gráficos y métricas
7. Proyección de flujo futuro
8. Cierre automático mensual

Siempre considera la experiencia del usuario final que está acostumbrado a trabajar con Excel.
