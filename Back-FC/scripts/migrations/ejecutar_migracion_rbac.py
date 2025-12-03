"""
Script para aplicar migración de sistema RBAC
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.core.database import engine, SessionLocal

def ejecutar_migracion():
    """Ejecuta la migración SQL para agregar el sistema RBAC"""
    
    # Leer el archivo SQL
    sql_file = Path(__file__).parent / "001_agregar_sistema_rbac.sql"
    
    if not sql_file.exists():
        print(f"❌ Error: No se encontró el archivo {sql_file}")
        return False
    
    print("=" * 80)
    print("🔄 EJECUTANDO MIGRACIÓN: Sistema de Roles y Permisos (RBAC)")
    print("=" * 80)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Dividir en statements individuales (por el punto y coma)
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    db = SessionLocal()
    
    try:
        for i, statement in enumerate(statements, 1):
            # Saltar comentarios y líneas vacías
            if not statement or statement.startswith('--') or statement.startswith('/*'):
                continue
            
            # Limpiar el statement
            clean_statement = statement.strip()
            
            # Extraer nombre de operación para logging
            operation = clean_statement.split()[0].upper()
            
            print(f"\n[{i}/{len(statements)}] Ejecutando: {operation}...")
            
            try:
                db.execute(text(clean_statement))
                db.commit()
                print(f"   ✅ Completado")
            except Exception as e:
                error_msg = str(e)
                
                # Si la tabla ya existe, no es un error crítico
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print(f"   ⚠️  Ya existe (saltando): {error_msg.split(':')[0]}")
                    db.rollback()
                    continue
                else:
                    print(f"   ❌ Error: {error_msg}")
                    db.rollback()
                    raise
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        
        # Verificar que las tablas existen
        print("\n📊 Verificando tablas creadas:")
        
        tables = ['roles', 'permisos', 'rol_permiso']
        for table in tables:
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'")).fetchone()
            if result:
                print(f"   ✅ Tabla '{table}' creada correctamente")
            else:
                print(f"   ❌ Tabla '{table}' NO encontrada")
        
        # Verificar columna rol_id en usuarios
        result = db.execute(text("DESCRIBE usuarios")).fetchall()
        columnas = [row[0] for row in result]
        
        if 'rol_id' in columnas:
            print(f"   ✅ Columna 'rol_id' agregada a 'usuarios'")
        else:
            print(f"   ❌ Columna 'rol_id' NO encontrada en 'usuarios'")
        
        print("\n" + "=" * 80)
        print("🎯 SIGUIENTE PASO:")
        print("   Ejecutar: python -m scripts.setup.init_roles_permisos")
        print("   Para crear roles y permisos iniciales")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA MIGRACIÓN: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    try:
        exito = ejecutar_migracion()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
