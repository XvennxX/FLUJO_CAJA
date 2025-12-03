# Scripts de TRM (Tasa Representativa del Mercado)

Este directorio contiene todos los scripts relacionados con la obtención, procesamiento y automatización de la TRM.

## 🎯 Sistema de TRM Automática - Configuración 7:00 PM

### ✅ **Solución Completa Implementada:**

1. **Actualización Diaria Automática a las 7:00 PM (19:00)**
   - Scheduler que se ejecuta todos los días a las 7:00 PM
   - Obtiene la TRM del día automáticamente
   - Registra en base de datos PostgreSQL

2. **Recuperación Automática de TRMs Faltantes**
   - Al iniciar el servidor, revisa últimos 30 días
   - Detecta y recupera TRMs que faltaron cuando el servidor estaba apagado
   - No requiere intervención manual

3. **Monitoreo y Verificación**
   - Verificación de conexión cada hora
   - Logs detallados en `logs/trm_scheduler.log`
   - Resumen de operaciones al iniciar servidor

## 📁 Archivos principales:

### 🤖 **Automatización (USAR ESTOS):**
- `trm_scheduler_production.py` ⭐ **PRINCIPAL - Ejecuta a las 7:00 PM**
- `start_trm_scheduler.ps1` - Script de PowerShell para iniciar el scheduler
- `update_missing_trm.py` - Script manual para recuperar TRMs faltantes

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
