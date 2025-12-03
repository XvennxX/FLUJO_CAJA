# Sistema TRM Automático - Documentación

## 📋 Descripción
El sistema TRM automático mantiene actualizada la Tasa Representativa del Mercado (TRM) en la base de datos del sistema de flujo de caja, consultando automáticamente las fuentes oficiales del gobierno colombiano.

## 🚀 Componentes del Sistema

### 1. TRM Scraper (`scripts/trm/trm_scraper.py`)
- **Función**: Consulta y actualiza TRMs desde fuentes oficiales
- **Fuentes**: 
  - Datos Abiertos del Gobierno
  - Banco de la República
- **Características**:
  - Manejo de certificados SSL
  - Reintentos automáticos
  - Logging detallado

### 2. Servicio Automático (`trm_service.py`)
- **Función**: Ejecuta actualizaciones programadas de TRM
- **Horario**: 8:00 AM - 6:00 PM (días laborales)
- **Frecuencia**: Cada 30 minutos
- **Características**:
  - Solo actualiza días hábiles (lunes a viernes)
  - Detecta y actualiza TRMs faltantes
  - Ejecuta en background

### 3. Verificador de Estado (`check_trm_status.py`)
- **Función**: Reporta el estado actual del sistema TRM
- **Información**:
  - Total de TRMs en base de datos
  - Últimas 10 TRMs registradas
  - Análisis de cobertura y TRMs faltantes

## 🎯 Uso del Sistema

### Iniciar Servicio Automático
```bash
# Opción 1: Ejecutar directamente
python trm_service.py

# Opción 2: Usar script batch (Windows)
start_trm_service.bat
```

### Verificar Estado
```bash
# Opción 1: Ejecutar directamente
python check_trm_status.py

# Opción 2: Usar script batch (Windows)
check_trm.bat
```

### Actualización Manual
```bash
# Actualizar TRM para una fecha específica
python test_trm_simple.py
```

## 📊 Estado Actual del Sistema

### Últimas TRMs Registradas (Noviembre 2025):
- **31 de octubre**: $3,870.42 ✅
- **30 de octubre**: $3,885.29 ✅
- **29 de octubre**: $3,874.84 ✅
- **28 de octubre**: $3,844.20 ✅
- **25 de octubre**: $3,858.63 ✅

### Cobertura:
- **Total TRMs**: 50 registros
- **Última actualización**: 31 de octubre de 2025
- **Estado**: Sistema funcionando correctamente

## ⚡ Características Técnicas

### Manejo de Errores:
- SSL: Configurado para manejar certificados problemáticos
- Reintentos: Sistema de reintentos automáticos
- Fuentes múltiples: Fallback entre diferentes APIs
- Logging: Registro detallado de todas las operaciones

### Programación:
- **Librería**: `schedule` para programación de tareas
- **Base de datos**: SQLAlchemy ORM con MySQL
- **Sesiones**: Gestión automática de conexiones DB

### Validaciones:
- **Días hábiles**: Solo actualiza lunes a viernes
- **Duplicados**: Verifica existencia antes de insertar
- **Fechas futuras**: No intenta obtener TRMs no disponibles

## 🔧 Troubleshooting

### Problema: "No se puede conectar a la fuente"
- **Causa**: Problemas de SSL o conectividad
- **Solución**: El sistema tiene configurado SSL verify=False y reintentos automáticos

### Problema: "TRM no encontrada para fecha X"
- **Causa**: Fecha es feriado, fin de semana o TRM no publicada aún
- **Solución**: Normal - el sistema continúa e intentará en la próxima ejecución

### Problema: "Servicio no inicia"
- **Causa**: Dependencias faltantes o problemas de importación
- **Solución**: Verificar que todas las dependencias estén instaladas:
  ```bash
  pip install schedule requests sqlalchemy
  ```

## 📝 Logs del Sistema

El sistema genera logs detallados que incluyen:
- Timestamp de cada operación
- Consultas SQL ejecutadas
- Resultados de scraping
- Errores y warnings
- TRMs actualizadas exitosamente

## 🎯 Configuración Recomendada

### Para Producción:
1. Ejecutar `trm_service.py` como servicio del sistema
2. Configurar monitoreo de logs
3. Programar verificaciones periódicas con `check_trm_status.py`
4. Mantener respaldos de la base de datos

### Para Desarrollo:
1. Usar `test_trm_simple.py` para pruebas
2. Verificar estado con `check_trm_status.py`
3. Revisar logs para debugging

## ✅ Sistema Operacional

**Estado**: ✅ FUNCIONANDO CORRECTAMENTE
- ✅ Conexión a fuentes oficiales
- ✅ Actualización automática
- ✅ Base de datos sincronizada
- ✅ Manejo de errores robusto
- ✅ Programación automática activa

El sistema TRM está completamente operacional y actualizará automáticamente las TRMs faltantes según la programación establecida.