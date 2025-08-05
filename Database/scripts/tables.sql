-- Creación de tablas para el sistema de flujo de caja
USE flujo_caja;

-- Roles
CREATE TABLE rol (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Usuarios
CREATE TABLE usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre_completo VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

-- Cuentas o cajas
CREATE TABLE cuenta (
    id_cuenta INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    saldo_inicial DECIMAL(15,2) DEFAULT 0.00,
    estado BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Conceptos de ingreso o egreso
CREATE TABLE concepto (
    id_concepto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo ENUM('INGRESO', 'EGRESO') NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Ingresos
CREATE TABLE ingreso (
    id_ingreso INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME NOT NULL,
    monto DECIMAL(15,2) NOT NULL CHECK (monto > 0),
    descripcion TEXT,
    comprobante VARCHAR(100),
    id_concepto INT NOT NULL,
    id_usuario INT NOT NULL,
    id_cuenta INT NOT NULL,
    estado ENUM('ACTIVO', 'ANULADO') DEFAULT 'ACTIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_concepto) REFERENCES concepto(id_concepto),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta)
);

-- Egresos
CREATE TABLE egreso (
    id_egreso INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME NOT NULL,
    monto DECIMAL(15,2) NOT NULL CHECK (monto > 0),
    descripcion TEXT,
    comprobante VARCHAR(100),
    id_concepto INT NOT NULL,
    id_usuario INT NOT NULL,
    id_cuenta INT NOT NULL,
    estado ENUM('ACTIVO', 'ANULADO') DEFAULT 'ACTIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_concepto) REFERENCES concepto(id_concepto),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta)
);

-- Auditoría
CREATE TABLE auditoria (
    id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    accion TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    tabla_afectada VARCHAR(50),
    id_registro_afectado INT,
    datos_anteriores JSON,
    datos_nuevos JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Historial de sesión
CREATE TABLE sesion_usuario (
    id_sesion INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    token_session VARCHAR(255),
    inicio_sesion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fin_sesion DATETIME NULL,
    ip VARCHAR(45),
    user_agent TEXT,
    estado ENUM('ACTIVA', 'CERRADA', 'EXPIRADA') DEFAULT 'ACTIVA',
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);
