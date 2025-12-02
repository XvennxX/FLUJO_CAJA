# Fix: GMF auto-recalcular y mostrar valor persistido

## Problema
El GMF solo se mostraba al abrir el modal de configuración. No se recalculaba automáticamente al crear/editar transacciones de conceptos base.

## Causa raíz
1. El frontend calculaba GMF localmente en lugar de leer el valor persistido en BD
2. La configuración GMF incluía conceptos calculados/subtotales, causando duplicación (12 en lugar de 4)

## Solución implementada

### Backend
1. **Corregida configuración GMF** (`initialize_gmf_defaults.py`)
   - Excluye conceptos calculados: 2,3,4,49,50,51,52,54,82,83,84,85
   - Solo incluye conceptos base/manuales para evitar duplicación
   - Script actualizado para regenerar configs existentes

2. **Script de recálculo** (`recalcular_gmf_existentes.py`)
   - Recalcula todos los GMF mal guardados
   - Resultados: Cuenta 3: 12.00 → 4.00 ✅

3. **Persistencia automática** (ya implementada)
   - `crear_transaccion`: Persiste GMF después de crear cualquier transacción
   - `actualizar_transaccion`: Persiste GMF después de actualizar
   - Endpoint `/api/v1/gmf/recalculate`: Fuerza recálculo manual

### Frontend
1. **Mostrar valor persistido** (`DashboardTesoreria.tsx`)
   - Cambió `calcularGMF(account.id)` → `obtenerMonto(concepto.id, account.id)`
   - Ahora lee el GMF de la BD en lugar de calcularlo localmente
   - El backend ya lo persiste automáticamente

2. **Forzar recálculo al guardar config**
   - `guardarConceptosGMF` ahora llama a `/api/v1/gmf/recalculate`
   - Recarga transacciones para mostrar el valor actualizado

## Flujo actual
1. Usuario crea/edita concepto base → Backend persiste GMF automáticamente
2. Frontend recarga (después de 100ms) → Muestra GMF persistido
3. Usuario abre config GMF → Cambia conceptos → Guarda
4. Backend recalcula con nueva config → Frontend recarga → Muestra nuevo GMF

## Fórmula GMF
```
GMF = SUM(conceptos_base_con_signo) × 4/1000
```

Para 1000 en componentes base → GMF = 4.00 ✅

## Archivos modificados
- `Back-FC/scripts/setup/initialize_gmf_defaults.py`: Excluir conceptos calculados
- `Back-FC/scripts/setup/recalcular_gmf_existentes.py`: Script de corrección (nuevo)
- `Front-FC/src/components/Pages/DashboardTesoreria.tsx`: Leer GMF persistido + forzar recálculo al guardar config
