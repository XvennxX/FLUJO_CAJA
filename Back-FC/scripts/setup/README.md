# Scripts de Configuración Inicial

Este directorio contiene scripts para la configuración inicial del sistema.

## Archivos:

### 📊 **Datos iniciales:**
- `create_initial_data.py` - Crear datos iniciales para el sistema
- `create_test_banks.py` - Crear bancos de prueba para testing

### 🔐 **Seguridad:**
- `generate_bcrypt.py` - Generar hashes bcrypt para contraseñas

### 🏢 **Compañías:**
- `create_companies.py` - Script para crear compañías iniciales

## Uso:

```bash
# Crear datos iniciales
python setup/create_initial_data.py

# Crear bancos de prueba
python setup/create_test_banks.py

# Generar hash para contraseña
python setup/generate_bcrypt.py
```

**Nota:** Estos scripts generalmente se ejecutan una sola vez durante la configuración inicial del sistema.
