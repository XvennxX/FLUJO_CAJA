# DEFINICIONES FÍSICAS DE TABLAS - SISTEMA DE FLUJO DE CAJA

## INFORMACIÓN GENERAL

**Proyecto**: Sistema de Flujo de Caja - Bolívar  
**Motor de Base de Datos**: MySQL 8.0+  
**Charset**: utf8mb4  
**Collation**: utf8mb4_unicode_ci  
**Storage Engine**: InnoDB  
**Fecha de Documentación**: 18 de Diciembre de 2025  

---

## 📋 TABLA: `usuarios`

### Definición DDL

```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del usuario',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del usuario',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Email único para login',
    contrasena VARCHAR(255) NOT NULL COMMENT 'Password hasheado con bcrypt',
    rol VARCHAR(50) NOT NULL COMMENT 'Rol legacy (mantener compatibilidad)',
    rol_id INT NULL COMMENT 'ID del rol en sistema RBAC',
    estado BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Activo=TRUE, Inactivo=FALSE',
    
    -- Constraints
    INDEX idx_email (email),
    INDEX idx_rol_estado (rol, estado),
    INDEX idx_rol_id (rol_id),
    
    -- Foreign Keys
    CONSTRAINT fk_usuarios_rol 
        FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Usuarios del sistema con autenticación y roles';
```

### Campos Detallados

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK, AI | NULL | Identificador único autoincremental |
| `nombre` | VARCHAR(100) | NO | - | NULL | Nombre completo del usuario |
| `email` | VARCHAR(100) | NO | UK | NULL | Email único para autenticación |
| `contrasena` | VARCHAR(255) | NO | - | NULL | Password encriptado con bcrypt |
| `rol` | VARCHAR(50) | NO | - | NULL | Rol legacy: admin, tesoreria, pagaduria, mesa_dinero |
| `rol_id` | INT | SÍ | FK | NULL | Referencia al nuevo sistema RBAC |
| `estado` | BOOLEAN | NO | - | TRUE | Estado activo/inactivo del usuario |

### Índices

```sql
-- Índice principal
PRIMARY KEY (id)

-- Índices funcionales
UNIQUE KEY unique_email (email)
INDEX idx_rol_estado (rol, estado)
INDEX idx_rol_id (rol_id)
```

---

## 📋 TABLA: `roles`

### Definición DDL

```sql
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nombre descriptivo del rol',
    codigo VARCHAR(50) NOT NULL UNIQUE COMMENT 'Código identificador único',
    descripcion TEXT NULL COMMENT 'Descripción detallada del rol',
    activo BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Si el rol está activo',
    es_sistema BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'No se puede eliminar',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_codigo (codigo),
    INDEX idx_activo (activo)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Roles del sistema RBAC';
```

### Campos Detallados

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK, AI | NULL | ID único del rol |
| `nombre` | VARCHAR(100) | NO | UK | NULL | Nombre del rol (ej: "Administrador") |
| `codigo` | VARCHAR(50) | NO | UK | NULL | Código único (ej: "ADMIN") |
| `descripcion` | TEXT | SÍ | - | NULL | Descripción detallada |
| `activo` | BOOLEAN | NO | - | TRUE | Estado del rol |
| `es_sistema` | BOOLEAN | NO | - | FALSE | Rol del sistema (no eliminable) |
| `fecha_creacion` | TIMESTAMP | NO | - | CURRENT_TIMESTAMP | Fecha creación |
| `fecha_modificacion` | TIMESTAMP | NO | - | CURRENT_TIMESTAMP | Última modificación |

---

## 📋 TABLA: `permisos`

### Definición DDL

```sql
CREATE TABLE permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre descriptivo del permiso',
    codigo VARCHAR(100) NOT NULL UNIQUE COMMENT 'Código único del permiso',
    descripcion TEXT NULL COMMENT 'Descripción del permiso',
    modulo VARCHAR(50) NOT NULL COMMENT 'Módulo al que pertenece',
    activo BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Si está activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_codigo (codigo),
    INDEX idx_modulo (modulo),
    INDEX idx_activo (activo)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Permisos granulares del sistema';
```

---

## 📋 TABLA: `rol_permiso` (Many-to-Many)

### Definición DDL

```sql
CREATE TABLE rol_permiso (
    rol_id INT NOT NULL COMMENT 'ID del rol',
    permiso_id INT NOT NULL COMMENT 'ID del permiso',
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Clave primaria compuesta
    PRIMARY KEY (rol_id, permiso_id),
    
    -- Foreign Keys
    CONSTRAINT fk_rol_permiso_rol 
        FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rol_permiso_permiso 
        FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE,
    
    -- Índices
    INDEX idx_rol_id (rol_id),
    INDEX idx_permiso_id (permiso_id)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabla intermedia Roles-Permisos (Many-to-Many)';
```

---

## 📋 TABLA: `conceptos_flujo_caja`

### Definición DDL

```sql
CREATE TABLE conceptos_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID único del concepto',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del concepto (ej: SALDO INICIAL)',
    codigo VARCHAR(10) NULL COMMENT 'Código para dashboard (I, E, vacío)',
    tipo VARCHAR(50) NULL COMMENT 'Tipo de movimiento personalizable',
    area ENUM('tesoreria','pagaduria','ambas') NOT NULL DEFAULT 'ambas' 
        COMMENT 'Área donde aparece el concepto',
    orden_display INT DEFAULT 0 COMMENT 'Orden en el dashboard',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si está activo para usar',
    
    -- Sistema de dependencias automáticas
    depende_de_concepto_id INT NULL COMMENT 'Concepto del cual depende automáticamente',
    tipo_dependencia ENUM('copia','suma','resta') NULL COMMENT 'Tipo de cálculo automático',
    formula_dependencia VARCHAR(255) NULL COMMENT 'Fórmula compleja (ej: SUMA(1,2,3))',
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints y Foreign Keys
    CONSTRAINT fk_concepto_dependencia 
        FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_dependencia_valida CHECK (
        (depende_de_concepto_id IS NULL AND tipo_dependencia IS NULL) OR
        (depende_de_concepto_id IS NOT NULL AND tipo_dependencia IS NOT NULL)
    ),
    
    -- Índices
    INDEX idx_area_activo (area, activo),
    INDEX idx_orden_display (orden_display),
    INDEX idx_dependencia (depende_de_concepto_id)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Catálogo de conceptos para flujo de caja diario';
```

### Campos Detallados

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK, AI | NULL | ID único del concepto |
| `nombre` | VARCHAR(100) | NO | - | NULL | Nombre descriptivo |
| `codigo` | VARCHAR(10) | SÍ | - | NULL | Código dashboard (I/E/vacío) |
| `tipo` | VARCHAR(50) | SÍ | - | NULL | Tipo personalizable |
| `area` | ENUM | NO | - | 'ambas' | tesoreria, pagaduria, ambas |
| `orden_display` | INT | NO | - | 0 | Orden en dashboard |
| `activo` | BOOLEAN | NO | - | TRUE | Estado del concepto |
| `depende_de_concepto_id` | INT | SÍ | FK | NULL | Auto-referencia para dependencias |
| `tipo_dependencia` | ENUM | SÍ | - | NULL | copia, suma, resta |
| `formula_dependencia` | VARCHAR(255) | SÍ | - | NULL | Fórmulas complejas |

---

## 📋 TABLA: `transacciones_flujo_caja`

### Definición DDL

```sql
CREATE TABLE transacciones_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID único de la transacción',
    fecha DATE NOT NULL COMMENT 'Fecha específica del flujo de caja',
    concepto_id INT NOT NULL COMMENT 'Concepto al que pertenece',
    cuenta_id INT NULL COMMENT 'Cuenta bancaria (NULL para totales generales)',
    monto DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT 'Valor de la transacción',
    descripcion TEXT NULL COMMENT 'Observaciones adicionales',
    usuario_id INT NULL COMMENT 'Usuario que creó/modificó',
    area ENUM('tesoreria','pagaduria') NOT NULL DEFAULT 'tesoreria' 
        COMMENT 'Área de la transacción',
    compania_id INT NULL COMMENT 'Compañía asociada',
    auditoria JSON NULL COMMENT 'Información de auditoría',
    
    -- Campos de auditoría automática
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_transaccion_concepto 
        FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE,
    CONSTRAINT fk_transaccion_cuenta 
        FOREIGN KEY (cuenta_id) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE,
    CONSTRAINT fk_transaccion_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    CONSTRAINT fk_transaccion_compania 
        FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE SET NULL,
    
    -- Constraint de unicidad
    UNIQUE KEY unique_transaccion (fecha, concepto_id, cuenta_id),
    
    -- Índices de rendimiento
    INDEX idx_fecha (fecha),
    INDEX idx_concepto_fecha (concepto_id, fecha),
    INDEX idx_cuenta_fecha (cuenta_id, fecha),
    INDEX idx_usuario (usuario_id),
    INDEX idx_fecha_concepto_cuenta (fecha, concepto_id, cuenta_id)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Transacciones diarias del flujo de caja';
```

### Campos Detallados

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK, AI | NULL | ID único de transacción |
| `fecha` | DATE | NO | IDX | NULL | Fecha del flujo de caja |
| `concepto_id` | INT | NO | FK | NULL | Referencia al concepto |
| `cuenta_id` | INT | SÍ | FK | NULL | Cuenta bancaria (opcional) |
| `monto` | DECIMAL(18,2) | NO | - | 0.00 | Valor con 2 decimales |
| `descripcion` | TEXT | SÍ | - | NULL | Observaciones |
| `usuario_id` | INT | SÍ | FK | NULL | Usuario que registró |
| `area` | ENUM | NO | - | 'tesoreria' | tesoreria, pagaduria |
| `compania_id` | INT | SÍ | FK | NULL | Compañía asociada |
| `auditoria` | JSON | SÍ | - | NULL | Metadatos de auditoría |

---

## 📋 TABLA: `cuentas_bancarias`

### Definición DDL

```sql
CREATE TABLE cuentas_bancarias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_cuenta VARCHAR(50) NOT NULL COMMENT 'Número de cuenta bancaria',
    compania_id INT NOT NULL COMMENT 'Compañía propietaria',
    banco_id INT NOT NULL COMMENT 'Banco de la cuenta',
    tipo_cuenta ENUM('CORRIENTE','AHORROS') NOT NULL DEFAULT 'CORRIENTE',
    
    -- Foreign Keys
    CONSTRAINT fk_cuenta_compania 
        FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE CASCADE,
    CONSTRAINT fk_cuenta_banco 
        FOREIGN KEY (banco_id) REFERENCES bancos(id) ON DELETE CASCADE,
    
    -- Índices
    INDEX idx_compania (compania_id),
    INDEX idx_banco (banco_id),
    INDEX idx_numero (numero_cuenta)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cuentas bancarias del sistema';
```

---

## 📋 TABLA: `cuenta_moneda`

### Definición DDL

```sql
CREATE TABLE cuenta_moneda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta_id INT NOT NULL COMMENT 'ID de la cuenta bancaria',
    tipo_moneda ENUM('COP','USD') NOT NULL COMMENT 'Tipo de moneda',
    saldo_inicial DECIMAL(18,2) DEFAULT 0.00 COMMENT 'Saldo inicial',
    saldo_actual DECIMAL(18,2) DEFAULT 0.00 COMMENT 'Saldo actual calculado',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si está activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_cuenta_moneda_cuenta 
        FOREIGN KEY (cuenta_id) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE,
    
    -- Constraint de unicidad
    UNIQUE KEY unique_cuenta_moneda (cuenta_id, tipo_moneda),
    
    -- Índices
    INDEX idx_cuenta_activo (cuenta_id, activo),
    INDEX idx_tipo_moneda (tipo_moneda)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Configuración multi-moneda de cuentas bancarias';
```

---

## 📋 TABLA: `trm`

### Definición DDL

```sql
CREATE TABLE trm (
    fecha DATE PRIMARY KEY COMMENT 'Fecha de la TRM (clave primaria)',
    valor DECIMAL(18,6) NOT NULL COMMENT 'Valor de la TRM con 6 decimales',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp de creación',
    
    -- Índice por fecha (implícito por PK)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tasas Representativas del Mercado (TRM) diarias';
```

---

## 📋 TABLA: `companias`

### Definición DDL

```sql
CREATE TABLE companias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre de la compañía',
    
    -- Índice por nombre
    INDEX idx_nombre (nombre)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Compañías del grupo empresarial';
```

---

## 📋 TABLA: `bancos`

### Definición DDL

```sql
CREATE TABLE bancos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nombre único del banco',
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de bancos';
```

---

## 📋 TABLA: `gmf_config`

### Definición DDL

```sql
CREATE TABLE gmf_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta_bancaria_id INT NOT NULL COMMENT 'Cuenta bancaria asociada',
    tasa_gmf DECIMAL(8,6) NOT NULL COMMENT 'Tasa GMF (ej: 0.004000)',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si está activo',
    fecha_vigencia DATE NOT NULL COMMENT 'Fecha desde cuando aplica',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_gmf_cuenta 
        FOREIGN KEY (cuenta_bancaria_id) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE,
    
    -- Índices
    INDEX idx_cuenta_activo (cuenta_bancaria_id, activo),
    INDEX idx_fecha_vigencia (fecha_vigencia)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Configuración GMF por cuenta bancaria';
```

---

## 📋 TABLA: `auditoria`

### Definición DDL

```sql
CREATE TABLE auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL COMMENT 'Tabla que se modificó',
    registro_id INT NOT NULL COMMENT 'ID del registro afectado',
    accion ENUM('CREATE','READ','UPDATE','DELETE') NOT NULL COMMENT 'Acción realizada',
    datos_anteriores JSON NULL COMMENT 'Estado anterior (UPDATE/DELETE)',
    datos_nuevos JSON NULL COMMENT 'Estado nuevo (CREATE/UPDATE)',
    usuario_id INT NULL COMMENT 'Usuario que ejecutó la acción',
    ip_address VARCHAR(45) NULL COMMENT 'Dirección IP',
    user_agent TEXT NULL COMMENT 'Navegador/Cliente',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Momento de la acción',
    
    -- Foreign Key
    CONSTRAINT fk_auditoria_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    -- Índices para consultas rápidas
    INDEX idx_tabla_registro (tabla_afectada, registro_id),
    INDEX idx_usuario_fecha (usuario_id, timestamp),
    INDEX idx_fecha (timestamp),
    INDEX idx_accion (accion)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registro completo de auditoría del sistema';
```

---

## 📋 TABLA: `notificaciones`

### Definición DDL

```sql
CREATE TABLE notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL COMMENT 'Título de la notificación',
    mensaje TEXT NOT NULL COMMENT 'Contenido del mensaje',
    tipo ENUM('info','warning','error','success') NOT NULL DEFAULT 'info',
    usuario_id INT NOT NULL COMMENT 'Usuario destinatario',
    leida BOOLEAN DEFAULT FALSE COMMENT 'Si fue leída',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_leida TIMESTAMP NULL COMMENT 'Cuándo se marcó como leída',
    
    -- Foreign Key
    CONSTRAINT fk_notificacion_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Índices
    INDEX idx_usuario_leida (usuario_id, leida),
    INDEX idx_fecha_creacion (created_at),
    INDEX idx_tipo (tipo)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Sistema de notificaciones de usuarios';
```

---

## 🔧 CONFIGURACIONES GLOBALES DE BASE DE DATOS

### Configuración de Motor

```sql
-- Configuración InnoDB
SET innodb_buffer_pool_size = 1G;
SET innodb_log_file_size = 256M;
SET innodb_flush_log_at_trx_commit = 1;

-- Configuración de Character Set
SET character_set_server = utf8mb4;
SET collation_server = utf8mb4_unicode_ci;

-- Configuración de SQL Mode
SET sql_mode = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
```

### Variables de Sistema Importantes

```sql
-- Verificar configuración
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'character_set_server';
SHOW VARIABLES LIKE 'collation_server';
SHOW VARIABLES LIKE 'sql_mode';
```

---

## 📊 TAMAÑOS ESTIMADOS Y PERFORMANCE

### Estimación de Tamaños

| Tabla | Registros Estimados | Tamaño Aprox | Crecimiento |
|-------|-------------------|--------------|-------------|
| `usuarios` | < 100 | 10 KB | Bajo |
| `roles` | < 20 | 5 KB | Muy Bajo |
| `permisos` | < 100 | 15 KB | Bajo |
| `conceptos_flujo_caja` | < 200 | 50 KB | Bajo |
| `transacciones_flujo_caja` | > 50,000/año | 10-50 MB/año | Alto |
| `cuentas_bancarias` | < 500 | 25 KB | Bajo |
| `trm` | 365/año | 50 KB/año | Medio |
| `auditoria` | > 100,000/año | 20-100 MB/año | Muy Alto |

### Recomendaciones de Mantenimiento

```sql
-- Optimización de tablas (ejecutar mensualmente)
OPTIMIZE TABLE transacciones_flujo_caja;
OPTIMIZE TABLE auditoria;

-- Análisis de índices (ejecutar semanalmente)
ANALYZE TABLE transacciones_flujo_caja;

-- Purga de auditoría antigua (ejecutar anualmente)
DELETE FROM auditoria WHERE timestamp < DATE_SUB(NOW(), INTERVAL 2 YEAR);
```

Esta documentación proporciona la definición física completa de todas las tablas del sistema, incluyendo tipos de datos específicos, constraints, índices y recomendaciones de rendimiento.