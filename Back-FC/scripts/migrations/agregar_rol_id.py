"""
Script para agregar columna rol_id a tabla usuarios
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal

def agregar_columna_rol_id():
    """Agrega la columna rol_id a la tabla usuarios"""
    
    print("=" * 80)
    print("🔄 Agregando columna rol_id a tabla usuarios")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Verificar si la columna ya existe
        result = db.execute(text("DESCRIBE usuarios")).fetchall()
        columnas = [row[0] for row in result]
        
        if 'rol_id' in columnas:
            print("\n⚠️  La columna 'rol_id' ya existe en la tabla usuarios")
            return True
        
        # Agregar columna rol_id
        print("\n1. Agregando columna rol_id...")
        db.execute(text("""
            ALTER TABLE usuarios 
            ADD COLUMN rol_id INT NULL
        """))
        db.commit()
        print("   ✅ Columna rol_id agregada")
        
        # Agregar índice
        print("\n2. Agregando índice...")
        db.execute(text("""
            ALTER TABLE usuarios 
            ADD INDEX idx_rol_id (rol_id)
        """))
        db.commit()
        print("   ✅ Índice agregado")
        
        # Agregar foreign key
        print("\n3. Agregando foreign key...")
        db.execute(text("""
            ALTER TABLE usuarios 
            ADD CONSTRAINT fk_usuarios_rol 
            FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL
        """))
        db.commit()
        print("   ✅ Foreign key agregada")
        
        # Verificar
        result = db.execute(text("DESCRIBE usuarios")).fetchall()
        columnas = [row[0] for row in result]
        
        if 'rol_id' in columnas:
            print("\n✅ Columna 'rol_id' agregada exitosamente a 'usuarios'")
            return True
        else:
            print("\n❌ Error: Columna 'rol_id' no se agregó correctamente")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    try:
        exito = agregar_columna_rol_id()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
