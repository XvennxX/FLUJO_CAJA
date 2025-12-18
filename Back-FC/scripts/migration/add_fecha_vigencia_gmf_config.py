#!/usr/bin/env python3
"""
Migración: Agregar columna fecha_vigencia_desde a gmf_config

Esta migración:
1. Agrega la columna fecha_vigencia_desde (DATE NOT NULL)
2. Migra datos existentes: fecha_vigencia_desde = DATE(fecha_creacion)
3. Crea índice en (cuenta_bancaria_id, fecha_vigencia_desde) para búsquedas eficientes
"""
import sys
from pathlib import Path
from datetime import datetime

# Asegurar que el root del proyecto esté en sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from app.core.database import engine, SessionLocal

def run_migration():
    """Ejecuta la migración para agregar fecha_vigencia_desde"""
    db = SessionLocal()
    
    try:
        print("🔄 Iniciando migración de gmf_config...")
        
        # 1. Verificar si la columna ya existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'gmf_config' 
            AND column_name = 'fecha_vigencia_desde'
        """))
        
        if result.fetchone():
            print("✅ La columna fecha_vigencia_desde ya existe. Migración no necesaria.")
            return
        
        # 2. Agregar columna fecha_vigencia_desde (temporal como nullable)
        print("📝 Agregando columna fecha_vigencia_desde...")
        db.execute(text("""
            ALTER TABLE gmf_config 
            ADD COLUMN fecha_vigencia_desde DATE
        """))
        db.commit()
        
        # 3. Migrar datos existentes: fecha_vigencia_desde = DATE(fecha_creacion)
        print("📊 Migrando datos existentes...")
        db.execute(text("""
            UPDATE gmf_config 
            SET fecha_vigencia_desde = DATE(fecha_creacion)
            WHERE fecha_vigencia_desde IS NULL
        """))
        db.commit()
        
        # 4. Hacer la columna NOT NULL (sintaxis MySQL)
        print("🔒 Configurando columna como NOT NULL...")
        db.execute(text("""
            ALTER TABLE gmf_config 
            MODIFY COLUMN fecha_vigencia_desde DATE NOT NULL
        """))
        db.commit()
        
        # 5. Crear índice para búsquedas eficientes
        print("⚡ Creando índice en (cuenta_bancaria_id, fecha_vigencia_desde)...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_gmf_config_cuenta_fecha_vigencia 
            ON gmf_config(cuenta_bancaria_id, fecha_vigencia_desde DESC)
        """))
        db.commit()
        
        print("✅ Migración completada exitosamente!")
        print("\n📋 Resumen:")
        print("   - Columna fecha_vigencia_desde agregada")
        print("   - Datos migrados: fecha_vigencia_desde = DATE(fecha_creacion)")
        print("   - Índice creado para búsquedas eficientes")
        print("\n🎯 Sistema de versionado histórico ahora activo:")
        print("   - Cada cambio crea nueva versión con fecha_vigencia_desde")
        print("   - Config aplicable = más reciente con fecha_vigencia_desde <= fecha_objetivo")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("MIGRACIÓN: Add fecha_vigencia_desde to gmf_config")
    print("=" * 80)
    
    respuesta = input("\n¿Deseas ejecutar esta migración? (si/no): ").lower()
    
    if respuesta in ['si', 's', 'yes', 'y']:
        run_migration()
    else:
        print("❌ Migración cancelada.")
