# Tests del Backend

Esta carpeta contiene los tests automatizados esenciales del backend.

## Tests Activos ✅

### Tests de Funcionalidad Core
- `test_casos_siempre_ejecutar.py` - Tests básicos que siempre deben pasar
- `test_diferencia_saldos_siempre_ejecutar.py` - Tests críticos de diferencias de saldos
- `test_diferencia_saldos.py` - Tests adicionales de validación de saldos

### Tests de Proyecciones
- `test_proyeccion_saldo.py` - Tests de lógica de proyección
- `test_proyeccion_tesoreria.py` - Tests específicos de Tesorería

### Tests de WebSocket
- `test_websocket.py` - Tests de comunicación en tiempo real

## Limpieza Realizada 🗑️
- ❌ Tests obsoletos de fechas 2024
- ❌ Tests de bugs ya resueltos
- ❌ Scripts experimentales vacíos
- ❌ Tests temporales de debug

## Ejecución

Para ejecutar todos los tests:
```bash
cd Back-FC
python -m pytest tests/
```

Para ejecutar tests específicos:
```bash
python -m pytest tests/test_archivo_especifico.py
```

## Convenciones

- Usar `pytest` como framework de testing
- Nombrar archivos como `test_*.py`
- Usar fixtures para setup común
- Documentar casos edge en tests específicos