"""
Script para crear e insertar datos en la tabla dias_festivos.
"""
import sys
import os
from datetime import date

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal, engine
from app.models.dias_festivos import DiaFestivo, Base

def crear_tabla_y_datos():
    """Crear tabla y insertar datos de festivos colombianos."""
    try:
        # Crear todas las tablas
        print("Creando tablas...")
        Base.metadata.create_all(bind=engine)
        
        # Crear sesión
        db = SessionLocal()
        
        # Limpiar datos existentes para evitar duplicados
        count = db.query(DiaFestivo).count()
        if count > 0:
            print(f"Eliminando {count} registros existentes...")
            db.query(DiaFestivo).delete()
            db.commit()
        
        # Festivos de Colombia 2025
        festivos_2025 = [
            (date(2025, 1, 1), 'Año Nuevo', 'Celebración del primer día del año', 'civil'),
            (date(2025, 1, 6), 'Reyes Magos', 'Epifanía del Señor', 'religioso'),
            (date(2025, 3, 24), 'Día de San José', 'Festividad de San José', 'religioso'),
            (date(2025, 4, 17), 'Jueves Santo', 'Jueves previo a la Pascua', 'religioso'),
            (date(2025, 4, 18), 'Viernes Santo', 'Conmemoración de la crucifixión de Jesucristo', 'religioso'),
            (date(2025, 5, 1), 'Día del Trabajo', 'Día Internacional del Trabajador', 'civil'),
            (date(2025, 6, 2), 'Ascensión de Jesús', 'Ascensión del Señor', 'religioso'),
            (date(2025, 6, 23), 'Corpus Christi', 'Festividad católica', 'religioso'),
            (date(2025, 6, 30), 'San Pedro y San Pablo', 'Festividad de los apóstoles', 'religioso'),
            (date(2025, 7, 20), 'Día de la Independencia', 'Independencia de Colombia', 'nacional'),
            (date(2025, 8, 7), 'Batalla de Boyacá', 'Conmemoración de la Batalla de Boyacá', 'nacional'),
            (date(2025, 8, 18), 'Asunción de la Virgen', 'Asunción de María', 'religioso'),
            (date(2025, 10, 13), 'Día de la Raza', 'Día de la Hispanidad', 'nacional'),
            (date(2025, 11, 3), 'Todos los Santos', 'Festividad católica', 'religioso'),
            (date(2025, 11, 17), 'Independencia de Cartagena', 'Independencia de Cartagena', 'nacional'),
            (date(2025, 12, 8), 'Inmaculada Concepción', 'Festividad católica', 'religioso'),
            (date(2025, 12, 25), 'Navidad', 'Celebración del nacimiento de Jesucristo', 'religioso')
        ]
        
        # Festivos de Colombia 2026 (fechas aproximadas según regulación)
        festivos_2026 = [
            (date(2026, 1, 1), 'Año Nuevo', 'Celebración del primer día del año', 'civil'),
            (date(2026, 1, 12), 'Reyes Magos', 'Epifanía del Señor (trasladado)', 'religioso'),
            (date(2026, 3, 23), 'Día de San José', 'Festividad de San José (trasladado)', 'religioso'),
            (date(2026, 4, 2), 'Jueves Santo', 'Jueves previo a la Pascua', 'religioso'),
            (date(2026, 4, 3), 'Viernes Santo', 'Conmemoración de la crucifixión de Jesucristo', 'religioso'),
            (date(2026, 5, 1), 'Día del Trabajo', 'Día Internacional del Trabajador', 'civil'),
            (date(2026, 5, 18), 'Ascensión de Jesús', 'Ascensión del Señor (trasladado)', 'religioso'),
            (date(2026, 6, 8), 'Corpus Christi', 'Festividad católica (trasladado)', 'religioso'),
            (date(2026, 6, 15), 'Sagrado Corazón de Jesús', 'Festividad católica (trasladado)', 'religioso'),
            (date(2026, 6, 29), 'San Pedro y San Pablo', 'Festividad de los apóstoles (trasladado)', 'religioso'),
            (date(2026, 7, 20), 'Día de la Independencia', 'Independencia de Colombia', 'nacional'),
            (date(2026, 8, 7), 'Batalla de Boyacá', 'Conmemoración de la Batalla de Boyacá', 'nacional'),
            (date(2026, 8, 17), 'Asunción de la Virgen', 'Asunción de María (trasladado)', 'religioso'),
            (date(2026, 10, 12), 'Día de la Raza', 'Día de la Hispanidad (trasladado)', 'nacional'),
            (date(2026, 11, 2), 'Todos los Santos', 'Festividad católica (trasladado)', 'religioso'),
            (date(2026, 11, 16), 'Independencia de Cartagena', 'Independencia de Cartagena (trasladado)', 'nacional'),
            (date(2026, 12, 8), 'Inmaculada Concepción', 'Festividad católica', 'religioso'),
            (date(2026, 12, 25), 'Navidad', 'Celebración del nacimiento de Jesucristo', 'religioso')
        ]
        
        # Combinar todos los festivos
        todos_festivos = festivos_2025 + festivos_2026
        
        # Insertar registros
        print(f"Insertando {len(todos_festivos)} festivos...")
        for fecha, nombre, descripcion, tipo in todos_festivos:
            festivo = DiaFestivo(
                fecha=fecha,
                nombre=nombre,
                descripcion=descripcion,
                tipo=tipo,
                activo=True
            )
            db.add(festivo)
        
        # Confirmar transacción
        db.commit()
        print("¡Datos insertados exitosamente!")
        
        # Verificar inserción
        count = db.query(DiaFestivo).count()
        print(f"Total de festivos en la base de datos: {count}")
        
        db.close()
        
    except Exception as e:
        print(f"Error al crear tabla o insertar datos: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise

if __name__ == "__main__":
    crear_tabla_y_datos()