# API Endpoints - Estado de Implementación

## 🔐 Autenticación
- ✅ `POST /api/v1/auth/login` - Iniciar sesión
- ✅ `POST /api/v1/auth/logout` - Cerrar sesión

## 👥 Usuarios
- ✅ `GET /api/v1/usuarios` - Listar usuarios
- ✅ `POST /api/v1/usuarios` - Crear usuario
- ✅ `GET /api/v1/usuarios/{id}` - Obtener usuario
- ✅ `PUT /api/v1/usuarios/{id}` - Actualizar usuario
- ✅ `PATCH /api/v1/usuarios/{id}/estado` - Cambiar estado

## 🎭 Roles
- ✅ `GET /api/v1/roles` - Listar roles

## 💰 Ingresos
- 🚧 `GET /api/v1/ingresos` - Listar ingresos
- 🚧 `POST /api/v1/ingresos` - Crear ingreso
- 🚧 `GET /api/v1/ingresos/{id}` - Obtener ingreso
- 🚧 `PUT /api/v1/ingresos/{id}` - Actualizar ingreso
- 🚧 `DELETE /api/v1/ingresos/{id}` - Eliminar ingreso

## 💸 Egresos
- 🚧 `GET /api/v1/egresos` - Listar egresos
- 🚧 `POST /api/v1/egresos` - Crear egreso
- 🚧 `GET /api/v1/egresos/{id}` - Obtener egreso
- 🚧 `PUT /api/v1/egresos/{id}` - Actualizar egreso
- 🚧 `DELETE /api/v1/egresos/{id}` - Eliminar egreso

## 🧾 Conceptos
- 🚧 `GET /api/v1/conceptos` - Listar conceptos
- 🚧 `POST /api/v1/conceptos` - Crear concepto
- 🚧 `PUT /api/v1/conceptos/{id}` - Actualizar concepto
- 🚧 `DELETE /api/v1/conceptos/{id}` - Eliminar concepto

## 🗃️ Cuentas
- 🚧 `GET /api/v1/cuentas` - Listar cuentas
- 🚧 `POST /api/v1/cuentas` - Crear cuenta
- 🚧 `GET /api/v1/cuentas/{id}/movimientos` - Movimientos por cuenta
- 🚧 `PUT /api/v1/cuentas/{id}` - Actualizar cuenta
- 🚧 `PATCH /api/v1/cuentas/{id}/saldo` - Ajustar saldo

## 📊 Reportes
- 🚧 `GET /api/v1/reportes/diario` - Resumen diario
- 🚧 `GET /api/v1/reportes/mensual` - Resumen mensual
- 🚧 `GET /api/v1/reportes/comparativo-areas` - Comparativo por áreas
- 🚧 `GET /api/v1/reportes/flujo` - Flujo de caja
- 🚧 `GET /api/v1/reportes/exportar` - Exportar reportes

## 🔍 Auditoría
- 🚧 `GET /api/v1/auditoria` - Listar auditoría
- 🚧 `GET /api/v1/auditoria/usuario/{id}` - Auditoría por usuario

## Leyenda
- ✅ Implementado y funcional
- 🚧 En desarrollo
- ❌ Pendiente
