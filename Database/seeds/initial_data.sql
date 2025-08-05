-- Datos iniciales para roles
USE flujo_caja;

INSERT INTO rol (nombre_rol, descripcion) VALUES 
('ADMINISTRADOR', 'Usuario con acceso completo al sistema'),
('SUPERVISOR', 'Usuario con permisos de supervisión y reportes'),
('OPERADOR', 'Usuario básico para registro de movimientos'),
('CONTADOR', 'Usuario especializado en reportes contables');

-- Datos iniciales para conceptos
INSERT INTO concepto (nombre, descripcion, tipo, estado) VALUES 
-- Conceptos de INGRESO
('Venta de Productos', 'Ingresos por venta de productos principales', 'INGRESO', TRUE),
('Venta de Servicios', 'Ingresos por prestación de servicios', 'INGRESO', TRUE),
('Intereses Bancarios', 'Intereses generados por depósitos bancarios', 'INGRESO', TRUE),
('Descuentos Recibidos', 'Descuentos obtenidos de proveedores', 'INGRESO', TRUE),
('Otros Ingresos', 'Ingresos diversos no clasificados', 'INGRESO', TRUE),
('Préstamos Recibidos', 'Capital recibido por préstamos', 'INGRESO', TRUE),
('Aportes de Socios', 'Capital aportado por socios', 'INGRESO', TRUE),

-- Conceptos de EGRESO
('Compra de Mercancía', 'Adquisición de productos para venta', 'EGRESO', TRUE),
('Gastos de Oficina', 'Papelería, útiles y suministros de oficina', 'EGRESO', TRUE),
('Servicios Públicos', 'Electricidad, agua, gas, internet', 'EGRESO', TRUE),
('Nómina', 'Salarios y prestaciones del personal', 'EGRESO', TRUE),
('Arrendamientos', 'Pago de arriendos y alquileres', 'EGRESO', TRUE),
('Mantenimiento', 'Gastos de mantenimiento y reparaciones', 'EGRESO', TRUE),
('Impuestos', 'Pago de impuestos y tasas', 'EGRESO', TRUE),
('Intereses Pagados', 'Intereses por préstamos y financiaciones', 'EGRESO', TRUE),
('Publicidad', 'Gastos en marketing y publicidad', 'EGRESO', TRUE),
('Transporte', 'Gastos de transporte y combustible', 'EGRESO', TRUE),
('Seguros', 'Pago de pólizas de seguros', 'EGRESO', TRUE),
('Otros Gastos', 'Gastos diversos no clasificados', 'EGRESO', TRUE);

-- Cuenta inicial por defecto
INSERT INTO cuenta (nombre, descripcion, saldo_inicial, saldo_actual, estado) VALUES 
('Caja Principal', 'Caja principal de la empresa', 0.00, 0.00, TRUE),
('Banco Cuenta Corriente', 'Cuenta corriente bancaria principal', 0.00, 0.00, TRUE),
('Banco Cuenta Ahorros', 'Cuenta de ahorros para reservas', 0.00, 0.00, TRUE);

-- Usuario administrador por defecto (contraseña: admin123)
-- NOTA: En producción cambiar esta contraseña
INSERT INTO usuario (nombre_completo, correo, contraseña, id_rol, estado) VALUES 
('Administrador Sistema', 'admin@empresa.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewaBnBdmCrrHm/Ve', 1, TRUE);
