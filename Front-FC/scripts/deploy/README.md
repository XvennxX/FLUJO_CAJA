# Scripts de Despliegue

Scripts para automatizar el despliegue de la aplicación frontend a diferentes entornos.

## 📁 **Archivos disponibles:**

### `deploy.sh`
Script principal de despliegue automatizado.

**Uso:**
```bash
./scripts/deploy/deploy.sh
```

**Características:**
- ✅ Verificación previa de archivos construidos
- ✅ Compresión automática de archivos
- ✅ Backup de versión actual
- ✅ Subida al servidor
- ✅ Reinicio de servicios

## ⚙️ **Configuración**

### Archivo `deploy.config.json`
El script genera automáticamente un archivo de configuración:

```json
{
  "server": {
    "host": "your-server.com",
    "port": 22,
    "username": "deploy",
    "deployPath": "/var/www/html"
  },
  "backup": {
    "enabled": true,
    "backupPath": "/var/backups/frontend"
  }
}
```

## 🚀 **Proceso de despliegue:**

1. **Verificación** - Comprueba que existan archivos construidos
2. **Compresión** - Crea archivo .tar.gz con los assets
3. **Backup** - Respalda la versión actual del servidor
4. **Subida** - Transfiere archivos al servidor
5. **Activación** - Reinicia servicios necesarios

## 📋 **Prerequisitos:**

- Ejecutar `npm run build` antes del despliegue
- Configurar acceso SSH al servidor
- Permisos de escritura en el directorio de destino

## 🛡️ **Seguridad:**

- Usa autenticación por clave SSH
- Realiza backup antes de cada despliegue
- Verifica integridad de archivos
- Logs detallados de cada operación
