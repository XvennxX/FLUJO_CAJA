-- =========================================================
-- COMPLETAR TABLA: conceptos_flujo_caja
-- Agregar campos faltantes para funcionalidad completa
-- =========================================================

-- 1. AGREGAR CAMPOS DE ÁREA Y ORDEN
ALTER TABLE conceptos_flujo_caja 
ADD COLUMN area ENUM('tesoreria','pagaduria','ambas') NOT NULL DEFAULT 'ambas' 
COMMENT 'Área donde aparece el concepto' AFTER codigo;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN orden_display INT DEFAULT 0 
COMMENT 'Orden en el dashboard' AFTER area;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN activo BOOLEAN DEFAULT TRUE 
COMMENT 'Si está activo para usar' AFTER orden_display;

-- 2. AGREGAR CAMPOS DE DEPENDENCIAS AUTOMÁTICAS
ALTER TABLE conceptos_flujo_caja 
ADD COLUMN depende_de_concepto_id INT NULL 
COMMENT 'Concepto del cual depende automáticamente' AFTER activo;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN tipo_dependencia ENUM('copia','suma','resta') NULL 
COMMENT 'Tipo de cálculo automático' AFTER depende_de_concepto_id;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN factor DECIMAL(10,4) DEFAULT 1.0000 
COMMENT 'Factor multiplicador para el cálculo' AFTER tipo_dependencia;

-- 3. AGREGAR CAMPOS DE AUDITORÍA
ALTER TABLE conceptos_flujo_caja 
ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
AFTER factor;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
AFTER fecha_creacion;

ALTER TABLE conceptos_flujo_caja 
ADD COLUMN usuario_creacion INT NULL 
COMMENT 'Usuario que creó el concepto' AFTER fecha_modificacion;

-- 4. AGREGAR FOREIGN KEYS
ALTER TABLE conceptos_flujo_caja 
ADD CONSTRAINT fk_concepto_dependencia 
FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL;

ALTER TABLE conceptos_flujo_caja 
ADD CONSTRAINT fk_concepto_usuario 
FOREIGN KEY (usuario_creacion) REFERENCES users(id) ON DELETE SET NULL;

-- 5. AGREGAR ÍNDICES
ALTER TABLE conceptos_flujo_caja 
ADD INDEX idx_area_activo (area, activo);

ALTER TABLE conceptos_flujo_caja 
ADD INDEX idx_orden_display (orden_display);

ALTER TABLE conceptos_flujo_caja 
ADD INDEX idx_dependencia (depende_de_concepto_id);

-- 6. AGREGAR CONSTRAINT DE VALIDACIÓN
ALTER TABLE conceptos_flujo_caja 
ADD CONSTRAINT chk_dependencia_valida CHECK (
    (depende_de_concepto_id IS NULL AND tipo_dependencia IS NULL) OR
    (depende_de_concepto_id IS NOT NULL AND tipo_dependencia IS NOT NULL)
);

-- 7. VERIFICAR ESTRUCTURA ACTUALIZADA
DESCRIBE conceptos_flujo_caja;
