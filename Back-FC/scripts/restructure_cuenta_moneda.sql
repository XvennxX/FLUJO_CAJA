-- Script para reestructurar las cuentas bancarias con tabla intermedia para monedas
-- Autor: Sistema de Gestión de Cuentas Bancarias
-- Fecha: 20 de agosto de 2025

-- 1. Crear la tabla intermedia cuenta_moneda
CREATE TABLE cuenta_moneda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cuenta INT NOT NULL,
    moneda ENUM('COP', 'USD', 'EUR') NOT NULL,
    FOREIGN KEY (id_cuenta) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cuenta_moneda (id_cuenta, moneda)
);

-- 2. Migrar datos existentes (si los hay)
-- Insertar registros en cuenta_moneda basados en los datos actuales de cuentas_bancarias
INSERT INTO cuenta_moneda (id_cuenta, moneda)
SELECT id, moneda 
FROM cuentas_bancarias 
WHERE moneda IS NOT NULL;

-- 3. Eliminar la columna moneda de cuentas_bancarias
ALTER TABLE cuentas_bancarias DROP COLUMN moneda;

-- 4. Verificar la estructura actualizada
DESCRIBE cuentas_bancarias;
DESCRIBE cuenta_moneda;

-- 5. Verificar los datos migrados
SELECT 
    cb.id,
    cb.numero_cuenta,
    cb.tipo_cuenta,
    GROUP_CONCAT(cm.moneda) as monedas_disponibles
FROM cuentas_bancarias cb
LEFT JOIN cuenta_moneda cm ON cb.id = cm.id_cuenta
GROUP BY cb.id, cb.numero_cuenta, cb.tipo_cuenta;
