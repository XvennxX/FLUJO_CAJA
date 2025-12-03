# Cargue Automático de Saldos desde Excel

## Descripción General
Sistema para importar saldos iniciales desde archivos Excel con múltiples hojas (una por día del mes).

## Características

### 📥 Importación Automática
- **Dos modos de carga:**
  - **Mes Completo**: Procesa todos los días del mes hasta el día actual
  - **Día Específico**: Procesa solo un día seleccionado

### 📊 Formato del Excel
- **Nombre del archivo**: `SEPTIEMBRE2025.xlsx` (formato: MES-AÑO)
- **Estructura**: Una hoja por día (nombres: "1", "2", "3"... "31")
- **Fila clave**: "SALDO INICIAL" (para ambos archivos)
- **Detección automática**:
  - Números de cuenta (6+ dígitos)
  - Moneda (COP/USD)
  - Conversión automática USD → COP usando TRM del día

### 🔄 Procesamiento
1. **Tesorería**: Lee "SALDO INICIAL" → Crea transacciones con `concepto_id` de "SALDO INICIAL" en área tesorería
2. **Pagaduría**: Lee "SALDO DIA ANTERIOR" → Crea transacciones con `concepto_id` de "SALDO DIA ANTERIOR" en área pagaduría
3. **Conversión USD**: Si columna es USD, aplica: `(valorUSD × TRM) / 1000`

## Flujo de Uso

### Frontend (`CargueInicial.tsx`)
1. Click en botón "Importar desde Excel" (verde)
2. Seleccionar tipo de carga (Mes/Día)
3. Seleccionar mes a importar
4. Si es día específico, seleccionar fecha
5. Subir archivo Tesorería
6. Subir archivo Pagaduría
7. Marcar "Sobrescribir" si se desea reemplazar datos existentes
8. Click "Importar"

### Backend (`importador_saldos_service.py`)
**Endpoint**: `POST /api/v1/saldo-inicial/importar-saldos`

**Parámetros (FormData)**:
- `tipo_carga`: "mes" | "dia"
- `mes`: "YYYY-MM"
- `dia`: "YYYY-MM-DD" (opcional, requerido si tipo_carga="dia")
- `sobrescribir`: boolean
- `archivo_tesoreria`: File (Excel)
- `archivo_pagaduria`: File (Excel)

**Respuesta**:
```json
{
  "success": true,
  "tipo_carga": "mes",
  "mes": "2025-09",
  "dias_procesados": 25,
  "cuentas_tesoreria": 150,
  "cuentas_pagaduria": 150,
  "cuentas_sin_match": ["123456", "789012"],
  "dias_sin_trm": ["2025-09-01", "2025-09-02"],
  "errores": []
}
```

## Validaciones

### ✅ Requisitos
- Solo usuarios `administrador` pueden acceder
- TRM debe existir para cada día a procesar
- Números de cuenta deben existir en BD
- Archivos deben tener formato válido

### ⚠️ Advertencias
- **Días sin TRM**: Se saltan automáticamente
- **Cuentas no encontradas**: Se reportan pero no detienen el proceso
- **Sobrescribir**: Si está activo, reemplaza transacciones existentes

## Arquitectura Técnica

### Servicio Principal: `ImportadorSaldosService`
```python
def importar(
    db: Session,
    tipo_carga: str,      # 'mes' o 'dia'
    mes: str,             # 'YYYY-MM'
    dia: Optional[str],   # 'YYYY-MM-DD'
    sobrescribir: bool,
    archivo_tesoreria: bytes,
    archivo_pagaduria: bytes,
    usuario_id: int = 1
) -> Dict
```

### Métodos Auxiliares
1. **`_parse_excel_multi_sheet`**: Parsea todas las hojas del Excel
2. **`_parse_single_sheet`**: Procesa una hoja individual
   - Busca fila "SALDO INICIAL" o "SALDO DIA ANTERIOR"
   - Extrae números de cuenta del encabezado
   - Detecta moneda (COP/USD)
   - Lee valores de la fila objetivo
3. **`_obtener_trm`**: Obtiene TRM para una fecha

### Flujo de Procesamiento
```
1. Validar parámetros (mes, día, tipo_carga)
2. Determinar días a procesar
3. Parsear ambos Excels → Dict[fecha, (valores, monedas)]
4. Para cada día:
   a. Obtener TRM del día
   b. Procesar Tesorería:
      - Buscar cuenta en BD
      - Convertir USD si aplica
      - Crear/actualizar transacción área=tesoreria
   c. Procesar Pagaduría:
      - Buscar cuenta en BD
      - Convertir USD si aplica
      - Crear/actualizar transacción área=pagaduria
5. Commit y retornar resultado
```

## Ejemplo de Uso

### Caso 1: Importar Mes Completo
```bash
# Archivos necesarios:
- SEPTIEMBRE2025.xlsx (Tesorería)
- CUADROFLUJOSEPTIEMBRE2025.xlsx (Pagaduría)

# Resultado:
✓ Procesados 30 días
✓ 600 transacciones tesorería
✓ 600 transacciones pagaduría
⚠ Días sin TRM: 2025-09-01, 2025-09-02
```

### Caso 2: Importar Día Específico
```bash
# Archivos: mismos
# Selección: Día 2025-09-15

# Resultado:
✓ Procesado 1 día
✓ 20 transacciones tesorería
✓ 20 transacciones pagaduría
```

## Errores Comunes

### 🔴 "No se encontró 'SALDO INICIAL' en esta hoja"
**Causa**: Fila no existe o tiene formato diferente  
**Solución**: Verificar que la hoja tenga exactamente el texto "SALDO INICIAL" en mayúsculas

### 🔴 "No se encontró fila con números de cuenta"
**Causa**: Números de cuenta no están en formato correcto (deben ser 6+ dígitos)  
**Solución**: Asegurar que encabezado tenga números de cuenta válidos

### 🔴 "Días sin TRM"
**Causa**: TRM no existe en BD para esas fechas  
**Solución**: Ejecutar script `scripts/trm/poblar_trm_sept_nov.py`

### 🔴 "Cuentas no encontradas"
**Causa**: Números de cuenta en Excel no existen en tabla `cuentas_bancarias`  
**Solución**: Verificar/crear cuentas faltantes en BD

## Notas de Implementación

### Detección de USD
El sistema busca en filas superiores al encabezado de cuentas palabras clave:
- "USD"
- "DOLAR" / "DÓLAR"
- "US$"

### Fórmula de Conversión
```python
if es_usd:
    monto_cop = (valor_usd * trm_valor) / 1000
else:
    monto_cop = valor_cop
```

### Manejo de Errores
- Errores por hoja no detienen el proceso completo
- Se reportan en `resultado.errores[]`
- Días sin TRM se saltan y reportan en `resultado.dias_sin_trm[]`

## Próximas Mejoras Sugeridas
- [ ] Validación previa del Excel antes de importar
- [ ] Preview de datos a importar
- [ ] Importación en background para archivos grandes
- [ ] Exportar template Excel con formato correcto
- [ ] Log detallado por transacción creada
