-- Índices para optimización del sistema de flujo de caja
USE flujo_caja;

-- Índices para tabla usuario
CREATE INDEX idx_usuario_correo ON usuario(correo);
CREATE INDEX idx_usuario_rol ON usuario(id_rol);
CREATE INDEX idx_usuario_estado ON usuario(estado);

-- Índices para tabla cuenta
CREATE INDEX idx_cuenta_estado ON cuenta(estado);
CREATE INDEX idx_cuenta_nombre ON cuenta(nombre);

-- Índices para tabla concepto
CREATE INDEX idx_concepto_tipo ON concepto(tipo);
CREATE INDEX idx_concepto_estado ON concepto(estado);

-- Índices para tabla ingreso
CREATE INDEX idx_ingreso_fecha ON ingreso(fecha);
CREATE INDEX idx_ingreso_usuario ON ingreso(id_usuario);
CREATE INDEX idx_ingreso_cuenta ON ingreso(id_cuenta);
CREATE INDEX idx_ingreso_concepto ON ingreso(id_concepto);
CREATE INDEX idx_ingreso_estado ON ingreso(estado);
CREATE INDEX idx_ingreso_fecha_cuenta ON ingreso(fecha, id_cuenta);
CREATE INDEX idx_ingreso_monto ON ingreso(monto);

-- Índices para tabla egreso
CREATE INDEX idx_egreso_fecha ON egreso(fecha);
CREATE INDEX idx_egreso_usuario ON egreso(id_usuario);
CREATE INDEX idx_egreso_cuenta ON egreso(id_cuenta);
CREATE INDEX idx_egreso_concepto ON egreso(id_concepto);
CREATE INDEX idx_egreso_estado ON egreso(estado);
CREATE INDEX idx_egreso_fecha_cuenta ON egreso(fecha, id_cuenta);
CREATE INDEX idx_egreso_monto ON egreso(monto);

-- Índices para tabla auditoria
CREATE INDEX idx_auditoria_usuario ON auditoria(id_usuario);
CREATE INDEX idx_auditoria_fecha ON auditoria(fecha);
CREATE INDEX idx_auditoria_tabla ON auditoria(tabla_afectada);
CREATE INDEX idx_auditoria_fecha_usuario ON auditoria(fecha, id_usuario);

-- Índices para tabla sesion_usuario
CREATE INDEX idx_sesion_usuario ON sesion_usuario(id_usuario);
CREATE INDEX idx_sesion_inicio ON sesion_usuario(inicio_sesion);
CREATE INDEX idx_sesion_estado ON sesion_usuario(estado);
CREATE INDEX idx_sesion_token ON sesion_usuario(token_session);
