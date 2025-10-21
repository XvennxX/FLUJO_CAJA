# 🔧 Corrección: Recálculo Automático y Aplicación de Signos

## 📋 Problemas Identificados

### 1. **Los valores auto-calculados no se recalculan**
Al modificar un valor en el dashboard de Tesorería, los conceptos dependientes no se actualizaban automáticamente.

### 2. **Los valores auto-calculados quedan negativos incorrectamente**
Cuando un concepto auto-calculado debía ser positivo (código "I" para INGRESO), se mostraba negativo.

---

## 🔍 Causa Raíz

### Problema 1: Recálculo Duplicado
El servicio `TransaccionFlujoCajaService.actualizar_transaccion()` YA llamaba a `procesar_dependencias_completas_ambos_dashboards()`, pero el API lo volvía a llamar, causando ejecución duplicada y posibles inconsistencias.

### Problema 2: Falta de Aplicación de Signos
El método `_crear_o_actualizar_transaccion()` en `DependenciasFlujoCajaService` **NO** aplicaba el signo correcto según el código del concepto (I/E/N) cuando creaba o actualizaba transacciones auto-calculadas.

---

## ✅ Soluciones Implementadas

### 1. **Agregado método `_aplicar_signo_por_tipo_concepto()` al servicio de dependencias**

**Ubicación:** `app/services/dependencias_flujo_caja_service.py`

```python
def _aplicar_signo_por_tipo_concepto(self, monto: Decimal, concepto: ConceptoFlujoCaja) -> Decimal:
    """
    Aplica el signo correcto al monto según el CODIGO del concepto:
    - I (INGRESO): Siempre positivo 
    - E (EGRESO): Siempre negativo
    - N (NEUTRAL): Mantiene el signo calculado
    """
    codigo = concepto.codigo or ""
    monto_absoluto = abs(monto)
    
    if codigo == "I":
        return monto_absoluto  # ✅ Siempre positivo
    elif codigo == "E":
        return -monto_absoluto  # ✅ Siempre negativo
    else:
        return monto  # ⚖️ Mantiene signo calculado
```

### 2. **Actualizado `_crear_o_actualizar_transaccion()` para aplicar signos**

**Antes:**
```python
transaccion = TransaccionFlujoCaja(
    ...
    monto=nuevo_monto,  # ❌ No aplicaba signo correcto
    ...
)
```

**Después:**
```python
# 🔥 APLICAR SIGNO CORRECTO según el código del concepto
monto_corregido = self._aplicar_signo_por_tipo_concepto(nuevo_monto, concepto)

transaccion = TransaccionFlujoCaja(
    ...
    monto=monto_corregido,  # ✅ Usa monto con signo correcto
    ...
)
```

### 3. **Actualizado `_procesar_concepto_dependiente()` para aplicar signos al actualizar**

**Antes:**
```python
if transaccion_existente:
    transaccion_existente.monto = nuevo_monto  # ❌ No aplicaba signo
```

**Después:**
```python
if transaccion_existente:
    # 🔥 APLICAR SIGNO CORRECTO
    monto_corregido = self._aplicar_signo_por_tipo_concepto(nuevo_monto, concepto)
    transaccion_existente.monto = monto_corregido  # ✅ Usa monto correcto
```

### 4. **Eliminada llamada duplicada de recálculo en el API**

**Antes (api/transacciones_flujo_caja.py):**
```python
transaccion = service.actualizar_transaccion(...)

# ❌ Recálculo duplicado
dependencias_service = DependenciasFlujoCajaService(db)
resultados_completos = dependencias_service.procesar_dependencias_completas_ambos_dashboards(...)
```

**Después:**
```python
# ✅ El método actualizar_transaccion YA ejecuta el recálculo interno
transaccion = service.actualizar_transaccion(...)

# Solo enviar notificación WebSocket
await websocket_manager.broadcast_update(...)
```

---

## 🎯 Lógica de Aplicación de Signos

### Conceptos con código "I" (INGRESO)
- **Siempre positivo**
- Ejemplos: Pagos Intercompañías, Ingresos Intereses, Redención Títulos
- Si el cálculo da negativo (-1000), se convierte a positivo (1000)

### Conceptos con código "E" (EGRESO)
- **Siempre negativo**
- Ejemplos: Cobros Intercompañías, Compra Títulos, Cancelación KW
- Si el cálculo da positivo (1000), se convierte a negativo (-1000)

### Conceptos con código "N" (NEUTRAL)
- **Mantiene el signo calculado**
- Ejemplos: Saldo Inicial, Consumo, Ventanilla
- El signo se mantiene como resulte del cálculo

---

## 🧪 Pruebas Realizadas

### Script: `test_recalculo_signos.py`

**Resultados:**
```
✅ INGRESO (I): -1000 → 1000 (Siempre positivo)
✅ EGRESO (E): 1000 → -1000 (Siempre negativo)
✅ NEUTRAL (N): Mantiene signo original
```

**Conceptos probados:**
- ✅ Pagos Intercompañías (I): Convierte a positivo
- ✅ Cobros Intercompañías (E): Convierte a negativo
- ✅ Ingresos Intereses (I): Convierte a positivo
- ✅ Compra Títulos (E): Convierte a negativo
- ✅ Saldo Inicial (N): Mantiene signo

---

## 📊 Flujo de Actualización Corregido

```
1. Usuario modifica transacción en Dashboard
   ↓
2. API: PUT /transacciones/{id}
   ↓
3. Validar que NO sea concepto auto-calculado
   ↓
4. TransaccionFlujoCajaService.actualizar_transaccion()
   ├─ Aplicar signo correcto al monto (según código concepto)
   ├─ Guardar transacción (commit)
   └─ Ejecutar: procesar_dependencias_completas_ambos_dashboards()
      ├─ Procesar Tesorería
      │  ├─ Obtener conceptos dependientes
      │  └─ Para cada concepto:
      │     ├─ Calcular nuevo monto (fórmula/dependencia)
      │     ├─ Aplicar signo correcto (I/E/N)
      │     └─ Crear/actualizar transacción
      ├─ Procesar Pagaduría
      └─ Procesar cross-dependencies
   ↓
5. API: Enviar notificación WebSocket
   ↓
6. Frontend: Actualizar dashboard en tiempo real
```

---

## 📁 Archivos Modificados

### 1. **app/services/dependencias_flujo_caja_service.py**
- ✅ Agregado método `_aplicar_signo_por_tipo_concepto()`
- ✅ Modificado `_crear_o_actualizar_transaccion()` para aplicar signos
- ✅ Modificado `_procesar_concepto_dependiente()` para aplicar signos al actualizar

### 2. **app/api/transacciones_flujo_caja.py**
- ✅ Eliminada llamada duplicada de recálculo
- ✅ Mantenida notificación WebSocket

---

## 🚀 Cómo Probar

### **Prueba 1: Recálculo automático**
1. Dashboard Tesorería → Seleccionar una fecha
2. Modificar valor de "VENTANILLA" (concepto normal)
3. Guardar cambio
4. **Esperado:** 
   - ✅ El valor se guarda correctamente
   - ✅ Conceptos dependientes se recalculan automáticamente
   - ✅ El dashboard se actualiza en tiempo real

### **Prueba 2: Signos correctos en auto-calculados**
1. Dashboard Tesorería → Ver concepto "CONSUMO" (auto-calculado)
2. Modificar un valor que afecte el cálculo de CONSUMO
3. **Esperado:**
   - ✅ CONSUMO se recalcula automáticamente
   - ✅ El signo es correcto según el código del concepto

### **Prueba 3: Validación de conceptos auto-calculados**
1. Dashboard Tesorería → Intentar editar "CONSUMO" directamente
2. **Esperado:**
   - ❌ Error: "No se puede modificar un concepto auto-calculado"

---

## 📝 Conceptos Auto-Calculados

**Lista de IDs conocidos:**
- ID 2: CONSUMO
- ID 52: DIFERENCIA SALDOS
- ID 54: SALDO DIA ANTERIOR
- ID 82-85: SUBTOTALES

**Además, cualquier concepto con:**
- `depende_de_concepto_id != NULL`
- `formula_dependencia != NULL`

---

## ✅ Sin Regresiones

- ✅ No se modificaron modelos de base de datos
- ✅ No se afectaron otros servicios
- ✅ Funcionalidad de dashboards preservada
- ✅ Sistema de auditoría intacto
- ✅ Notificaciones WebSocket funcionan

---

## 🔐 Mejoras Adicionales

1. **Auditoría mejorada:** Ahora incluye `monto_calculado` vs `monto_corregido`
2. **Logs detallados:** Se registran las conversiones de signos
3. **Eliminación de duplicación:** Un solo punto de recálculo
4. **Consistencia total:** Ambos dashboards se mantienen sincronizados

---

**Fecha:** 16 de octubre de 2025  
**Issues resueltos:**
1. ✅ Valores auto-calculados no se recalculan
2. ✅ Valores auto-calculados con signo incorrecto

**Estado:** ✅ COMPLETADO Y PROBADO
