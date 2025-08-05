# Configuración con Docker

Archivos de configuración para contenedores Docker.

## Estructura

```
docker/
├── docker-compose.yml      # Orquestación de servicios
├── docker-compose.dev.yml  # Configuración para desarrollo
├── docker-compose.prod.yml # Configuración para producción
├── Dockerfile.backend      # Imagen del backend
├── Dockerfile.frontend     # Imagen del frontend
└── .env.example           # Variables de entorno de ejemplo
```

## Servicios

### Backend Service
- Python API con FastAPI
- Puerto: 8000
- Volúmenes para desarrollo

### Frontend Service
- Aplicación web
- Puerto: 3000
- Proxy reverso a backend

### Database Service
- MySQL 8.0
- Puerto: 3306
- Volumen persistente para datos

### Uso

```bash
# Desarrollo
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
