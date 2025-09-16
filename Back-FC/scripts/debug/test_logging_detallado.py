#!/usr/bin/env python3
"""
Test con logging super detallado para ver exactamente qué pasa
"""

import sys
import os
from datetime import date, datetime

# Configurar el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from app.core.config import Settings
settings = Settings()
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaUpdate

import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_con_logging_detallado():
    """Test con logging super detallado"""
    print("🔍 === TEST CON LOGGING DETALLADO === 🔍")
    
    # Preparar base de datos
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
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
        
        print(f"\n🔧 LLAMANDO actualizar_transaccion con logging máximo:")
        
        # CREAR DATOS DE ACTUALIZACIÓN
        nuevos_datos = TransaccionFlujoCajaUpdate(
            monto=7777.77,
            descripcion="TEST LOGGING DETALLADO"
        )
        
        # Activar logging específico
        logger_servicio = logging.getLogger('app.services.transaccion_flujo_caja_service')
        logger_dependencias = logging.getLogger('app.services.dependencias_flujo_caja_service')
        
        logger_servicio.setLevel(logging.DEBUG)
        logger_dependencias.setLevel(logging.DEBUG)
        
        print(f"📝 Datos a actualizar: monto={nuevos_datos.monto}, descripcion={nuevos_datos.descripcion}")
        
        # EJECUTAR CON LOGGING
        resultado = servicio.actualizar_transaccion(
            transaccion_id=id_transaccion,
            transaccion_data=nuevos_datos,
            usuario_id=1
        )
        
        if resultado:
            print(f"✅ actualizar_transaccion retornó: ID {resultado.id}")
        else:
            print(f"❌ actualizar_transaccion retornó None")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.rollback()  # No guardar cambios
        db.close()
        print(f"🔄 Rollback ejecutado")

if __name__ == "__main__":
    test_con_logging_detallado()