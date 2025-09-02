-- Script para agregar la columna tipo_cuenta a la tabla cuentas_bancarias
-- Autor: Sistema de Gestión de Cuentas Bancarias
-- Fecha: 20 de agosto de 2025

-- Verificar la estructura actual de la tabla
-- DESCRIBE cuentas_bancarias;

-- Agregar la nueva columna tipo_cuenta
ALTER TABLE cuentas_bancarias 
ADD COLUMN tipo_cuenta ENUM('CORRIENTE', 'AHORROS') NOT NULL DEFAULT 'CORRIENTE' 
AFTER moneda;

-- Verificar que la columna se agregó correctamente
DESCRIBE cuentas_bancarias;

-- Opcional: Actualizar registros existentes si necesitas cambiar algunos a AHORROS
-- UPDATE cuentas_bancarias SET tipo_cuenta = 'AHORROS' WHERE id IN (1, 2, 3);

-- Verificar los datos después del cambio
SELECT id, numero_cuenta, compania_id, banco_id, moneda, tipo_cuenta 
FROM cuentas_bancarias;
