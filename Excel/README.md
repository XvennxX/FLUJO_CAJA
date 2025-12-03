# Carpeta Excel - Archivos de Cargue

Esta carpeta contiene archivos Excel utilizados para el cargue masivo de datos al sistema de flujo de caja.

## 📋 Propósito

- **Plantillas**: Archivos Excel con el formato requerido para cargue de datos
- **Archivos históricos**: Datos de meses anteriores para referencia
- **Backups**: Copias de seguridad de cargues importantes

## 📁 Contenido

- `SEPTIEMBRE 2025 (1).xlsx` - Datos de flujo de caja de septiembre 2025

## ⚠️ Notas Importantes

- Los archivos Excel **NO deben ser versionados** en Git (ver `.gitignore`)
- Solo se incluyen en la carpeta local para facilitar el cargue
- Mantener respaldos de archivos importantes en otro sistema de almacenamiento

## 🔧 Uso

1. Colocar archivo Excel en esta carpeta
2. Usar la funcionalidad de "Cargue Inicial" en el sistema
3. Seleccionar el archivo desde la interfaz web
4. El sistema procesará y cargará los datos automáticamente

## 📝 Formato de Archivos

Los archivos Excel deben seguir el formato estándar del sistema:
- Columnas requeridas según el módulo (transacciones, saldos, etc.)
- Fechas en formato correcto
- Montos numéricos sin formato especial
- Cuentas y conceptos válidos en el sistema
