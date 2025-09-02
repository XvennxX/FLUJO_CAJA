"""
Script de migración para crear la tabla TRM
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.trm import TRM

def create_trm_table():
    """
    Crea la tabla TRM en la base de datos
    """
    print("🔄 Creando tabla TRM...")
    
    try:
        # Crear todas las tablas definidas en Base
        Base.metadata.create_all(bind=engine, tables=[TRM.__table__])
        print("✅ Tabla TRM creada exitosamente")
        
        # Mostrar información de la tabla
        print("\n📋 Información de la tabla TRM:")
        print(f"Tabla: {TRM.__tablename__}")
        print("Columnas:")
        for column in TRM.__table__.columns:
            print(f"  - {column.name}: {column.type} {'(PK)' if column.primary_key else ''}")
        
    except Exception as e:
        print(f"❌ Error al crear tabla TRM: {e}")
        return False
    
    return True

def main():
    """
    Función principal
    """
    print("=" * 60)
    print("MIGRACIÓN DE TABLA TRM")
    print("=" * 60)
    
    success = create_trm_table()
    
    if success:
        print("\n🎉 Migración completada exitosamente")
        print("\nPuedes comenzar a usar los endpoints de TRM:")
        print("  - GET /api/v1/trm/current")
        print("  - GET /api/v1/trm/by-date/{fecha}")
        print("  - GET /api/v1/trm/range")
        print("  - POST /api/v1/trm/")
    else:
        print("\n❌ Error en la migración")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
