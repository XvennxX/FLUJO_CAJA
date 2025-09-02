# Migraciones de Base de Datos

Este directorio contiene archivos SQL para migraciones y cambios en la estructura de la base de datos.

## Archivos:

### 🏦 **Cuentas bancarias:**
- `add_tipo_cuenta_column.sql` - Agregar columna tipo_cuenta a las cuentas bancarias
- `restructure_cuenta_moneda.sql` - Reestructurar tabla intermedia cuenta_moneda

## Uso:

```sql
-- Ejecutar migraciones directamente en MySQL
mysql -u usuario -p nombre_bd < migrations/archivo.sql
```

**Importante:** 
- Hacer backup antes de ejecutar migraciones
- Ejecutar en orden cronológico
- Verificar cambios en ambiente de desarrollo primero
