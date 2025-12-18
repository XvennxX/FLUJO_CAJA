# Sistema de Versionado Histórico GMF

## 📋 Resumen

Implementación de versionado histórico para configuraciones GMF, permitiendo que cada día use la configuración correcta según su fecha.

## 🎯 Objetivo

Permitir que:
1. **Días 1-4:** Usan conceptos `[5, 9, 12]` → GMF calculado con esos conceptos
2. **Día 5:** Usuario cambia a `[5, 9]` → Aplica desde día 5 en adelante
3. **Días 6-30:** Automáticamente usan `[5, 9]` (herencia)
4. **Día 2 (retrospectivo):** Usuario entra al día 2, modifica conceptos → Solo recalcula día 2

## 🔧 Cambios Implementados

### 1. Modelo GMFConfig

**Archivo:** `Back-FC/app/models/gmf_config.py`

```python
class GMFConfig(Base):
    id = Column(Integer, primary_key=True)
    cuenta_bancaria_id = Column(Integer, ForeignKey("cuentas_bancarias.id"))
    conceptos_seleccionados = Column(Text)  # JSON: [5, 9, 12, ...]
    activo = Column(Boolean, default=True)
    fecha_vigencia_desde = Column(Date, nullable=False, index=True)  # 🆕 Desde cuándo aplica
    fecha_creacion = Column(DateTime, server_default=func.now())     # Cuándo se creó
```

**Cambio clave:** 
- `fecha_vigencia_desde`: Determina desde qué día es válida esta configuración
- `fecha_creacion`: Solo auditoría, cuándo se registró

### 2. Lógica de Búsqueda

**Archivo:** `Back-FC/app/services/dependencias_flujo_caja_service.py`

```python
def recalcular_gmf(self, fecha: date, cuenta_id: int):
    # Buscar config vigente para la fecha
    config = db.query(GMFConfig).filter(
        GMFConfig.cuenta_bancaria_id == cuenta_id,
        GMFConfig.activo == True,
        GMFConfig.fecha_vigencia_desde <= fecha  # 🔑 Clave del sistema
    ).order_by(GMFConfig.fecha_vigencia_desde.desc()).first()
```

**Lógica:**
- Busca la config más reciente cuya `fecha_vigencia_desde <= fecha_objetivo`
- Ejemplo: Si existe config para 2025-12-05, días 5-31 usan esa config

### 3. Endpoint POST /gmf-config/

**Archivo:** `Back-FC/app/api/gmf_config.py`

```python
@router.post("/")
async def crear_config_gmf(config: GMFConfigCreate):
    # Verificar si existe config para misma cuenta/fecha
    config_misma_fecha = db.query(GMFConfig).filter(
        cuenta_bancaria_id == config.cuenta_bancaria_id,
        fecha_vigencia_desde == config.fecha_vigencia_desde
    ).first()
    
    if config_misma_fecha:
        # Actualizar (corrección del mismo día)
        config_misma_fecha.conceptos_seleccionados = json.dumps(conceptos)
    else:
        # Crear NUEVA versión (no sobrescribir)
        nueva_config = GMFConfig(
            cuenta_bancaria_id=config.cuenta_bancaria_id,
            conceptos_seleccionados=json.dumps(conceptos),
            fecha_vigencia_desde=config.fecha_vigencia_desde  # 🆕
        )
        db.add(nueva_config)
```

**Comportamiento:**
- Si modificas la config del día 5: Crea nuevo registro con `fecha_vigencia_desde=2025-12-05`
- Si vuelves a modificar el día 5 el mismo día: Actualiza ese registro
- Si modificas el día 2 retrospectivamente: Crea registro con `fecha_vigencia_desde=2025-12-02`

### 4. Frontend

**Archivo:** `Front-FC/src/components/Pages/DashboardTesoreria.tsx`

```typescript
// Al guardar configuración
const guardarConfiguracionGMF = async (cuentaId: number, conceptos: number[]) => {
  await fetch('/api/v1/gmf-config/', {
    method: 'POST',
    body: JSON.stringify({
      cuenta_bancaria_id: cuentaId,
      conceptos_seleccionados: conceptos,
      fecha_vigencia_desde: selectedDate  // 🔑 Fecha del dashboard
    })
  });
};

// Al cargar configuración
const cargarConfiguracionGMF = async () => {
  // Obtener config vigente para la fecha seleccionada
  const response = await fetch(
    `/api/v1/gmf-config/${account.id}?fecha=${selectedDate}`
  );
};

// Al recalcular GMF
const guardarConceptosGMF = async (cuentaId: number) => {
  await fetch('/api/v1/gmf/recalculate', {
    body: JSON.stringify({
      fecha: selectedDate,  // Solo recalcula este día
      cuenta_bancaria_id: cuentaId
    })
  });
};
```

## 📊 Flujo Completo

### Escenario 1: Crear nueva configuración

```
Usuario en Dashboard día 5
  ↓
Abre modal GMF → Selecciona conceptos [5, 9]
  ↓
Guarda configuración
  ↓
Backend crea: GMFConfig { cuenta: 3, conceptos: [5,9], fecha_vigencia_desde: 2025-12-05 }
  ↓
Recalcula GMF solo para día 5
  ↓
Días 6-31 heredan automáticamente esta config
```

### Escenario 2: Corregir día pasado

```
Usuario en Dashboard día 2
  ↓
Abre modal GMF → Modifica conceptos a [5, 9, 12, 13]
  ↓
Guarda configuración
  ↓
Backend crea: GMFConfig { cuenta: 3, conceptos: [5,9,12,13], fecha_vigencia_desde: 2025-12-02 }
  ↓
Recalcula GMF solo para día 2
  ↓
Día 3-4 heredan esta config, día 5-31 mantienen config del día 5
```

### Escenario 3: Búsqueda de config vigente

```sql
-- Día 1: No hay config → NULL
SELECT * FROM gmf_config 
WHERE cuenta_bancaria_id = 3 
AND fecha_vigencia_desde <= '2025-12-01'
ORDER BY fecha_vigencia_desde DESC LIMIT 1;
-- Resultado: NULL

-- Día 2-4: Usa config del día 2
-- Resultado: { id: 1, fecha_vigencia_desde: '2025-12-02', conceptos: [5,9,12,13] }

-- Día 5-31: Usa config del día 5
-- Resultado: { id: 2, fecha_vigencia_desde: '2025-12-05', conceptos: [5,9] }
```

## 🗄️ Migración de Base de Datos

**Script:** `Back-FC/scripts/migration/add_fecha_vigencia_gmf_config.py`

Ejecutar:
```bash
cd Back-FC
python scripts/migration/add_fecha_vigencia_gmf_config.py
```

**Acciones:**
1. Agrega columna `fecha_vigencia_desde` (DATE NOT NULL)
2. Migra datos existentes: `fecha_vigencia_desde = DATE(fecha_creacion)`
3. Crea índice: `(cuenta_bancaria_id, fecha_vigencia_desde DESC)`

## 📝 Tabla de Versionado

```
gmf_config
┌────┬────────────────────┬─────────────────────────┬────────┬────────────────────┬─────────────────┐
│ id │ cuenta_bancaria_id │ conceptos_seleccionados │ activo │ fecha_vigencia_desde│ fecha_creacion  │
├────┼────────────────────┼─────────────────────────┼────────┼────────────────────┼─────────────────┤
│ 1  │ 3                  │ [5,9,12,13]             │ true   │ 2025-12-02         │ 2025-12-02 10:00│
│ 2  │ 3                  │ [5,9]                   │ true   │ 2025-12-05         │ 2025-12-05 14:30│
│ 3  │ 3                  │ [5,9,12]                │ true   │ 2025-12-10         │ 2025-12-10 09:15│
│ 4  │ 7                  │ [5,9,12,13,29]          │ true   │ 2025-12-01         │ 2025-12-01 08:00│
└────┴────────────────────┴─────────────────────────┴────────┴────────────────────┴─────────────────┘
```

**Interpretación:**
- Cuenta 3, días 1: Sin config → GMF no se calcula
- Cuenta 3, días 2-4: Usa config ID 1 → GMF con [5,9,12,13]
- Cuenta 3, días 5-9: Usa config ID 2 → GMF con [5,9]
- Cuenta 3, días 10-31: Usa config ID 3 → GMF con [5,9,12]
- Cuenta 7, días 1-31: Usa config ID 4 → GMF con [5,9,12,13,29]

## ✅ Validación

### Test 1: Crear config día 5
```python
# Crear config
config = GMFConfig(
    cuenta_bancaria_id=3,
    conceptos_seleccionados='[5,9]',
    fecha_vigencia_desde=date(2025, 12, 5)
)

# Verificar día 5
recalcular_gmf(fecha=date(2025, 12, 5), cuenta_id=3)
# Debe usar conceptos [5, 9]

# Verificar día 6 (herencia)
recalcular_gmf(fecha=date(2025, 12, 6), cuenta_id=3)
# Debe usar conceptos [5, 9]
```

### Test 2: Corregir día 2
```python
# Crear config retrospectiva
config = GMFConfig(
    cuenta_bancaria_id=3,
    conceptos_seleccionados='[5,9,12,13]',
    fecha_vigencia_desde=date(2025, 12, 2)
)

# Verificar día 2
recalcular_gmf(fecha=date(2025, 12, 2), cuenta_id=3)
# Debe usar conceptos [5, 9, 12, 13]

# Verificar día 5 (no afectado)
recalcular_gmf(fecha=date(2025, 12, 5), cuenta_id=3)
# Debe seguir usando conceptos [5, 9]
```

## 🚀 Beneficios

✅ **Histórico preservado:** Cada día mantiene su config correcta  
✅ **Correcciones retrospectivas:** Modificar días pasados sin afectar futuros  
✅ **Herencia automática:** Días futuros usan última config  
✅ **Auditoría completa:** Registro de cuándo y qué config se aplicó  
✅ **Performance:** Índice optimizado para búsquedas rápidas  

## 📚 Archivos Modificados

### Backend
- `app/models/gmf_config.py` - Modelo con fecha_vigencia_desde
- `app/schemas/gmf_config.py` - Schema con nueva columna
- `app/api/gmf_config.py` - Endpoints POST/GET actualizados
- `app/services/dependencias_flujo_caja_service.py` - Lógica de búsqueda
- `scripts/migration/add_fecha_vigencia_gmf_config.py` - Migración BD
- `scripts/setup/initialize_gmf_defaults.py` - Script actualizado

### Frontend
- `components/Pages/DashboardTesoreria.tsx`:
  - `cargarConfiguracionGMF()` - Pasa fecha como parámetro
  - `guardarConfiguracionGMF()` - Envía fecha_vigencia_desde
  - `guardarConceptosGMF()` - Recalcula solo fecha actual

## 📞 Soporte

Documentación creada: 9 de diciembre de 2025
Sistema implementado: GMF Versionado Histórico v1.0
