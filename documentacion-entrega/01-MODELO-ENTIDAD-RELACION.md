# MODELO ENTIDAD-RELACIÓN - SISTEMA DE FLUJO DE CAJA

## INFORMACIÓN GENERAL

**Proyecto**: Sistema de Flujo de Caja - Bolívar  
**Base de Datos**: MySQL 8.0+  
**Charset**: utf8mb4_unicode_ci  
**Engine**: InnoDB  
**Fecha de Documentación**: 18 de Diciembre de 2025  

---

## 📊 DIAGRAMA ENTIDAD-RELACIÓN

### ENTIDADES PRINCIPALES

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     USUARIOS    │    │      ROLES      │    │    PERMISOS     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ nombre          │    │ nombre          │    │ nombre          │
│ email (UK)      │    │ codigo (UK)     │    │ codigo (UK)     │
│ contrasena      │    │ descripcion     │    │ descripcion     │
│ rol             │    │ activo          │    │ modulo          │
│ rol_id (FK)     │    │ es_sistema      │    │ activo          │
│ estado          │    │ fecha_creacion  │    │ fecha_creacion  │
└─────────────────┘    │ fecha_actual.   │    └─────────────────┘
         │              └─────────────────┘             │
         │                        │                     │
         └────────────────────────┼─────────────────────┘
                                  │
                          ┌─────────────────┐
                          │  ROL_PERMISO    │
                          │  (Tabla Inter.) │
                          ├─────────────────┤
                          │ rol_id (PK,FK)  │
                          │ permiso_id(PK,FK)│
                          └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    COMPANIAS    │    │     BANCOS      │    │CUENTAS_BANCARIAS│
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ nombre          │    │ nombre (UK)     │    │ numero_cuenta   │
└─────────────────┘    └─────────────────┘    │ compania_id(FK) │
         │                       │             │ banco_id (FK)   │
         └───────────────────────┼─────────────┤ tipo_cuenta     │
                                 │             └─────────────────┘
                                 └─────────────────────│
                                                       │
┌─────────────────┐    ┌─────────────────┐            │
│  CUENTA_MONEDA  │    │    GMF_CONFIG   │            │
├─────────────────┤    ├─────────────────┤            │
│ id (PK)         │    │ id (PK)         │            │
│ cuenta_id (FK)  │────│ cuenta_bancaria │────────────┘
│ tipo_moneda     │    │ _id (FK)        │
│ saldo_inicial   │    │ tasa_gmf        │
│ saldo_actual    │    │ activo          │
│ activo          │    │ fecha_vigencia  │
│ fecha_creacion  │    │ created_at      │
│ fecha_actual.   │    │ updated_at      │
└─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    CONCEPTOS_FLUJO_CAJA                             │
├─────────────────────────────────────────────────────────────────────┤
│ id (PK)                                                             │
│ nombre                                                              │
│ codigo                          ┌─────────────────┐                │
│ tipo                            │  TipoMovimiento │                │
│ area ──────────────────────────▶│  AreaConcepto   │                │
│ orden_display                   │ TipoDependencia │                │
│ activo                          └─────────────────┘                │
│ depende_de_concepto_id (FK) ────┐                                  │
│ tipo_dependencia                │ ◄─────────────────────────────────┘
│ formula_dependencia             │ (AUTO-REFERENCIA)
│ created_at                      │
│ updated_at                      │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────┐
│                TRANSACCIONES_FLUJO_CAJA                            │
├─────────────────────────────────┼───────────────────────────────────┤
│ id (PK)                         │                                   │
│ fecha                           │                                   │
│ concepto_id (FK) ───────────────┘                                   │
│ cuenta_id (FK) ──────────────────────────────────────────────────┐  │
│ monto                                                            │  │
│ descripcion                      ┌─────────────────┐             │  │
│ usuario_id (FK) ─────────────────▶│AreaTransaccion │             │  │
│ area                             └─────────────────┘             │  │
│ compania_id (FK) ────────────────────────────────────────────┐   │  │
│ auditoria (JSON)                                             │   │  │
│ created_at                                                   │   │  │
│ updated_at                                                   │   │  │
└──────────────────────────────────────────────────────────────┼───┼──┘
                                                               │   │
            ┌──────────────────────────────────────────────────┘   │
            │              ┌─────────────────────────────────────┘
            ▼              ▼
┌─────────────────┐    ┌─────────────────┐
│       TRM       │    │NOTIFICACIONES   │
├─────────────────┤    ├─────────────────┤
│ fecha (PK)      │    │ id (PK)         │
│ valor           │    │ titulo          │
│ fecha_creacion  │    │ mensaje         │
└─────────────────┘    │ tipo            │
                       │ usuario_id (FK) │
                       │ leida           │
                       │ created_at      │
                       └─────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                      AUDITORIA                                       │
├──────────────────────────────────────────────────────────────────────┤
│ id (PK)                                                              │
│ tabla_afectada                                                       │
│ registro_id                                                          │
│ accion                         ┌─────────────────┐                   │
│ datos_anteriores (JSON)        │   TipoAccion    │                   │
│ datos_nuevos (JSON)      ──────▶│   TipoTabla     │                   │
│ usuario_id (FK)                └─────────────────┘                   │
│ ip_address                                                           │
│ user_agent                                                           │
│ timestamp                                                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 RELACIONES DETALLADAS

### 1. SISTEMA DE USUARIOS Y PERMISOS (RBAC)

```sql
-- Relación: Usuario → Rol (Many-to-One)
usuarios.rol_id → roles.id

-- Relación: Rol ↔ Permiso (Many-to-Many)
roles.id ↔ rol_permiso.rol_id
permisos.id ↔ rol_permiso.permiso_id
```

**Cardinalidad:**
- Un **Usuario** puede tener un **Rol** (0:1)
- Un **Rol** puede tener múltiples **Usuarios** (1:N)
- Un **Rol** puede tener múltiples **Permisos** (M:N)
- Un **Permiso** puede estar en múltiples **Roles** (M:N)

### 2. ESTRUCTURA BANCARIA

```sql
-- Relación: Compania ↔ CuentaBancaria (One-to-Many)
companias.id ← cuentas_bancarias.compania_id

-- Relación: Banco ↔ CuentaBancaria (One-to-Many) 
bancos.id ← cuentas_bancarias.banco_id

-- Relación: CuentaBancaria ↔ CuentaMoneda (One-to-Many)
cuentas_bancarias.id ← cuenta_moneda.cuenta_id

-- Relación: CuentaBancaria ↔ GMFConfig (One-to-Many)
cuentas_bancarias.id ← gmf_config.cuenta_bancaria_id
```

**Cardinalidad:**
- Una **Compania** puede tener múltiples **CuentasBancarias** (1:N)
- Un **Banco** puede tener múltiples **CuentasBancarias** (1:N)
- Una **CuentaBancaria** puede tener múltiples **CuentaMoneda** (1:N)
- Una **CuentaBancaria** puede tener múltiples **GMFConfig** (1:N)

### 3. SISTEMA DE FLUJO DE CAJA (CORE)

```sql
-- Relación: ConceptoFlujoCaja → ConceptoFlujoCaja (Auto-referencia)
conceptos_flujo_caja.depende_de_concepto_id → conceptos_flujo_caja.id

-- Relación: ConceptoFlujoCaja ↔ TransaccionFlujoCaja (One-to-Many)
conceptos_flujo_caja.id ← transacciones_flujo_caja.concepto_id

-- Relación: CuentaBancaria ↔ TransaccionFlujoCaja (One-to-Many)
cuentas_bancarias.id ← transacciones_flujo_caja.cuenta_id

-- Relación: Usuario ↔ TransaccionFlujoCaja (One-to-Many)
usuarios.id ← transacciones_flujo_caja.usuario_id

-- Relación: Compania ↔ TransaccionFlujoCaja (One-to-Many)
companias.id ← transacciones_flujo_caja.compania_id
```

**Cardinalidad:**
- Un **ConceptoFlujoCaja** puede depender de otro **ConceptoFlujoCaja** (0:1)
- Un **ConceptoFlujoCaja** puede tener múltiples **TransaccionesFlujoCaja** (1:N)
- Una **CuentaBancaria** puede tener múltiples **TransaccionesFlujoCaja** (1:N)
- Un **Usuario** puede crear múltiples **TransaccionesFlujoCaja** (1:N)
- Una **Compania** puede tener múltiples **TransaccionesFlujoCaja** (1:N)

### 4. SISTEMAS AUXILIARES

```sql
-- TRM: Tabla independiente (sin relaciones)
-- Notificaciones: Relación con Usuario
usuarios.id ← notificaciones.usuario_id

-- Auditoria: Relación con Usuario
usuarios.id ← auditoria.usuario_id
```

---

## 📋 ENUMERACIONES Y TIPOS

### Enums de Conceptos de Flujo de Caja

```sql
-- TipoMovimiento
ENUM('pagaduria', 'renta_fija', 'renta_variable', 'derivados', 'divisas', 'otros')

-- AreaConcepto  
ENUM('tesoreria', 'pagaduria', 'ambas')

-- TipoDependencia
ENUM('copia', 'suma', 'resta')
```

### Enums de Transacciones

```sql
-- AreaTransaccion
ENUM('tesoreria', 'pagaduria')
```

### Enums de Cuentas Bancarias

```sql
-- TipoCuenta
ENUM('CORRIENTE', 'AHORROS')

-- TipoMoneda  
ENUM('COP', 'USD')
```

### Enums de Auditoría

```sql
-- TipoAccion
ENUM('CREATE', 'READ', 'UPDATE', 'DELETE')

-- TipoTabla
ENUM('usuarios', 'conceptos_flujo_caja', 'transacciones_flujo_caja', 'cuentas_bancarias', 'companias', 'bancos')
```

---

## 🔄 DEPENDENCIAS Y CÁLCULOS AUTOMÁTICOS

### Sistema de Dependencias de Conceptos

El sistema permite que un concepto dependa automáticamente de otro:

```sql
-- Ejemplo: "SALDO FINAL" depende de "SALDO INICIAL"
UPDATE conceptos_flujo_caja 
SET depende_de_concepto_id = 1,  -- ID del concepto "SALDO INICIAL"
    tipo_dependencia = 'copia',  -- Copia el mismo valor
    formula_dependencia = NULL
WHERE id = 15;  -- ID del concepto "SALDO FINAL"
```

**Tipos de Dependencia:**
- **copia**: Copia exacta del valor del concepto padre
- **suma**: Suma el valor del concepto padre + factor
- **resta**: Resta el valor del concepto padre - factor

### Fórmulas Complejas

```sql
-- Ejemplo: "TOTAL EGRESOS" suma múltiples conceptos
UPDATE conceptos_flujo_caja 
SET formula_dependencia = 'SUMA(5,6,7,8)'  -- IDs de conceptos a sumar
WHERE id = 20;
```

---

## 🔐 RESTRICCIONES DE INTEGRIDAD

### Constraints Principales

```sql
-- Unicidad de transacciones por fecha/concepto/cuenta
UNIQUE KEY unique_transaccion (fecha, concepto_id, cuenta_id)

-- Validación de dependencias
CONSTRAINT chk_dependencia_valida CHECK (
    (depende_de_concepto_id IS NULL AND tipo_dependencia IS NULL) OR
    (depende_de_concepto_id IS NOT NULL AND tipo_dependencia IS NOT NULL)
)

-- Emails únicos
UNIQUE KEY unique_email (email)

-- Códigos únicos en roles y permisos
UNIQUE KEY unique_codigo_rol (codigo)
UNIQUE KEY unique_codigo_permiso (codigo)
```

### Claves Foráneas con Acciones

```sql
-- Eliminación en cascada
FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE
FOREIGN KEY (cuenta_id) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE

-- Poner NULL al eliminar
FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL
```

---

## 📊 ÍNDICES DE RENDIMIENTO

### Índices por Tabla

```sql
-- usuarios
INDEX idx_email (email)
INDEX idx_rol_estado (rol, estado)
INDEX idx_rol_id (rol_id)

-- conceptos_flujo_caja
INDEX idx_area_activo (area, activo)
INDEX idx_orden_display (orden_display)
INDEX idx_dependencia (depende_de_concepto_id)

-- transacciones_flujo_caja
INDEX idx_fecha (fecha)
INDEX idx_concepto_fecha (concepto_id, fecha)
INDEX idx_cuenta_fecha (cuenta_id, fecha)
INDEX idx_usuario (usuario_id)
INDEX idx_fecha_concepto_cuenta (fecha, concepto_id, cuenta_id)

-- cuentas_bancarias
INDEX idx_compania (compania_id)
INDEX idx_banco (banco_id)
INDEX idx_numero (numero_cuenta)

-- auditoria
INDEX idx_tabla_registro (tabla_afectada, registro_id)
INDEX idx_usuario_fecha (usuario_id, timestamp)
INDEX idx_fecha (timestamp)
```

---

## 🎯 CASOS DE USO DEL MODELO

### 1. Flujo de Caja Diario
1. Usuario selecciona fecha
2. Sistema consulta `transacciones_flujo_caja` por fecha
3. Agrupa por `concepto_id` y `area`
4. Calcula totales automáticos usando dependencias

### 2. Dashboard Multi-Area
1. Sistema consulta conceptos por `area` (tesoreria/pagaduria)
2. Para cada concepto, busca transacciones de la fecha
3. Aplica cálculos automáticos según `tipo_dependencia`
4. Presenta vista consolidada

### 3. Sistema de Permisos
1. Usuario hace login
2. Sistema carga `rol_obj` con `permisos`
3. Cada acción valida permisos via `tiene_permiso(codigo)`
4. Control granular por módulo/acción

### 4. TRM Automática
1. Scheduler ejecuta a las 7 PM
2. Consulta fuentes oficiales
3. Inserta/actualiza tabla `trm`
4. Transacciones USD se convierten automáticamente

Este modelo soporta completamente todos los requerimientos del sistema de flujo de caja, con flexibilidad para crecimiento y mantenimiento.