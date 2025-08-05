"""
Script para verificar la estructura de las tablas
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_table_structure():
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        print("🔍 Verificando estructura de las tablas...")
        
        with engine.connect() as connection:
            connection.execute(text("USE flujo_caja"))
            
            tables = ['rol', 'usuario', 'cuenta', 'concepto', 'ingreso', 'egreso']
            
            for table in tables:
                print(f"\n📊 Estructura de la tabla '{table}':")
                result = connection.execute(text(f"DESCRIBE {table}"))
                columns = result.fetchall()
                
                for column in columns:
                    field = column[0]
                    field_type = column[1]
                    null = column[2]
                    key = column[3]
                    default = column[4]
                    extra = column[5]
                    
                    print(f"  {field}: {field_type} {'NULL' if null == 'YES' else 'NOT NULL'} {key} {extra}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_table_structure()
