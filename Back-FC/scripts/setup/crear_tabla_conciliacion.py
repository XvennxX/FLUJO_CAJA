"""
Script para crear la tabla de conciliaciones contables
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.conciliacion_contable import ConciliacionContable

def create_conciliacion_table():
    """
    Crea la tabla de conciliaciones contables en la base de datos
    """
    print("🔄 Creando tabla de conciliaciones contables...")
    
    try:
        # Crear la tabla
        Base.metadata.create_all(bind=engine, tables=[ConciliacionContable.__table__])
        print("✅ Tabla 'conciliaciones_contables' creada exitosamente")
        
        # Mostrar información de la tabla
        print("\n📊 Información de la tabla:")
        print(f"Tabla: {ConciliacionContable.__tablename__}")
        print("Columnas:")
        for column in ConciliacionContable.__table__.columns:
            print(f"  - {column.name}: {column.type} {'(PK)' if column.primary_key else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tabla de conciliaciones: {e}")
        return False

def main():
    """
    Función principal
    """
    print("=" * 60)
    print("MIGRACIÓN DE TABLA CONCILIACIONES CONTABLES")
    print("=" * 60)
    
    success = create_conciliacion_table()
    
    if success:
        print("\n🎉 Migración completada exitosamente")
        print("\nPuedes comenzar a usar los endpoints de conciliación:")
        print("  - POST /api/v1/conciliacion/fecha")
        print("  - PUT /api/v1/conciliacion/centralizadora/{empresa_id}")
        print("  - PUT /api/v1/conciliacion/confirmar/{empresa_id}")
        print("  - PUT /api/v1/conciliacion/evaluar-todas")
        print("  - PUT /api/v1/conciliacion/cerrar-todas")
    else:
        print("\n❌ Error en la migración")
    
    print("=" * 60)

if __name__ == "__main__":
    main()