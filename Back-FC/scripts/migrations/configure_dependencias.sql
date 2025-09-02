-- =========================================================
-- CONFIGURAR DEPENDENCIAS AUTOMÁTICAS ENTRE CONCEPTOS
-- Relaciones de cálculo automático entre áreas
-- =========================================================

-- IMPORTANTE: Ejecutar DESPUÉS de insertar los conceptos iniciales

-- 1. DEPENDENCIA PRINCIPAL: SALDO NETO INICIAL PAGADURÍA (tesorería) depende de SALDO DIA ANTERIOR (pagaduría)
-- Cuando se actualice el SALDO DIA ANTERIOR en pagaduría, se copiará automáticamente al SALDO NETO INICIAL en tesorería

UPDATE conceptos_flujo_caja 
SET 
    depende_de_concepto_id = (
        SELECT id FROM conceptos_flujo_caja c2 
        WHERE c2.nombre = 'SALDO DIA ANTERIOR' AND c2.area = 'pagaduria' 
        LIMIT 1
    ),
    tipo_dependencia = 'copia',
    factor = 1.0000
WHERE nombre = 'SALDO NETO INICIAL PAGADURÍA' AND area = 'tesoreria';

-- 2. EJEMPLO DE DEPENDENCIA SUMA: Si quisiéramos que un concepto sume valores
-- UPDATE conceptos_flujo_caja 
-- SET 
--     depende_de_concepto_id = (SELECT id FROM conceptos_flujo_caja WHERE nombre = 'INGRESO' AND area = 'pagaduria' LIMIT 1),
--     tipo_dependencia = 'suma',
--     factor = 0.1000  -- 10% del valor original
-- WHERE nombre = 'COMISIONES' AND area = 'tesoreria';

-- 3. VERIFICAR DEPENDENCIAS CONFIGURADAS
SELECT 
    c1.id,
    c1.nombre as concepto_destino,
    c1.area as area_destino,
    c2.nombre as concepto_origen,
    c2.area as area_origen,
    c1.tipo_dependencia,
    c1.factor
FROM conceptos_flujo_caja c1
LEFT JOIN conceptos_flujo_caja c2 ON c1.depende_de_concepto_id = c2.id
WHERE c1.depende_de_concepto_id IS NOT NULL
ORDER BY c1.area, c1.orden_display;

-- 4. FUNCIÓN PARA AGREGAR NUEVAS DEPENDENCIAS (ejemplo de uso)
-- Para agregar una nueva dependencia, usar esta estructura:
/*
UPDATE conceptos_flujo_caja 
SET 
    depende_de_concepto_id = (
        SELECT id FROM conceptos_flujo_caja 
        WHERE nombre = 'NOMBRE_CONCEPTO_ORIGEN' AND area = 'AREA_ORIGEN' 
        LIMIT 1
    ),
    tipo_dependencia = 'copia',  -- o 'suma' o 'resta'
    factor = 1.0000              -- factor multiplicador
WHERE nombre = 'NOMBRE_CONCEPTO_DESTINO' AND area = 'AREA_DESTINO';
*/

-- 5. MOSTRAR RESUMEN DE CONFIGURACIÓN
SELECT 
    'DEPENDENCIAS CONFIGURADAS' as resumen,
    COUNT(*) as total
FROM conceptos_flujo_caja 
WHERE depende_de_concepto_id IS NOT NULL;

SELECT 
    'CONCEPTOS SIN DEPENDENCIAS' as resumen,
    COUNT(*) as total
FROM conceptos_flujo_caja 
WHERE depende_de_concepto_id IS NULL;
