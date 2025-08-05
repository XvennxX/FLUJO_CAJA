-- Vistas para reportes del sistema de flujo de caja
USE flujo_caja;

-- Vista: Resumen diario de movimientos
CREATE VIEW vista_resumen_diario AS
SELECT 
    DATE(COALESCE(i.fecha, e.fecha)) as fecha,
    c.id_cuenta,
    c.nombre as cuenta_nombre,
    COALESCE(SUM(i.monto), 0) as total_ingresos,
    COALESCE(SUM(e.monto), 0) as total_egresos,
    (COALESCE(SUM(i.monto), 0) - COALESCE(SUM(e.monto), 0)) as flujo_neto,
    COUNT(DISTINCT i.id_ingreso) as cantidad_ingresos,
    COUNT(DISTINCT e.id_egreso) as cantidad_egresos
FROM cuenta c
LEFT JOIN ingreso i ON c.id_cuenta = i.id_cuenta AND i.estado = 'ACTIVO'
LEFT JOIN egreso e ON c.id_cuenta = e.id_cuenta AND e.estado = 'ACTIVO'
GROUP BY DATE(COALESCE(i.fecha, e.fecha)), c.id_cuenta, c.nombre
HAVING fecha IS NOT NULL
ORDER BY fecha DESC, c.nombre;

-- Vista: Movimientos por concepto
CREATE VIEW vista_movimientos_concepto AS
SELECT 
    con.id_concepto,
    con.nombre as concepto_nombre,
    con.tipo,
    COUNT(CASE WHEN con.tipo = 'INGRESO' THEN i.id_ingreso END) as cantidad_ingresos,
    COUNT(CASE WHEN con.tipo = 'EGRESO' THEN e.id_egreso END) as cantidad_egresos,
    COALESCE(SUM(CASE WHEN con.tipo = 'INGRESO' THEN i.monto END), 0) as total_ingresos,
    COALESCE(SUM(CASE WHEN con.tipo = 'EGRESO' THEN e.monto END), 0) as total_egresos
FROM concepto con
LEFT JOIN ingreso i ON con.id_concepto = i.id_concepto AND i.estado = 'ACTIVO'
LEFT JOIN egreso e ON con.id_concepto = e.id_concepto AND e.estado = 'ACTIVO'
WHERE con.estado = TRUE
GROUP BY con.id_concepto, con.nombre, con.tipo
ORDER BY con.tipo, con.nombre;

-- Vista: Saldos por cuenta
CREATE VIEW vista_saldos_cuenta AS
SELECT 
    c.id_cuenta,
    c.nombre as cuenta_nombre,
    c.saldo_inicial,
    COALESCE(SUM(i.monto), 0) as total_ingresos,
    COALESCE(SUM(e.monto), 0) as total_egresos,
    (c.saldo_inicial + COALESCE(SUM(i.monto), 0) - COALESCE(SUM(e.monto), 0)) as saldo_calculado,
    c.saldo_actual,
    c.estado,
    c.updated_at as ultima_actualizacion
FROM cuenta c
LEFT JOIN ingreso i ON c.id_cuenta = i.id_cuenta AND i.estado = 'ACTIVO'
LEFT JOIN egreso e ON c.id_cuenta = e.id_cuenta AND e.estado = 'ACTIVO'
GROUP BY c.id_cuenta, c.nombre, c.saldo_inicial, c.saldo_actual, c.estado, c.updated_at
ORDER BY c.nombre;

-- Vista: Flujo de caja mensual
CREATE VIEW vista_flujo_mensual AS
SELECT 
    YEAR(COALESCE(i.fecha, e.fecha)) as año,
    MONTH(COALESCE(i.fecha, e.fecha)) as mes,
    MONTHNAME(COALESCE(i.fecha, e.fecha)) as nombre_mes,
    c.id_cuenta,
    c.nombre as cuenta_nombre,
    COALESCE(SUM(i.monto), 0) as ingresos_mes,
    COALESCE(SUM(e.monto), 0) as egresos_mes,
    (COALESCE(SUM(i.monto), 0) - COALESCE(SUM(e.monto), 0)) as flujo_neto_mes
FROM cuenta c
LEFT JOIN ingreso i ON c.id_cuenta = i.id_cuenta AND i.estado = 'ACTIVO'
LEFT JOIN egreso e ON c.id_cuenta = e.id_cuenta AND e.estado = 'ACTIVO'
GROUP BY YEAR(COALESCE(i.fecha, e.fecha)), MONTH(COALESCE(i.fecha, e.fecha)), c.id_cuenta, c.nombre
HAVING año IS NOT NULL AND mes IS NOT NULL
ORDER BY año DESC, mes DESC, c.nombre;

-- Vista: Actividad de usuarios
CREATE VIEW vista_actividad_usuarios AS
SELECT 
    u.id_usuario,
    u.nombre_completo,
    u.correo,
    r.nombre_rol,
    COUNT(DISTINCT i.id_ingreso) as ingresos_registrados,
    COUNT(DISTINCT e.id_egreso) as egresos_registrados,
    COALESCE(SUM(i.monto), 0) as monto_total_ingresos,
    COALESCE(SUM(e.monto), 0) as monto_total_egresos,
    u.ultimo_acceso,
    u.estado as usuario_activo
FROM usuario u
INNER JOIN rol r ON u.id_rol = r.id_rol
LEFT JOIN ingreso i ON u.id_usuario = i.id_usuario AND i.estado = 'ACTIVO'
LEFT JOIN egreso e ON u.id_usuario = e.id_usuario AND e.estado = 'ACTIVO'
GROUP BY u.id_usuario, u.nombre_completo, u.correo, r.nombre_rol, u.ultimo_acceso, u.estado
ORDER BY u.nombre_completo;
