# ⏰ CONFIGURACIÓN FINAL DEL SISTEMA TRM - PRODUCCIÓN

## 🎯 **Configuración Establecida**

### **📅 Horario de Ejecución:**
- **Tiempo**: Todos los días a las **19:00 (7:00 PM)** - Hora Colombia
- **Objetivo**: Obtener la TRM del día siguiente cuando esté disponible
- **Fallback**: Si la TRM del día siguiente no está disponible, actualiza la TRM actual

### **🔄 Lógica de Funcionamiento:**

#### **PASO 1: Intento Principal (7:00 PM)**
```
Buscar TRM para MAÑANA (día siguiente)
↓
¿Está disponible?
├─ SÍ → Guardar TRM del día siguiente ✅
└─ NO → Continuar al PASO 2
```

#### **PASO 2: Fallback Automático**
```
Buscar TRM para HOY (día actual)
↓
Actualizar/Confirmar TRM actual ✅
```

### **💾 Almacenamiento en Base de Datos:**

#### **🔍 Lógica de Guardado:**
- **Una TRM por fecha**: No se duplican registros
- **Actualización inteligente**: Si existe, actualiza valor; si no existe, crea nuevo
- **Histórico completo**: Mantiene todas las fechas con sus valores

#### **📊 Estructura de datos:**
```sql
Tabla: trm
├─ fecha (DATE) - Clave primaria
├─ valor (DECIMAL 18,6) - Valor TRM con 6 decimales
└─ fecha_creacion (TIMESTAMP) - Cuándo se creó el registro
```

## 🚀 **Cómo Usar el Sistema**

### **1. Iniciar Servicio (Recomendado para Producción)**
```bash
# Ejecutar archivo .bat (Windows)
scripts/start_trm_service.bat

# O ejecutar directamente con Python
python scripts/trm_scheduler_simple.py
```

### **2. Verificar Estado del Sistema**
```bash
# Ver TRM actual
python -c "import requests; print(requests.get('http://localhost:8000/api/v1/trm/current').json())"

# Actualización manual inmediata
scripts/update_trm_now.bat
```

### **3. Logs y Monitoreo**
- **Archivo de log**: `trm_scheduler.log`
- **Logs en consola**: Tiempo real durante ejecución
- **Formato**: Fecha/hora, nivel, mensaje detallado

## 📈 **Fuentes de Datos**

### **🇨🇴 Fuente Principal: Portal de Datos Abiertos**
- **URL**: https://www.datos.gov.co/resource/32sa-8pi3.json
- **Ventajas**: Oficial del gobierno, formato JSON estructurado
- **Actualización**: Disponible diariamente alrededor de las 6:00 PM

### **🏦 Fuente de Respaldo: Banco de la República**
- **URL**: API del Banco de la República
- **Uso**: Si falla la fuente principal
- **Confiabilidad**: Fuente oficial bancaria

## ⚡ **Escenarios de Ejecución**

### **📅 Día Normal (Lunes a Viernes)**
```
19:00 → Ejecuta automáticamente
      → Busca TRM para mañana
      → ¿Disponible? SÍ → Guarda para mañana ✅
```

### **🔄 TRM No Disponible (Fines de Semana/Festivos)**
```
19:00 → Ejecuta automáticamente
      → Busca TRM para mañana
      → ¿Disponible? NO → Fallback: Actualiza TRM actual ✅
```

### **⚠️ Error de Conexión**
```
19:00 → Ejecuta automáticamente
      → Error de red/API
      → Registra error en log
      → Reintentará mañana automáticamente
```

## 🛠️ **Configuración Avanzada**

### **🕒 Cambiar Horario de Ejecución**
Editar en `scripts/trm_scheduler_simple.py`:
```python
# Cambiar "19:00" por la hora deseada en formato 24h
schedule.every().day.at("19:00").do(job_update_trm)
```

### **🔧 Configurar como Servicio de Windows**
```bash
# Instalar NSSM (Non-Sucking Service Manager)
# Crear servicio
nssm install "TRM-Bolivar" "C:\ruta\python.exe" "C:\ruta\scripts\trm_scheduler_simple.py"
nssm set "TRM-Bolivar" AppDirectory "C:\ruta\Back-FC"
nssm start "TRM-Bolivar"
```

## 📊 **Estado Actual del Sistema**

### **✅ Verificado y Funcionando:**
- [x] Conexión a fuentes oficiales de TRM
- [x] Almacenamiento en base de datos MySQL
- [x] API REST endpoints funcionales
- [x] Integración con frontend (Dashboard Pagaduría)
- [x] Scheduler configurado para 19:00 diario
- [x] Lógica de fallback para días sin TRM nueva
- [x] Logging completo y manejo de errores

### **🎯 TRM Actual:**
- **Valor**: $4,036.42 COP
- **Fecha**: 20 de agosto de 2025
- **Última actualización**: 15:06:33 (hoy)
- **Fuente**: Portal de Datos Abiertos del Gobierno

## 📞 **Soporte y Mantenimiento**

### **🔍 Verificación Regular:**
1. **Diaria**: Comprobar que se ejecutó a las 7 PM
2. **Semanal**: Revisar logs para errores
3. **Mensual**: Verificar precisión de datos vs fuentes oficiales

### **🚨 Resolución de Problemas:**
- **Sin conexión**: Verificar internet y APIs externas
- **Error de BD**: Verificar conexión MySQL
- **TRM incorrecta**: Comparar con fuentes oficiales
- **Servicio detenido**: Reiniciar scheduler

---

## 🎉 **¡SISTEMA LISTO PARA PRODUCCIÓN!**

El sistema TRM está completamente configurado y probado para:
- ✅ **Ejecutarse automáticamente** todos los días a las 7 PM
- ✅ **Obtener la TRM del día siguiente** cuando esté disponible
- ✅ **Mantener histórico completo** en base de datos
- ✅ **Integrarse con el frontend** del dashboard
- ✅ **Manejar errores** y situaciones especiales

**Próxima ejecución**: Hoy a las 19:00 (7:00 PM) - Hora Colombia
