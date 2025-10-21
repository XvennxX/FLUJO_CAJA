# 🔧 Corrección DEFINITIVA: Aplicación de Signos Según Código de Concepto

## 📋 Entendimiento Correcto del Flujo

### **El usuario SIEMPRE ingresa valores ABSOLUTOS (sin signo):**
- Usuario ingresa: **15** (solo el número, sin + ni -)
- Usuario ingresa: **20** (solo el número, sin + ni -)

### **El BACKEND debe aplicar el signo según el código del concepto:**
- **Código "I" (INGRESO):** Guardar como POSITIVO → +15
- **Código "E" (EGRESO):** Guardar como NEGATIVO → -15
- **Código "N" (NEUTRAL):** Guardar como POSITIVO → +15

---

## ✅ Solución Implementada

### **Archivo:** `app/services/transaccion_flujo_caja_service.py`

#### **1. Nuevo método `_aplicar_signo_por_codigo_concepto()`:**

```python
def _aplicar_signo_por_codigo_concepto(self, monto_absoluto: float, concepto: ConceptoFlujoCaja) -> float:
    """
    Aplica el signo correcto al monto según el CODIGO del concepto.
    El usuario SIEMPRE ingresa valores absolutos (positivos).
    - I (INGRESO): Guarda POSITIVO (+15)
    - E (EGRESO): Guarda NEGATIVO (-15)
    - N (NEUTRAL): Guarda POSITIVO (+15) por defecto
    """
    codigo = concepto.codigo or "N"
    
    if codigo == "E":
        # EGRESO: Guardar como NEGATIVO
        return -abs(monto_absoluto)
    else:
        # INGRESO (I) o NEUTRAL (N): Guardar como POSITIVO
        return abs(monto_absoluto)
```

#### **2. Método `crear_transaccion()` actualizado:**

```python
def crear_transaccion(self, transaccion_data: TransaccionFlujoCajaCreate, usuario_id: int):
    # Obtener concepto
    concepto = self.db.query(ConceptoFlujoCaja).filter(
        ConceptoFlujoCaja.id == transaccion_data.concepto_id
    ).first()
    
    # APLICAR SIGNO según código del concepto
    monto_original = abs(float(transaccion_data.monto))  # Usuario ingresa valor absoluto
    monto_corregido = self._aplicar_signo_por_codigo_concepto(monto_original, concepto)
    
    # Guardar con signo correcto
    db_transaccion = TransaccionFlujoCaja(
        ...
        monto=monto_corregido,  # ✅ Con signo aplicado
        ...
    )
```

#### **3. Método `actualizar_transaccion()` actualizado:**

```python
def actualizar_transaccion(self, transaccion_id: int, transaccion_data: TransaccionFlujoCajaUpdate, usuario_id: int):
    update_data = transaccion_data.model_dump(exclude_unset=True)
    
    # Si se actualiza el monto, aplicar signo
    if 'monto' in update_data:
        concepto = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id == db_transaccion.concepto_id
        ).first()
        
        # Usuario ingresa valor absoluto, aplicar signo según código
        monto_original = abs(float(update_data['monto']))
        monto_corregido = self._aplicar_signo_por_codigo_concepto(monto_original, concepto)
        update_data['monto'] = monto_corregido  # ✅ Con signo aplicado
```

---

## 🎯 Ejemplos Prácticos

### **Ejemplo 1: Crear Egreso**
```
Usuario en Dashboard:
├─ Selecciona: "APERTURA ACTIVO FINANCIERO" (Código "E" - Egreso)
├─ Ingresa: 15 (valor absoluto, sin signo)
└─ Click Guardar
    ↓
Backend:
├─ Recibe: 15
├─ Identifica código: "E" (Egreso)
├─ Aplica signo: -15
└─ Guarda en BD: -15 ✅
```

### **Ejemplo 2: Crear Ingreso**
```
Usuario en Dashboard:
├─ Selecciona: "PAGOS INTERCOMPAÑÍAS" (Código "I" - Ingreso)
├─ Ingresa: 20 (valor absoluto, sin signo)
└─ Click Guardar
    ↓
Backend:
├─ Recibe: 20
├─ Identifica código: "I" (Ingreso)
├─ Aplica signo: +20
└─ Guarda en BD: +20 ✅
```

### **Ejemplo 3: Crear Neutral**
```
Usuario en Dashboard:
├─ Selecciona: "SALDO INICIAL" (Código "N" - Neutral)
├─ Ingresa: 100 (valor absoluto, sin signo)
└─ Click Guardar
    ↓
Backend:
├─ Recibe: 100
├─ Identifica código: "N" (Neutral)
├─ Aplica signo: +100
└─ Guarda en BD: +100 ✅
```

---

## 📊 Comportamiento por Código de Concepto

| Código | Tipo | Usuario Ingresa | Backend Guarda |
|--------|------|-----------------|----------------|
| **I** | Ingreso | 15 | **+15** |
| **E** | Egreso | 15 | **-15** |
| **N** | Neutral | 15 | **+15** |
| **null** | (Sin código) | 15 | **+15** (default) |

---

## 🧪 Pruebas Requeridas

### **Prueba 1: Crear Egreso**
1. Dashboard → Concepto "APERTURA ACTIVO FINANCIERO" (Egreso)
2. Ingresar: **15**
3. Guardar
4. **Verificar BD:** Debe quedar **-15** ✅

### **Prueba 2: Crear Ingreso**
1. Dashboard → Concepto "PAGOS INTERCOMPAÑÍAS" (Ingreso)
2. Ingresar: **20**
3. Guardar
4. **Verificar BD:** Debe quedar **+20** ✅

### **Prueba 3: Modificar Egreso**
1. Editar un egreso existente
2. Cambiar valor a: **30**
3. Guardar
4. **Verificar BD:** Debe quedar **-30** ✅

### **Prueba 4: Verificar SUB-TOTAL**
```
Valores ingresados:
- PAGOS INTERCOMPAÑÍAS (I): 20 → BD: +20
- COBROS INTERCOMPAÑÍAS (E): 20 → BD: -20
- APERTURA ACTIVO FINANCIERO (E): 20 → BD: -20

SUB-TOTAL TESORERÍA (auto-calculado):
Cálculo: 20 + (-20) + (-20) = -20
Resultado: -20 ✅
```

---

## ⚙️ Lógica del Método `abs()`

```python
monto_original = abs(float(transaccion_data.monto))
```

**¿Por qué `abs()`?**
- Asegura que **SIEMPRE** trabajamos con valor absoluto
- Si el usuario por error envía -15, lo convierte a 15
- Si el usuario envía 15, lo mantiene como 15
- Luego aplicamos el signo según el código del concepto

---

## 🔄 Valores Auto-Calculados

Los valores auto-calculados (SUB-TOTAL, DIFERENCIA SALDOS, etc.) **TAMBIÉN** deben aplicar el signo según su código:

**En `dependencias_flujo_caja_service.py`:**
```python
def _aplicar_signo_por_tipo_concepto(self, monto: Decimal, concepto: ConceptoFlujoCaja) -> Decimal:
    codigo = concepto.codigo or "N"
    
    if codigo == "E":
        return -abs(monto)  # Egreso: siempre negativo
    else:
        return abs(monto) if codigo == "I" else monto  # Ingreso: positivo, Neutral: mantiene
```

**Diferencia:**
- **Transacciones manuales:** Usuario ingresa absoluto, aplicamos signo
- **Transacciones auto-calculadas:** Fórmula da resultado (puede ser +/-), aplicamos signo según código

---

## 📁 Archivos Modificados

```
✅ app/services/transaccion_flujo_caja_service.py
   - Agregado _aplicar_signo_por_codigo_concepto()
   - Actualizado crear_transaccion() para aplicar signo
   - Actualizado actualizar_transaccion() para aplicar signo

✅ app/services/dependencias_flujo_caja_service.py
   - Mantiene _aplicar_signo_por_tipo_concepto() para auto-calculados
   - (Sin cambios adicionales)
```

---

## 🎉 Resultado Final

**Flujo Correcto:**
```
Usuario ingresa valor ABSOLUTO (sin signo)
    ↓
Backend identifica código del concepto
    ↓
Backend aplica signo según código:
    - "I" → Positivo
    - "E" → Negativo
    - "N" → Positivo
    ↓
Guarda en base de datos con signo correcto ✅
```

---

**Fecha:** 16 de octubre de 2025  
**Issue:** Backend debe aplicar signos según código de concepto  
**Solución:** Usuario ingresa absoluto, backend aplica signo  
**Estado:** ✅ IMPLEMENTADO CORRECTAMENTE
