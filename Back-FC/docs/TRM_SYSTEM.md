# Sistema de TRM Automático - Bolivar

## Descripción

Este sistema obtiene automáticamente la Tasa Representativa del Mercado (TRM) desde la Superintendencia Financiera de Colombia y la integra en el dashboard de Pagaduría.

## Características

- ✅ **Actualización automática**: Se ejecuta diariamente a las 18:00 (6 PM)
- ✅ **Múltiples fuentes**: Portal de datos abiertos del gobierno y Banco de la República
- ✅ **Base de datos**: Almacenamiento histórico de TRM
- ✅ **API REST**: Endpoints para consultar TRM
- ✅ **Integración frontend**: Visualización en dashboard de Pagaduría
- ✅ **Manejo de errores**: Fallbacks y logging completo

## Estructura de Archivos

```
Back-FC/
├── app/
│   ├── models/
│   │   └── trm.py              # Modelo de datos TRM
│   └── api/
│       └── trm.py              # Endpoints API TRM
├── scripts/
│   ├── trm_scraper.py          # Script principal de scraping
│   ├── trm_scheduler.py        # Servicio automatizado
│   ├── test_trm.py             # Script de pruebas
│   ├── migrate_trm.py          # Migración de base de datos
│   ├── start_trm_service.bat   # Iniciar servicio (Windows)
│   └── update_trm_now.bat      # Actualización manual (Windows)
```

## Base de Datos

### Tabla: `trm`

```sql
CREATE TABLE trm (
    fecha DATE PRIMARY KEY,
    valor DECIMAL(18,6) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Campos

- **fecha**: Fecha de la TRM (clave primaria)
- **valor**: Valor de la TRM con 6 decimales de precisión
- **fecha_creacion**: Timestamp de creación del registro

## API Endpoints

### `GET /api/v1/trm/current`
Obtiene la TRM más reciente.

**Respuesta:**
```json
{
  "fecha": "2025-08-20",
  "valor": "4036.420000",
  "fecha_creacion": "2025-08-20T15:06:33"
}
```

### `GET /api/v1/trm/by-date/{fecha}`
Obtiene la TRM para una fecha específica.

**Parámetros:**
- `fecha`: Fecha en formato YYYY-MM-DD

### `GET /api/v1/trm/range`
Obtiene un rango de TRMs.

**Parámetros de consulta:**
- `fecha_inicio`: Fecha de inicio (opcional)
- `fecha_fin`: Fecha de fin (opcional)
- `limit`: Número máximo de resultados (default: 30)

### `POST /api/v1/trm/`
Crea o actualiza una TRM.

**Body:**
```json
{
  "fecha": "2025-08-20",
  "valor": 4036.42
}
```

## Fuentes de Datos

### 1. Portal de Datos Abiertos del Gobierno
- **URL**: https://www.datos.gov.co/resource/32sa-8pi3.json
- **Ventajas**: API estructurada, confiable
- **Formato**: JSON directo

### 2. Banco de la República
- **URL**: https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario
- **Ventajas**: Fuente oficial
- **Uso**: Fallback si falla la primera fuente

## Automatización

### Servicio Diario
El scheduler se ejecuta continuamente y programa la actualización para las 18:00 diarias:

```python
schedule.every().day.at("18:00").do(job_update_trm)
```

### Logging
Todos los procesos generan logs detallados:
- `trm_scraper.log`: Logs del scraping
- `trm_scheduler.log`: Logs del servicio automatizado

## Uso

### 1. Instalación
```bash
# Instalar dependencias
pip install requests schedule beautifulsoup4 lxml

# Crear tabla TRM
python scripts/migrate_trm.py
```

### 2. Pruebas
```bash
# Ejecutar pruebas completas
python scripts/test_trm.py
```

### 3. Actualización Manual
```bash
# Windows
scripts/update_trm_now.bat

# Linux/Mac
python scripts/trm_scraper.py
```

### 4. Servicio Automático
```bash
# Windows
scripts/start_trm_service.bat

# Linux/Mac
python scripts/trm_scheduler.py
```

## Integración Frontend

### Hook React
```typescript
import { useTRM } from '../../hooks/useTRM';

const { trm, loading, error } = useTRM();
```

### Visualización
- **Header del dashboard**: Indicador de TRM actual con fecha
- **Fila TRM**: Valor en cada columna de cuenta bancaria
- **Formato**: Moneda colombiana con separadores de miles

## Configuración de Producción

### 1. Como Servicio Windows
```bash
# Crear servicio Windows con NSSM
nssm install TRM-Service "C:\ruta\a\python.exe" "C:\ruta\a\scripts\trm_scheduler.py"
nssm set TRM-Service AppDirectory "C:\ruta\a\Back-FC"
nssm start TRM-Service
```

### 2. Como Cron Job (Linux)
```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar a las 18:00 diarios
0 18 * * * /usr/bin/python3 /ruta/a/scripts/trm_scraper.py
```

### 3. Variables de Entorno
```env
# .env
TRM_UPDATE_TIME=18:00
TRM_FALLBACK_VALUE=4000.00
TRM_RETRY_ATTEMPTS=3
```

## Monitoreo

### 1. Estado del Servicio
- Verificar logs en `trm_scheduler.log`
- Endpoint de salud: `GET /api/v1/trm/current`

### 2. Alertas
- Error de conexión a fuentes externas
- Falla en actualización diaria
- Valores de TRM fuera de rango esperado

## Solución de Problemas

### Problema: No se actualiza la TRM
**Solución:**
1. Verificar conexión a internet
2. Revisar logs de errores
3. Ejecutar actualización manual
4. Verificar estado de APIs externas

### Problema: Error en base de datos
**Solución:**
1. Verificar conexión a MySQL
2. Ejecutar migración nuevamente
3. Revisar permisos de base de datos

### Problema: TRM no aparece en frontend
**Solución:**
1. Verificar que el backend esté ejecutándose
2. Revisar consola del navegador para errores
3. Verificar endpoint `/api/v1/trm/current`

## Contacto y Soporte

Para soporte técnico o mejoras del sistema TRM, contactar al equipo de desarrollo.

## Versión

- **Versión actual**: 1.0.0
- **Última actualización**: 20 de agosto de 2025
- **Próximas mejoras**: 
  - Dashboard de históricos de TRM
  - Alertas por cambios significativos
  - Exportación de datos históricos
