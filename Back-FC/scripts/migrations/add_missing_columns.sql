-- =========================================================
-- MIGRACIÓN: AGREGAR CAMPOS FALTANTES A TABLAS EXISTENTES
-- Fecha: 26 de agosto de 2025
-- Descripción: Completar estructura de tablas flujo de caja
-- =========================================================

-- 1. AGREGAR CAMPOS FALTANTES A conceptos_flujo_caja
ALTER TABLE conceptos_flujo_caja 
ADD COLUMN area ENUM('tesoreria','pagaduria','ambas') NOT NULL DEFAULT 'ambas' COMMENT 'Área donde aparece el concepto';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN orden_display INT DEFAULT 0 COMMENT 'Orden en el dashboard';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN activo BOOLEAN DEFAULT TRUE COMMENT 'Si está activo para usar';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN depende_de_concepto_id INT NULL COMMENT 'Concepto del cual depende automáticamente';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN tipo_dependencia ENUM('copia','suma','resta') NULL COMMENT 'Tipo de cálculo automático';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación';

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de actualización';

-- 2. AGREGAR CAMPOS FALTANTES A transacciones_flujo_caja
ALTER TABLE transacciones_flujo_caja 
ADD COLUMN area ENUM('tesoreria','pagaduria') NOT NULL DEFAULT 'tesoreria' COMMENT 'Área de la transacción';

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN compania_id INT NULL COMMENT 'ID de la compañía (opcional)';

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN auditoria JSON NULL COMMENT 'Información de auditoría (quién, cuándo, qué)';

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación';

ALTER TABLE transacciones_flujo_caja 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de actualización';

-- 3. AGREGAR FOREIGN KEYS (solo si no existen)
ALTER TABLE conceptos_flujo_caja 
ADD CONSTRAINT fk_concepto_dependencia 
FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL;

ALTER TABLE transacciones_flujo_caja 
ADD CONSTRAINT fk_transaccion_concepto 
FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE;

-- 4. AGREGAR ÍNDICES PARA PERFORMANCE
CREATE INDEX idx_conceptos_area ON conceptos_flujo_caja(area);
CREATE INDEX idx_conceptos_activo ON conceptos_flujo_caja(activo);
CREATE INDEX idx_conceptos_orden ON conceptos_flujo_caja(orden_display);

CREATE INDEX idx_transacciones_fecha ON transacciones_flujo_caja(fecha);
CREATE INDEX idx_transacciones_area ON transacciones_flujo_caja(area);
CREATE INDEX idx_transacciones_concepto ON transacciones_flujo_caja(concepto_id);

-- 5. VERIFICAR ESTRUCTURA FINAL
SHOW COLUMNS FROM conceptos_flujo_caja;
SHOW COLUMNS FROM transacciones_flujo_caja;
