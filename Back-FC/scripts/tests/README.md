# 📁 Scripts Organizados - Tests

## 🧪 Tests Principales (Mantener)

### Tests de Funcionalidad Core
- `test_flujo_automatico_completo.py` - **Test completo del flujo automático**
- `test_validaciones_campos.py` - **Validaciones de campos y restricciones**
- `test_api_con_auth.py` - **Test de autenticación API**
- `test_auditoria.py` - **Test del sistema de auditoría**

### Tests de Cálculos Automáticos
- `test_auto_calculos_corregidos.py` - **Tests de auto-cálculos principales**
- `test_auto_recalculo_completo.py` - **Test de recálculo automático completo**
- `test_cadena_completa_pagaduria.py` - **Test completo de pagaduría**
- `test_dependencias_pagaduria.py` - **Test de dependencias pagaduría**

### Tests de Componentes Específicos
- `test_saldo_inicial_automatico.py` - **Test saldo inicial automático**
- `test_subtotal_movimiento.py` - **Test subtotal movimiento**
- `test_ventanilla_automatico.py` - **Test VENTANILLA automático**
- `test_movimiento_tesoreria.py` - **Test movimiento tesorería**

### Tests de Flujo Completo
- `test_flujo_completo_dias.py` - **Test de flujo por días**
- `test_sincronizacion_dashboards.py` - **Test sincronización entre dashboards**

### Scripts de Test
- `test_completo.bat` - **Script batch para Windows**
- `test_completo.sh` - **Script bash para Linux/Mac**

## 🗑️ Tests Eliminados (Obsoletos)

### ❌ Tests de Sincronización Duplicados
- `test_sync_*.py` - Múltiples tests duplicados de sincronización
- `test_completo_sync_*.py` - Tests de sync específicos ya integrados

### ❌ Tests de Problemas Específicos Resueltos
- `test_problema_*.py` - Tests de problemas específicos ya solucionados

### ❌ Tests de Lógica Específica Ya Implementada
- `test_logica_*.py` - Tests de lógica específica ya validada
- `test_simple_*.py` - Tests simples redundantes
- `test_mejoras_*.py` - Tests de mejoras ya implementadas

## 📝 Uso de Tests

### Ejecutar Test Individual
```bash
cd scripts/tests
python test_flujo_automatico_completo.py
```

### Ejecutar Todos los Tests
```bash
cd scripts/tests
# Windows
test_completo.bat
# Linux/Mac  
./test_completo.sh
```

### Tests Recomendados para Validación
1. `test_flujo_automatico_completo.py` - Validar flujo completo
2. `test_auto_calculos_corregidos.py` - Validar cálculos automáticos
3. `test_validaciones_campos.py` - Validar restricciones de campos