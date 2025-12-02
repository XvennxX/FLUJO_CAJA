"""
Script de migración para crear la tabla de configuración GMF
"""
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import text
from app.core.database import engine, SessionLocal

def crear_tabla_gmf_config():
    """Crear tabla gmf_config en la base de datos"""
    
    sql = """
    CREATE TABLE IF NOT EXISTS gmf_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cuenta_bancaria_id INT NOT NULL,
        conceptos_seleccionados TEXT NULL,
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_gmf_cuenta_bancaria 
            FOREIGN KEY (cuenta_bancaria_id) 
            REFERENCES cuentas_bancarias(id) 
            ON DELETE CASCADE,
            
        INDEX idx_gmf_cuenta_bancaria (cuenta_bancaria_id),
        INDEX idx_gmf_activo (activo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        print("🔄 Creando tabla gmf_config...")
        
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        
        print("✅ Tabla gmf_config creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tabla gmf_config: {e}")
        return False

def verificar_tabla():
    """Verificar que la tabla fue creada correctamente"""
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'gmf_config'"))
            if result.fetchone():
                print("✅ Verificación exitosa: Tabla gmf_config existe")
                
                # Mostrar estructura de la tabla
                result = conn.execute(text("DESCRIBE gmf_config"))
                print("\n📋 Estructura de la tabla gmf_config:")
                for row in result:
                    print(f"   - {row[0]}: {row[1]}")
                
                return True
            else:
                print("❌ Verificación fallida: Tabla gmf_config no existe")
                return False
                
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal de migración"""
    print("="*70)
    print("MIGRACIÓN: Crear tabla gmf_config")
    print("="*70)
    
    # Crear tabla
    if not crear_tabla_gmf_config():
        print("\n❌ Migración fallida")
        sys.exit(1)
    
    # Verificar tabla
    if not verificar_tabla():
        print("\n❌ Migración fallida en verificación")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)

if __name__ == "__main__":
    main()
