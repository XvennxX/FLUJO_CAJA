-- Script de inicialización para MySQL
-- Sistema de Flujo de Caja

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS flujo_caja_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos
USE flujo_caja_db;

-- Crear usuario para la aplicación (opcional)
-- CREATE USER IF NOT EXISTS 'flujo_user'@'localhost' IDENTIFIED BY 'flujo_pass_2025';
-- GRANT ALL PRIVILEGES ON flujo_caja_db.* TO 'flujo_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Configuraciones adicionales para MySQL
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- Verificar la configuración
SHOW VARIABLES LIKE 'character_set_database';
SHOW VARIABLES LIKE 'collation_database';

-- Mensaje de confirmación
SELECT 'Base de datos flujo_caja_db creada exitosamente' AS status;
