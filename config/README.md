# Configuración del Proyecto

Este directorio contiene archivos de configuración centralizados del proyecto.

## 📁 Archivos

### `docker-compose.yml`
Configuración de Docker Compose para levantar los servicios:
- PostgreSQL (Base de datos)
- Backend (FastAPI)
- Frontend (React)

**Uso:**
```bash
docker-compose -f config/docker-compose.yml up -d
```

### `Makefile`
Comandos útiles para el desarrollo del proyecto.

**Uso:**
```bash
# Ver comandos disponibles
make help

# Ejemplos
make install    # Instalar dependencias
make dev        # Iniciar desarrollo
make test       # Ejecutar tests
make clean      # Limpiar archivos temporales
```

## ⚙️ Variables de Entorno

Las variables de entorno se configuran en:
- Raíz del proyecto: `.env` (basado en `.env.example`)
- Backend: `Back-FC/.env`
- Frontend: `Front-FC/.env`

## 🔧 Configuración por Entorno

- **Desarrollo:** Usa los valores por defecto de `.env.example`
- **Producción:** Configura variables específicas según el servidor

## 📚 Más Información

Ver documentación completa en: `docs/`
