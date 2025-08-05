-- Crear base de datos y usuario para el sistema de flujo de caja
-- Ejecutar con privilegios de administrador

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS flujo_caja
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Crear usuario para la aplicación (opcional)
-- CREATE USER 'flujo_caja_user'@'localhost' IDENTIFIED BY 'secure_password_123';
-- GRANT ALL PRIVILEGES ON flujo_caja.* TO 'flujo_caja_user'@'localhost';
-- FLUSH PRIVILEGES;

USE flujo_caja;
