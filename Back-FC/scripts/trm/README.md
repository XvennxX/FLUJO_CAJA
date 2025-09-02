# Scripts de TRM (Tasa Representativa del Mercado)

Este directorio contiene todos los scripts relacionados con la obtención, procesamiento y automatización de la TRM.

## ⚠️ **IMPORTANTE: Problema de Backend Apagado**

**Si el backend está apagado a las 7 PM, NO se actualiza la TRM automáticamente.**

### ✅ **Solución implementada:**
- **Verificación automática**: Al iniciar el backend, revisa TRMs faltantes de los últimos 7 días
- **Actualización manual**: Scripts para recuperar TRMs perdidas
- **Recuperación automática**: Ya no necesitas recordar actualizar manualmente

## Archivos principales:

### 🤖 **Automatización:**
- `trm_scheduler_simple.py` - **Scheduler principal con verificación automática al inicio**
- `trm_scheduler.py` - Scheduler original (desarrollo)

### 📊 **Obtención de datos:**
- `trm_scraper.py` - Script principal que obtiene TRM desde fuentes oficiales

### 🔧 **Utilidades:**
- `update_missing_trm.py` - **NUEVO: Actualiza TRMs faltantes (manual)**
- `migrate_trm.py` - Crear tabla TRM en la base de datos
- `monitor_trm.py` - Monitor en tiempo real para verificar actualizaciones
- `test_trm.py` - Pruebas completas del sistema TRM

### 🖥️ **Ejecución (Windows):**
- `start_trm_service.bat` - Iniciar servicio automático de TRM
- `update_trm_now.bat` - **MEJORADO: Verifica y actualiza TRMs faltantes**

## Uso:

### 🚀 **Uso normal:**
```bash
# Iniciar servicio automático (revisa TRMs faltantes al inicio)
start_trm_service.bat
```

### 🛠️ **Recuperar TRMs perdidas:**
```bash
# Verificar y actualizar TRMs faltantes (últimos 7 días)
update_trm_now.bat

# O manualmente:
python scripts\trm\update_missing_trm.py

# Para fecha específica:
python scripts\trm\update_missing_trm.py 2025-08-20
```

### 📊 **Otros comandos:**
```bash
# Crear tabla TRM
python migrate_trm.py

# Monitorear actualizaciones
python monitor_trm.py
```

## 🔄 **Flujo mejorado:**

1. **Al iniciar el backend**: Automáticamente verifica TRMs faltantes
2. **A las 7 PM diario**: Actualiza TRM del día siguiente
3. **Si falta alguna**: Ejecuta `update_trm_now.bat` para recuperar

## 📋 **Comportamiento actual:**

- ✅ **Backend encendido a las 7 PM**: TRM se actualiza automáticamente
- ❌ **Backend apagado a las 7 PM**: TRM se pierde
- ✅ **Al encender backend**: Verifica y recupera TRMs automáticamente
- ✅ **Actualización manual**: `update_trm_now.bat` cuando sea necesario
