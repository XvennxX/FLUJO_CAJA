# ⚙️ Utilidades del Sistema - Scripts Utils

## 🛠️ Scripts de Utilidad

### TRM (Tasa de Cambio)
- `update_trm_now.py` - **Actualización manual inmediata de TRM**

## 📋 Descripción de Utilidades

### TRM Manual
**Archivo**: `update_trm_now.py`
**Propósito**: Actualizar la TRM inmediatamente sin esperar la ejecución automática programada.

**Uso**:
```bash
python scripts/utils/update_trm_now.py
```

**Casos de uso**:
- Actualización urgente de TRM
- Testing de sistema TRM  
- Recuperación después de fallas automáticas
- Inicialización manual del sistema

## ⚠️ Precauciones
- Verificar conectividad antes de ejecutar
- No ejecutar durante picos de transacciones
- Documentar razón de actualización manual