# 🔧 INSTRUCCIONES DE USO - SISTEMA TRM AUTOMÁTICO

## ✅ Sistema Configurado Para:
- **Ejecutar diariamente a las 7:00 PM (19:00)**
- **Recuperar automáticamente TRMs faltantes al iniciar el servidor**

---

## 🚀 INICIO RÁPIDO

### **Opción 1: Iniciar Servidor (RECOMENDADO para desarrollo)**

```powershell
cd Back-FC
python run_server.py
```

**¿Qué hace?**
- ✅ Inicia el servidor FastAPI
- ✅ Al arrancar, revisa últimos 30 días
- ✅ Recupera automáticamente TRMs faltantes
- ✅ Muestra resumen de TRMs recuperadas

---

### **Opción 2: Iniciar Scheduler Independiente (PRODUCCIÓN)**

```powershell
cd Back-FC\scripts\trm
.\start_trm_scheduler.ps1
```

**Menú interactivo con opciones:**
1. ⭐ Iniciar en segundo plano
2. Ver logs en tiempo real
3. Ver historial de logs
4. Detener scheduler
5. Recuperación manual
6. Salir

**IMPORTANTE:** El scheduler debe estar ejecutándose para que funcione la actualización automática a las 7:00 PM

---

## 📋 FLUJO COMPLETO DEL SISTEMA

### 1️⃣ **Al Iniciar el Servidor** (`run_server.py`)

```
INICIO DEL SERVIDOR
    ↓
Verificación automática (últimos 30 días)
    ↓
Busca fechas sin TRM
    ↓
Recupera TRMs faltantes
    ↓
Muestra resumen en consola
    ↓
Servidor listo para usar
```

**Ejemplo de salida:**
```
======================================================================
🔍 VERIFICANDO TRMs FALTANTES AL INICIAR SERVIDOR
======================================================================
📅 Revisando últimos 30 días para TRMs faltantes...

📊 RESUMEN DE RECUPERACIÓN DE TRMs:
   ✅ Fechas faltantes encontradas: 3
   ✅ TRMs actualizadas exitosamente: 3
   ❌ Actualizaciones fallidas: 0
   🎉 Se recuperaron 3 TRMs faltantes

======================================================================
✅ VERIFICACIÓN DE TRMs COMPLETADA
======================================================================
```

---

### 2️⃣ **Ejecución Diaria Automática** (7:00 PM)

```
SCHEDULER EJECUTA A LAS 19:00
    ↓
Obtiene TRM del día actual
    ↓
Guarda en base de datos
    ↓
Verifica fechas faltantes
    ↓
Recupera TRMs que faltaban
    ↓
Registra en logs
```

**Archivo de logs:** `Back-FC/logs/trm_scheduler.log`

**Ejemplo de log:**
```
2025-11-06 19:00:00 - INFO - 🌙 ACTUALIZACIÓN TRM DIARIA - 7:00 PM
2025-11-06 19:00:05 - INFO - 📅 Obteniendo TRM para 2025-11-06
2025-11-06 19:00:08 - INFO - ✅ TRM DIARIA EXITOSA para 2025-11-06
2025-11-06 19:00:10 - INFO - 🔄 Verificando fechas faltantes...
2025-11-06 19:00:15 - INFO - 📊 Resumen TRM: 0 faltantes, 0 actualizadas
```

---

## 🛠️ OPERACIONES MANUALES

### Recuperar TRMs de los últimos N días

```powershell
cd Back-FC
python scripts\trm\update_missing_trm.py 30
```

Parámetro: número de días hacia atrás (ejemplo: 30 días)

---

### Ver logs del scheduler

```powershell
# Ver últimas 20 líneas
Get-Content logs\trm_scheduler.log -Tail 20

# Ver logs en tiempo real
Get-Content logs\trm_scheduler.log -Wait -Tail 20
```

---

### Probar el sistema

```powershell
cd Back-FC
python scripts\trm\test_trm_system.py
```

Verifica:
- ✅ Importación de módulos
- ✅ Conexión al scraper
- ✅ Base de datos
- ✅ Configuración del scheduler

---

## 🔍 VERIFICACIÓN DEL SISTEMA

### ¿Cómo sé si está funcionando?

1. **Ver logs del scheduler:**
   ```powershell
   Get-Content logs\trm_scheduler.log -Tail 20
   ```

2. **Verificar en base de datos:**
   - Consultar tabla `trm`
   - Debe tener registros diarios

3. **API Endpoint:**
   ```
   GET http://localhost:8000/api/v1/trm/current
   ```

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### **Problema:** TRMs no se actualizan a las 7:00 PM

**Causa:** Scheduler no está ejecutándose

**Solución:**
```powershell
cd Back-FC\scripts\trm
.\start_trm_scheduler.ps1
# Seleccionar opción 1 (Iniciar en segundo plano)
```

---

### **Problema:** Error al iniciar servidor

**Causa:** Falta instalar dependencias

**Solución:**
```powershell
cd Back-FC
pip install -r requirements.txt
pip install schedule
```

---

### **Problema:** No se recuperan TRMs faltantes

**Causa:** Error de conexión o fechas son fines de semana

**Solución Manual:**
```powershell
python scripts\trm\update_missing_trm.py 30
```

Ver logs para detalles del error

---

## 📊 CONFIGURACIÓN AVANZADA

### Cambiar horario de ejecución

Editar: `scripts/trm/trm_scheduler_production.py`

```python
# Línea 146 - Cambiar horario (formato 24h)
schedule.every().day.at("19:00").do(job_trm_diaria)  # 7:00 PM

# Ejemplos:
# "07:00" = 7:00 AM
# "12:00" = 12:00 PM (mediodía)
# "15:30" = 3:30 PM
# "23:00" = 11:00 PM
```

---

### Ajustar días de recuperación al iniciar

Editar: `run_server.py`

```python
# Línea 29 - Cambiar días hacia atrás
resultado = trm_service.verificar_trms_faltantes(days_back=30)

# Valores sugeridos:
# 7 = última semana
# 30 = último mes
# 60 = últimos 2 meses
```

---

## 📁 ARCHIVOS DEL SISTEMA

```
Back-FC/
├── run_server.py                              # ⭐ Servidor con verificación automática
├── scripts/
│   └── trm/
│       ├── trm_scheduler_production.py       # ⭐ Scheduler principal (7:00 PM)
│       ├── start_trm_scheduler.ps1           # Script de inicio fácil
│       ├── trm_scraper.py                    # Obtiene TRM del Banco República
│       ├── update_missing_trm.py             # Recuperación manual
│       ├── test_trm_system.py                # Test del sistema
│       └── README.md                         # Documentación detallada
├── app/
│   └── services/
│       └── trm_service.py                    # Servicio de gestión TRM
└── logs/
    └── trm_scheduler.log                     # ⭐ Logs del scheduler
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

Para producción, verificar:

- [ ] Scheduler ejecutándose en segundo plano
- [ ] Logs generándose correctamente
- [ ] Servidor configurado para auto-start
- [ ] TRMs actualizándose a las 7:00 PM
- [ ] Recuperación automática funcionando
- [ ] Backup de tabla `trm` configurado

---

## 📞 COMANDOS ÚTILES

```powershell
# Iniciar servidor con verificación
python run_server.py

# Iniciar scheduler
cd scripts\trm; .\start_trm_scheduler.ps1

# Recuperación manual (30 días)
python scripts\trm\update_missing_trm.py 30

# Ver logs en tiempo real
Get-Content logs\trm_scheduler.log -Wait -Tail 20

# Test del sistema
python scripts\trm\test_trm_system.py

# Ver procesos Python ejecutándose
Get-Process python*
```

---

## 🎯 RESULTADO ESPERADO

### **Operación Normal:**

1. **Servidor arranca:**
   - Verifica últimos 30 días
   - Recupera 0-N TRMs faltantes
   - Muestra resumen en consola
   - Queda listo para usar

2. **Todos los días a las 7:00 PM:**
   - Scheduler obtiene TRM del día
   - Guarda en base de datos
   - Verifica y recupera fechas faltantes
   - Registra en logs

3. **Consultas API funcionan:**
   - GET /api/v1/trm/current ✅
   - GET /api/v1/trm/{fecha} ✅
   - Sin fechas faltantes ✅

---

**Última actualización:** 6 de Noviembre de 2025  
**Versión:** 2.0 - Producción  
**Horario configurado:** 7:00 PM (19:00) diariamente  
**Recuperación automática:** Últimos 30 días al iniciar servidor
