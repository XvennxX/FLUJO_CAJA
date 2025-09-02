-- =========================================================
-- MIGRACIÓN: CREAR TABLAS FLUJO DE CAJA DIARIO
-- Fecha: 26 de agosto de 2025
-- Descripción: Implementación completa del sistema de flujo de caja
-- =========================================================

-- 1. TABLA: conceptos_flujo_caja
-- Catálogo dinámico de conceptos para tesorería y pagaduría
CREATE TABLE conceptos_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del concepto (ej: SALDO INICIAL)',
    codigo VARCHAR(10) COMMENT 'Código para dashboard (I, E, vacio)',
    tipo ENUM('ingreso','egreso','neutral') NOT NULL COMMENT 'Tipo para cálculos de totales',
    area ENUM('tesoreria','pagaduria','ambas') NOT NULL COMMENT 'Área donde aparece el concepto',
    orden_display INT DEFAULT 0 COMMENT 'Orden en el dashboard',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si está activo para usar',
    
    -- DEPENDENCIAS AUTOMÁTICAS
    depende_de_concepto_id INT NULL COMMENT 'Concepto del cual depende automáticamente',
    tipo_dependencia ENUM('copia','suma','resta') NULL COMMENT 'Tipo de cálculo automático',
    factor DECIMAL(10,4) DEFAULT 1.0000 COMMENT 'Factor multiplicador para el cálculo',
    
    -- AUDITORÍA
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    usuario_creacion INT COMMENT 'Usuario que creó el concepto',
    
    -- FOREIGN KEYS
    FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_creacion) REFERENCES users(id) ON DELETE SET NULL,
    
    -- ÍNDICES
    INDEX idx_area_activo (area, activo),
    INDEX idx_orden_display (orden_display),
    INDEX idx_dependencia (depende_de_concepto_id),
    
    -- CONSTRAINTS
    CONSTRAINT chk_dependencia_valida CHECK (
        (depende_de_concepto_id IS NULL AND tipo_dependencia IS NULL) OR
        (depende_de_concepto_id IS NOT NULL AND tipo_dependencia IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Catálogo de conceptos para flujo de caja diario';

-- 2. TABLA: transacciones_flujo_caja
-- Transacciones diarias por concepto y cuenta bancaria
CREATE TABLE transacciones_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL COMMENT 'Fecha específica del flujo de caja',
    concepto_id INT NOT NULL COMMENT 'Concepto al que pertenece',
    cuenta_id INT NULL COMMENT 'Cuenta bancaria (NULL para totales generales)',
    monto DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT 'Valor de la transacción',
    descripcion TEXT COMMENT 'Observaciones adicionales',
    
    -- AUDITORÍA
    usuario_id INT NULL COMMENT 'Usuario que creó/modificó (NULL si automático)',
    es_automatica BOOLEAN DEFAULT FALSE COMMENT 'Si fue generada automáticamente',
    transaccion_origen_id INT NULL COMMENT 'Transacción que generó esta (dependencias)',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) COMMENT 'IP desde donde se modificó',
    
    -- FOREIGN KEYS
    FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE,
    FOREIGN KEY (cuenta_id) REFERENCES bank_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (transaccion_origen_id) REFERENCES transacciones_flujo_caja(id) ON DELETE SET NULL,
    
    -- CONSTRAINTS
    UNIQUE KEY unique_transaccion (fecha, concepto_id, cuenta_id),
    
    -- ÍNDICES
    INDEX idx_fecha (fecha),
    INDEX idx_concepto_fecha (concepto_id, fecha),
    INDEX idx_cuenta_fecha (cuenta_id, fecha),
    INDEX idx_usuario (usuario_id),
    INDEX idx_automatica (es_automatica),
    INDEX idx_fecha_concepto_cuenta (fecha, concepto_id, cuenta_id)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Transacciones diarias del flujo de caja';

-- 3. VERIFICAR TABLAS CREADAS
SELECT 
    TABLE_NAME as 'Tabla Creada',
    TABLE_COMMENT as 'Descripción'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME IN ('conceptos_flujo_caja', 'transacciones_flujo_caja');

-- 4. MOSTRAR ESTRUCTURA
DESCRIBE conceptos_flujo_caja;
DESCRIBE transacciones_flujo_caja;
