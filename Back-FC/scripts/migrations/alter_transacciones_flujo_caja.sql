-- =========================================================
-- COMPLETAR TABLA: transacciones_flujo_caja
-- Agregar campos faltantes para funcionalidad completa
-- =========================================================

-- 1. CAMBIAR TIPO DE FECHA A DATE si no está así
ALTER TABLE transacciones_flujo_caja 
MODIFY COLUMN fecha DATE NOT NULL 
COMMENT 'Fecha específica del flujo de caja';

-- 2. CAMBIAR TIPO DE MONTO A DECIMAL(18,2)
ALTER TABLE transacciones_flujo_caja 
MODIFY COLUMN monto DECIMAL(18,2) NOT NULL DEFAULT 0.00 
COMMENT 'Valor de la transacción';

-- 3. AGREGAR CAMPOS DE AUDITORÍA FALTANTES
ALTER TABLE transacciones_flujo_caja 
ADD COLUMN es_automatica BOOLEAN DEFAULT FALSE 
COMMENT 'Si fue generada automáticamente' AFTER usuario_id;

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN transaccion_origen_id INT NULL 
COMMENT 'Transacción que generó esta (dependencias)' AFTER es_automatica;

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
AFTER transaccion_origen_id;

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
AFTER fecha_creacion;

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN ip_address VARCHAR(45) NULL 
COMMENT 'IP desde donde se modificó' AFTER fecha_modificacion;

-- 4. AGREGAR FOREIGN KEYS FALTANTES
ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT fk_transaccion_concepto 
FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE;

ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT fk_transaccion_cuenta 
FOREIGN KEY (cuenta_id) REFERENCES bank_accounts(id) ON DELETE CASCADE;

ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT fk_transaccion_usuario 
FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT fk_transaccion_origen 
FOREIGN KEY (transaccion_origen_id) REFERENCES transacciones_flujo_caja(id) ON DELETE SET NULL;

-- 5. AGREGAR CONSTRAINT ÚNICO PRINCIPAL
ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT unique_transaccion UNIQUE (fecha, concepto_id, cuenta_id);

-- 6. AGREGAR ÍNDICES PARA PERFORMANCE
ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_fecha (fecha);

ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_concepto_fecha (concepto_id, fecha);

ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_cuenta_fecha (cuenta_id, fecha);

ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_usuario (usuario_id);

ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_automatica (es_automatica);

ALTER TABLE transacciones_flujo_caja 
ADD INDEX idx_fecha_concepto_cuenta (fecha, concepto_id, cuenta_id);

-- 7. VERIFICAR ESTRUCTURA ACTUALIZADA
DESCRIBE transacciones_flujo_caja;
