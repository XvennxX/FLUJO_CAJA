# 🔧 Scripts de Mantenimiento

## 🛠️ Herramientas de Reparación y Mantenimiento

### Corrección de Saldos
- `arreglar_saldo_final.py` - **Corregir saldo final cuentas**
- `fix_saldo_final_176.py` - **Fix específico saldo final $176**
- `recalcular_saldo_final.py` - **Recalcular saldo final usando fórmula**

### Limpieza de Datos
- `limpiar_registros_nulos.py` - **Eliminar registros nulos o inválidos**
- `limpiar_saldo_dia_anterior.py` - **Limpiar datos saldo día anterior**

### Actualización de Sistemas
- `actualizar_auditoria_vacia.py` - **Actualizar registros auditoría vacíos**

## 📋 Procedimientos de Mantenimiento

### Corrección de Saldos
1. **Verificar problema**:
   ```bash
   python ../debug/verificar_estado_bd.py
   ```

2. **Ejecutar corrección**:
   ```bash
   python maintenance/recalcular_saldo_final.py
   ```

3. **Validar resultado**:
   ```bash
   python ../debug/verificar_saldo_final_simple.py
   ```

### Limpieza Rutinaria
1. **Limpiar registros nulos**:
   ```bash
   python maintenance/limpiar_registros_nulos.py
   ```

2. **Actualizar auditoría**:
   ```bash
   python maintenance/actualizar_auditoria_vacia.py
   ```

### Corrección de Problemas Específicos
- Para saldo final incorrecto: `fix_saldo_final_176.py`
- Para inconsistencias día anterior: `limpiar_saldo_dia_anterior.py`
- Para recálculo completo: `recalcular_saldo_final.py`

## ⚠️ Precauciones

### Antes de Ejecutar
1. **Backup de base de datos**
2. **Verificar en entorno de pruebas**
3. **Revisar logs de ejecución**

### Durante Ejecución
1. **Monitor de recursos del sistema**
2. **Validación de transacciones activas**
3. **Confirmación de cambios**

### Después de Ejecutar
1. **Validar integridad de datos**
2. **Verificar cálculos automáticos**
3. **Confirmar funcionamiento normal**

## 📞 Soporte
Para problemas con scripts de mantenimiento, consultar documentación técnica en `/docs/` o logs del sistema.