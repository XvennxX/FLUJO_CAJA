# Base de Datos - MySQL

Configuración y scripts para la base de datos MySQL.

## Estructura

```
Database/
├── scripts/
│   ├── create_database.sql    # Creación de BD y usuario
│   ├── tables.sql            # Definición de tablas
│   ├── indexes.sql           # Índices para optimización
│   ├── views.sql             # Vistas para reportes
│   └── procedures.sql        # Procedimientos almacenados
├── seeds/
│   ├── categories.sql        # Datos iniciales de categorías
│   ├── users.sql            # Usuarios de prueba
│   └── sample_data.sql      # Datos de ejemplo
├── backup/
│   └── (archivos de respaldo)
└── README.md
```

## Configuración

### Requisitos
- MySQL 8.0 o superior
- Usuario con permisos de creación de BD

### Instalación
1. Ejecutar `scripts/create_database.sql`
2. Ejecutar `scripts/tables.sql`
3. Ejecutar `scripts/indexes.sql`
4. Cargar datos iniciales desde `seeds/`

## Backup

Los respaldos se almacenan en la carpeta `backup/` con nomenclatura:
- `backup_YYYYMMDD_HHMM.sql`
