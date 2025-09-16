# 🐛 Scripts de Debug y Análisis

## 🔍 Herramientas de Análisis

### Análisis de Componentes
- `analizar_saldo_final.py` - **Analiza cálculos de saldo final**
- `analizar_problema_actual.py` - **Diagnóstico de problemas actuales**
- `analizar_problema_saldo.py` - **Análisis específico de saldos**
- `analizar_transacciones.py` - **Análisis detallado de transacciones**
- `analisis_pagaduria.py` - **Análisis específico de pagaduría**

### Debug de Componentes Específicos  
- `debug_saldo_inicial.py` - **Debug del saldo inicial**
- `debug_ventanilla.py` - **Debug de VENTANILLA**

### Diagnóstico de Sistemas
- `diagnostico_saldo_anterior.py` - **Diagnóstico saldo día anterior**
- `diagnostico_sync_ventanilla.py` - **Diagnóstico sync VENTANILLA**

### Verificación de Estado
- `verificar_componentes_saldo.py` - **Verificar componentes de saldo**
- `verificar_datos_dias.py` - **Verificar datos por días**
- `verificar_estado_bd.py` - **Estado general de base de datos**
- `verificar_implementacion_final.py` - **Verificar implementación final**
- `verificar_saldo_final_simple.py` - **Verificación simple saldo final**
- `verificar_saldo_inicial_cuentas.py` - **Verificar saldo inicial por cuentas**
- `verificar_saldo_neto_transacciones.py` - **Verificar saldo neto**
- `verificar_sync_simple.py` - **Verificación simple de sync**
- `verificar_api_multicuenta.py` - **Verificar API multicuenta**
- `verificar_auditoria.py` - **Verificar sistema de auditoría**
- `verificar_conceptos_2_82.py` - **Verificar conceptos 2 y 82**
- `verificar_dia_10.py` - **Verificar datos día 10**

### Visualización de Datos
- `ver_todas_transacciones.py` - **Ver todas las transacciones**
- `ver_transacciones_dia3.py` - **Ver transacciones día específico**

### Búsqueda y Consultas
- `buscar_conceptos_saldo.py` - **Buscar conceptos relacionados con saldo**

### Procesamiento Temporal
- `procesar_hoy.py` - **Procesar transacciones fecha actual**

### Confirmación de Estados
- `confirmar_saldo_neto.py` - **Confirmar cálculos saldo neto**

## 📝 Uso de Herramientas de Debug

### Análisis General del Sistema
```bash
python debug/verificar_estado_bd.py
python debug/analizar_problema_actual.py
```

### Debug de Componente Específico
```bash
python debug/debug_ventanilla.py
python debug/diagnostico_sync_ventanilla.py
```

### Verificación de Datos
```bash
python debug/ver_todas_transacciones.py
python debug/verificar_componentes_saldo.py
```

## ⚠️ Nota Importante
Estos scripts son para **análisis y debug únicamente**. No ejecutar en producción sin supervisión.