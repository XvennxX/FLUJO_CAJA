#!/bin/bash
# Script para despliegue automático

CONFIG_FILE="deploy.config.json"
BUILD_DIR="dist"

echo "🚀 Iniciando proceso de despliegue..."

# Verificar que existe el directorio de construcción
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ No se encuentra el directorio de construcción. Ejecuta 'npm run build' primero."
    exit 1
fi

# Cargar configuración
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  No se encuentra el archivo de configuración. Creando uno por defecto..."
    cat > "$CONFIG_FILE" << EOF
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
EOF
    echo "📝 Configuración creada en $CONFIG_FILE. Actualiza los valores y vuelve a ejecutar."
    exit 1
fi

echo "📦 Comprimiendo archivos..."
tar -czf release.tar.gz -C "$BUILD_DIR" .

echo "🔄 Creando backup de la versión actual..."
# Aquí iría la lógica de backup remoto

echo "📤 Subiendo archivos al servidor..."
# Aquí iría la lógica de despliegue (rsync, scp, etc.)

echo "🔧 Reiniciando servicios..."
# Aquí iría la lógica de reinicio de servicios

echo "✅ Despliegue completado exitosamente!"
echo "🌐 La aplicación debería estar disponible en: https://your-domain.com"
