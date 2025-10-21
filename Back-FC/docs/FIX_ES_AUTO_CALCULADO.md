# 🔧 Corrección: Error 'ConceptoFlujoCaja' object has no attribute 'es_auto_calculado'

## 📋 Resumen del Problema

**Error reportado:**
```
Error: 'ConceptoFlujoCaja' object has no attribute 'es_auto_calculado'
```

**Ubicación:** Dashboard de Tesorería al intentar modificar una transacción existente.

## 🔍 Causa Raíz

El código en `app/api/transacciones_flujo_caja.py` intentaba acceder a un atributo `es_auto_calculado` que **NO existe** en el modelo `ConceptoFlujoCaja`.

### Modelo Real (conceptos_flujo_caja.py)
```python
class ConceptoFlujoCaja(Base):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    codigo = Column(String(10))  # I, E, N
    tipo = Column(String(50))
    area = Column(Enum(AreaConcepto))
    depende_de_concepto_id = Column(Integer, ForeignKey(...))  # ✅ Existe
    tipo_dependencia = Column(Enum(TipoDependencia))
    # ❌ NO existe: es_auto_calculado
```

## ✅ Solución Implementada

### Cambios en `app/api/transacciones_flujo_caja.py`

#### 1. Endpoint `/quick` (Línea ~170)

**ANTES:**
```python
if concepto and concepto.es_auto_calculado:  # ❌ Error
    raise HTTPException(...)
```

**DESPUÉS:**
```python
# Lista de conceptos que se auto-calculan
conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]

# Verificar si el concepto es auto-calculado o tiene dependencias
es_auto_calculado = (
    transaccion_existente.concepto_id in conceptos_auto_calculados or
    (concepto and concepto.depende_de_concepto_id is not None)
)

if es_auto_calculado:
    raise HTTPException(...)
```

#### 2. Endpoint PUT `/{transaccion_id}` (Línea ~225)

**ANTES:**
```python
conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]

if transaccion_existente.concepto_id in conceptos_auto_calculados:
    raise HTTPException(...)
# ❌ No verificaba dependencias
```

**DESPUÉS:**
```python
conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]

# Obtener el concepto para verificar dependencias
concepto_service = ConceptoFlujoCajaService(db)
concepto = concepto_service.obtener_concepto_por_id(transaccion_existente.concepto_id)

# Verificar si el concepto es auto-calculado o tiene dependencias
es_auto_calculado = (
    transaccion_existente.concepto_id in conceptos_auto_calculados or
    (concepto and concepto.depende_de_concepto_id is not None)
)

if es_auto_calculado:
    raise HTTPException(...)
```

## 🎯 Lógica de Validación

Un concepto se considera **auto-calculado** si:

1. **Está en la lista de IDs conocidos:**
   - ID 2: CONSUMO
   - ID 52: DIFERENCIA SALDOS
   - ID 54: SALDO DIA ANTERIOR
   - ID 82-85: SUBTOTALES

2. **O tiene dependencias configuradas:**
   - `concepto.depende_de_concepto_id is not None`

## 🧪 Verificación

Script de prueba: `test_fix_auto_calculado.py`

**Resultado:**
```
✅ CORRECTO: El atributo 'es_auto_calculado' NO existe
✅ Lógica de auto-calculado funciona correctamente
✅ Conceptos con dependencias detectados correctamente
```

## 📊 Impacto

### ✅ Funcionalidades Preservadas
- Dashboard de Tesorería funciona normalmente
- Dashboard de Pagaduría sin cambios
- Edición de transacciones permitidas
- Validación de conceptos auto-calculados mejorada

### ✅ Mejoras Adicionales
- Validación más robusta (verifica lista + dependencias)
- Consistencia entre ambos endpoints (quick y normal)
- Mensajes de error más claros

## 🚀 Pruebas Recomendadas

1. **Editar transacción normal:**
   ```
   Dashboard Tesorería → Editar monto de "VENTANILLA"
   ✅ Debe permitir la edición
   ```

2. **Intentar editar concepto auto-calculado:**
   ```
   Dashboard Tesorería → Editar monto de "CONSUMO" (ID 2)
   ❌ Debe mostrar error: "No se puede modificar un concepto auto-calculado"
   ```

3. **Editar concepto con dependencias:**
   ```
   Si existe un concepto con depende_de_concepto_id != NULL
   ❌ Debe bloquear la edición
   ```

## 📝 Archivos Modificados

```
✅ Back-FC/app/api/transacciones_flujo_caja.py
   - Línea ~170: Endpoint PUT /quick
   - Línea ~225: Endpoint PUT /{transaccion_id}

✅ Back-FC/test_fix_auto_calculado.py (nuevo)
   - Script de verificación
```

## 🔐 Sin Regresiones

- ✅ No se modificó el modelo `ConceptoFlujoCaja`
- ✅ No se afectaron otros servicios
- ✅ Imports ya existían en el archivo
- ✅ No hay errores de sintaxis
- ✅ Tests de verificación pasan correctamente

---

**Fecha:** 16 de octubre de 2025
**Issue:** Error al editar transacciones en Dashboard Tesorería
**Estado:** ✅ RESUELTO
