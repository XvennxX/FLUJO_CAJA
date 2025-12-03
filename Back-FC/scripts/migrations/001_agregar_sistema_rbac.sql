-- ============================================================================
-- MIGRACIÓN: Agregar Sistema de Roles y Permisos (RBAC)
-- Fecha: 2025-11-11
-- Descripción: Crea tablas para roles, permisos y actualiza usuarios
-- ============================================================================

-- 1. Crear tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    es_sistema BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Crear tabla de permisos
CREATE TABLE IF NOT EXISTS permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    modulo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_modulo (modulo),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Crear tabla de relación roles-permisos (Many-to-Many)
CREATE TABLE IF NOT EXISTS rol_permiso (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE,
    INDEX idx_rol_id (rol_id),
    INDEX idx_permiso_id (permiso_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Agregar columna rol_id a tabla usuarios (nullable para compatibilidad)
ALTER TABLE usuarios 
ADD COLUMN rol_id INT NULL,
ADD CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL,
ADD INDEX idx_rol_id (rol_id);

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Verificar que las tablas se crearon correctamente
SELECT 
    'roles' as tabla, COUNT(*) as registros FROM roles
UNION ALL
SELECT 
    'permisos' as tabla, COUNT(*) as registros FROM permisos
UNION ALL
SELECT 
    'rol_permiso' as tabla, COUNT(*) as registros FROM rol_permiso;

-- Verificar columna rol_id en usuarios
DESCRIBE usuarios;

-- ============================================================================
-- NOTAS
-- ============================================================================
-- 
-- Después de ejecutar esta migración, ejecutar:
-- python -m scripts.setup.init_roles_permisos
-- 
-- Esto creará:
-- - 35+ permisos en 10 módulos
-- - 5 roles predefinidos (ADMIN, TESORERIA, PAGADURIA, MESA_DINERO, CONSULTA)
-- - Migrará usuarios existentes del campo 'rol' (string) a 'rol_id' (FK)
-- ============================================================================
