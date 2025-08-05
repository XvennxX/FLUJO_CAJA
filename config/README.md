# Configuraciones Globales

Archivos de configuración compartidos entre servicios.

## Estructura

```
config/
├── development.env         # Variables para desarrollo
├── production.env          # Variables para producción
├── testing.env            # Variables para testing
├── nginx.conf             # Configuración de Nginx
└── README.md
```

## Variables de Entorno

### Base de Datos
- `DB_HOST`: Host de MySQL
- `DB_PORT`: Puerto de MySQL (default: 3306)
- `DB_USER`: Usuario de base de datos
- `DB_PASSWORD`: Contraseña de base de datos
- `DB_NAME`: Nombre de la base de datos

### API
- `API_HOST`: Host del backend
- `API_PORT`: Puerto del backend (default: 8000)
- `SECRET_KEY`: Clave secreta para JWT
- `DEBUG`: Modo debug (true/false)

### Frontend
- `REACT_APP_API_URL`: URL del backend
- `REACT_APP_ENV`: Entorno (development/production)

## Uso

Copiar el archivo correspondiente al entorno y renombrar a `.env`:

```bash
cp config/development.env .env
```
