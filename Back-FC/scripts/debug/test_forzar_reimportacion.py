#!/usr/bin/env python3
"""
Test forzando re-importación completa
"""

import sys
import os
import importlib

# Limpiar cualquier importación previa
modules_to_remove = []
for module_name in sys.modules.keys():
    if 'app.services' in module_name:
        modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    del sys.modules[module_name]

# Configurar el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import date

def test_forzar_reimportacion():
    """Test forzando re-importación"""
    print("🔍 === TEST FORZANDO RE-IMPORTACIÓN === 🔍")
    
    try:
        # Importación forzada
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from app.core.config import Settings
        settings = Settings()
        
        # Forzar re-importación del servicio
        import app.services.transaccion_flujo_caja_service
        importlib.reload(app.services.transaccion_flujo_caja_service)
        
        from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
        from app.schemas.flujo_caja import TransaccionFlujoCajaUpdate
        
        # Preparar base de datos
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        servicio = TransaccionFlujoCajaService(db)
        fecha_hoy = date(2025, 9, 16)
        
        # Buscar transacción para modificar
        transaccion_info = db.execute(text("""
            SELECT id, concepto_id, monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id BETWEEN 5 AND 49 AND cuenta_id = 1 AND area = 'tesoreria'
            ORDER BY id LIMIT 1
        """), {"fecha": fecha_hoy}).fetchone()
        
        if not transaccion_info:
            print("❌ No hay transacciones para modificar")
            return
            
        id_transaccion = transaccion_info[0]
        
        print(f"🔧 EJECUTANDO actualizar_transaccion (FORZADO):")
        
        # CREAR DATOS DE ACTUALIZACIÓN
        nuevos_datos = TransaccionFlujoCajaUpdate(
            monto=6666.66,
            descripcion="TEST RE-IMPORTACIÓN FORZADA"
        )
        
        # EJECUTAR
        resultado = servicio.actualizar_transaccion(
            transaccion_id=id_transaccion,
            transaccion_data=nuevos_datos,
            usuario_id=1
        )
        
        if resultado:
            print(f"✅ actualizar_transaccion completado: ID {resultado.id}")
        else:
            print(f"❌ actualizar_transaccion falló")
        
        db.rollback()
        db.close()
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forzar_reimportacion()