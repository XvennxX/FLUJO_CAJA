-- =========================================================
-- INSERTAR CONCEPTOS INICIALES DE FLUJO DE CAJA
-- Basado en los dashboards existentes de Tesorería y Pagaduría
-- =========================================================

-- 1. CONCEPTOS DE TESORERÍA
-- Basados en DashboardTesoreria.tsx

-- Grupo especial: PAGADURIA (saldos iniciales)
INSERT INTO conceptos_flujo_caja 
(nombre, codigo, tipo, area, orden_display, activo, usuario_creacion) VALUES
('SALDO INICIAL', '', 'neutral', 'tesoreria', 1, TRUE, 1),
('CONSUMO', '', 'neutral', 'tesoreria', 2, TRUE, 1),
('VENTANILLA', '', 'neutral', 'tesoreria', 3, TRUE, 1),
('SALDO NETO INICIAL PAGADURÍA', '', 'neutral', 'tesoreria', 4, TRUE, 1),

-- RENTA FIJA
('PAGOS INTERCOMPAÑÍAS', 'I', 'ingreso', 'tesoreria', 5, TRUE, 1),
('PAGOS INTERCOMPAÑÍAS', 'E', 'egreso', 'tesoreria', 6, TRUE, 1),
('INGRESOS INTERESES', 'I', 'ingreso', 'tesoreria', 7, TRUE, 1),
('INGRESO REDENCIÓN TÍTULOS', 'I', 'ingreso', 'tesoreria', 8, TRUE, 1),
('APERTURA ACTIVO FINANCIERO', 'E', 'egreso', 'tesoreria', 9, TRUE, 1),
('CANCELACIÓN ACTIVO FINANCIERO', 'I', 'ingreso', 'tesoreria', 10, TRUE, 1),
('INTERESES ACTIVO FINANCIERO', 'I', 'ingreso', 'tesoreria', 11, TRUE, 1),
('CANCELACIÓN KW', 'E', 'egreso', 'tesoreria', 12, TRUE, 1),
('PAGO INTERESES KW', 'E', 'egreso', 'tesoreria', 13, TRUE, 1),
('APERTURA KW', 'I', 'ingreso', 'tesoreria', 14, TRUE, 1),
('COMPRA TÍTULOS', 'E', 'egreso', 'tesoreria', 15, TRUE, 1),
('COMPRA SIMULTÁNEA ACTIVA', 'E', 'egreso', 'tesoreria', 16, TRUE, 1),
('REDENCIÓN SIMULTÁNEA PASIVA', 'E', 'egreso', 'tesoreria', 17, TRUE, 1),
('VENTA TÍTULOS', 'I', 'ingreso', 'tesoreria', 18, TRUE, 1),
('COMPRA SIMULTÁNEA PASIVA', 'I', 'ingreso', 'tesoreria', 19, TRUE, 1),
('REDENCIÓN SIMULTÁNEA ACTIVA', 'I', 'ingreso', 'tesoreria', 20, TRUE, 1),
('DISTRIBUCIÓN FCP', 'I', 'ingreso', 'tesoreria', 21, TRUE, 1),
('LLAMADO CAPITAL FCP', 'E', 'egreso', 'tesoreria', 22, TRUE, 1),
('RETIRO DE CAPITAL ENCARGOS', 'I', 'ingreso', 'tesoreria', 23, TRUE, 1),
('INCREMENTO DE CAPITAL ENCARGOS', 'E', 'egreso', 'tesoreria', 24, TRUE, 1),
('TRASLADO ARL', '', 'neutral', 'tesoreria', 25, TRUE, 1),

-- RENTA VARIABLE
('COMPRA ACCIONES', 'E', 'egreso', 'tesoreria', 26, TRUE, 1),
('VENTA ACCIONES', 'I', 'ingreso', 'tesoreria', 27, TRUE, 1),
('INGRESO DIVIDENDOS', 'I', 'ingreso', 'tesoreria', 28, TRUE, 1),
('EGRESO DIVIDENDOS', 'E', 'egreso', 'tesoreria', 29, TRUE, 1),
('INGRESO DIVIDENDOS ETF', 'I', 'ingreso', 'tesoreria', 30, TRUE, 1),

-- DERIVADOS
('SWAP', 'E', 'egreso', 'tesoreria', 31, TRUE, 1),
('OPCIONES', 'E', 'egreso', 'tesoreria', 32, TRUE, 1),
('OPCIONES', 'I', 'ingreso', 'tesoreria', 33, TRUE, 1),
('FORWARD', 'E', 'egreso', 'tesoreria', 34, TRUE, 1),
('FORWARD', 'I', 'ingreso', 'tesoreria', 35, TRUE, 1),

-- DIVISAS
('COMPRA DIVISAS OTRAS ÁREAS', 'E', 'egreso', 'tesoreria', 36, TRUE, 1),
('VENTA DIVISAS OTRAS ÁREAS', 'I', 'ingreso', 'tesoreria', 37, TRUE, 1),
('COMPRA DIVISAS REASEGUROS', 'E', 'egreso', 'tesoreria', 38, TRUE, 1),
('COMPRA DIVISAS COMPENSACIÓN', 'E', 'egreso', 'tesoreria', 39, TRUE, 1),
('VENTAS DIVISAS COMPENSACIÓN', 'I', 'ingreso', 'tesoreria', 40, TRUE, 1),

-- OTROS
('GARANTÍA SIMULTÁNEA', 'I', 'ingreso', 'tesoreria', 41, TRUE, 1),
('GARANTÍA SIMULTÁNEA', 'E', 'egreso', 'tesoreria', 42, TRUE, 1),
('EMBARGOS', '', 'neutral', 'tesoreria', 43, TRUE, 1),
('RECAUDO PRIMAS', 'I', 'ingreso', 'tesoreria', 44, TRUE, 1),
('OTROS', '', 'neutral', 'tesoreria', 45, TRUE, 1),
('IMPUESTOS', 'E', 'egreso', 'tesoreria', 46, TRUE, 1),
('COMISIONES', 'E', 'egreso', 'tesoreria', 47, TRUE, 1),
('RENDIMIENTOS', 'I', 'ingreso', 'tesoreria', 48, TRUE, 1),
('GMF', 'E', 'egreso', 'tesoreria', 49, TRUE, 1);

-- 2. CONCEPTOS DE PAGADURÍA
-- Basados en DashboardPagaduria.tsx

INSERT INTO conceptos_flujo_caja 
(nombre, codigo, tipo, area, orden_display, activo, usuario_creacion) VALUES
('DIFERENCIA SALDOS', '', 'neutral', 'pagaduria', 1, TRUE, 1),
('SALDOS EN BANCOS', '', 'neutral', 'pagaduria', 2, TRUE, 1),
('SALDO DIA ANTERIOR', 'I', 'ingreso', 'pagaduria', 3, TRUE, 1),
('INGRESO', 'I', 'ingreso', 'pagaduria', 4, TRUE, 1),
('EGRESO', 'E', 'egreso', 'pagaduria', 5, TRUE, 1),
('CONSUMO NACIONAL', 'E', 'egreso', 'pagaduria', 6, TRUE, 1),
('INGRESO CTA PAGADURIA', 'I', 'ingreso', 'pagaduria', 7, TRUE, 1),
('FINANSEGUROS', 'I', 'ingreso', 'pagaduria', 8, TRUE, 1),
('RECAUDOS LIBERTADOR', 'I', 'ingreso', 'pagaduria', 9, TRUE, 1),
('RENDIMIENTOS FINANCIEROS', 'I', 'ingreso', 'pagaduria', 10, TRUE, 1),
('INGRESOS REASEGUROS', 'I', 'ingreso', 'pagaduria', 11, TRUE, 1),
('EGR. REASEGUROS', 'E', 'egreso', 'pagaduria', 12, TRUE, 1),
('ING. COMPRA DE DIVISAS-REASEGUR', 'I', 'ingreso', 'pagaduria', 13, TRUE, 1),
('EGR. VENTA DIVISAS-REASEGUROS', 'E', 'egreso', 'pagaduria', 14, TRUE, 1),
('EGRESO - TRASLADOS COMPAÑÍAS', 'E', 'egreso', 'pagaduria', 15, TRUE, 1),
('INGRESO - TRASLADOS COMPAÑÍAS', 'I', 'ingreso', 'pagaduria', 16, TRUE, 1),
('EMBARGOS', 'E', 'egreso', 'pagaduria', 17, TRUE, 1),
('OTROS PAGOS', 'E', 'egreso', 'pagaduria', 18, TRUE, 1),
('VENTAN PROVEEDORES', 'E', 'egreso', 'pagaduria', 19, TRUE, 1),
('INTERCIAS RELAC./INDUS', '', 'neutral', 'pagaduria', 20, TRUE, 1),
('COMISIONES DAVIVIENDA', 'E', 'egreso', 'pagaduria', 21, TRUE, 1),
('NOMINA CONSEJEROS', 'E', 'egreso', 'pagaduria', 22, TRUE, 1),
('NOMINA ADMINISTRATIVA', '', 'neutral', 'pagaduria', 23, TRUE, 1),
('NOMINA PENSIONES', '', 'neutral', 'pagaduria', 24, TRUE, 1),
('PAGO SOI', 'E', 'egreso', 'pagaduria', 25, TRUE, 1),
('PAGO IVA', 'E', 'egreso', 'pagaduria', 26, TRUE, 1),
('OTROS IMPTOS', 'E', 'egreso', 'pagaduria', 27, TRUE, 1),
('EGRESO DIVIDENDOS', 'E', 'egreso', 'pagaduria', 28, TRUE, 1),
('CUATRO POR MIL', 'E', 'egreso', 'pagaduria', 29, TRUE, 1),
('DIFERENCIA EN CAMBIO CTAS REASEGUROS', '', 'neutral', 'pagaduria', 30, TRUE, 1);

-- 3. VERIFICAR DATOS INSERTADOS
SELECT 
    area,
    COUNT(*) as total_conceptos,
    SUM(CASE WHEN tipo = 'ingreso' THEN 1 ELSE 0 END) as ingresos,
    SUM(CASE WHEN tipo = 'egreso' THEN 1 ELSE 0 END) as egresos,
    SUM(CASE WHEN tipo = 'neutral' THEN 1 ELSE 0 END) as neutrales
FROM conceptos_flujo_caja 
WHERE activo = TRUE 
GROUP BY area;

-- 4. MOSTRAR CONCEPTOS POR ÁREA
SELECT 
    id,
    nombre,
    codigo,
    tipo,
    area,
    orden_display
FROM conceptos_flujo_caja 
WHERE area = 'tesoreria' 
ORDER BY orden_display 
LIMIT 10;

SELECT 
    id,
    nombre,
    codigo,
    tipo,
    area,
    orden_display
FROM conceptos_flujo_caja 
WHERE area = 'pagaduria' 
ORDER BY orden_display 
LIMIT 10;
