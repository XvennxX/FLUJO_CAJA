#!/usr/bin/env python3
"""
Test para verificar si el problema es de transacciones de base de datos.
Vamos a hacer commit explícito y verificar.
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
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaUpdate, AreaTransaccionSchema

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_transacciones_db():
    """Test para verificar el problema de transacciones"""
    print("🔍 === TEST DE TRANSACCIONES DE BASE DE DATOS === 🔍")
    
    # Preparar base de datos
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        servicio = TransaccionFlujoCajaService(db)
        fecha_hoy = date(2025, 9, 16)
        
        print(f"\n1. 📊 Estado inicial:")
        subtotal_antes = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": fecha_hoy}).fetchone()
        print(f"   SUBTOTAL antes: ${subtotal_antes[0] if subtotal_antes else '0.00'}")
        
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
        monto_original = transaccion_info[2]
        
        print(f"\n2. 🔧 MODIFICANDO transacción ID {id_transaccion}:")
        print(f"   Monto original: ${monto_original}")
        print(f"   Nuevo monto: $8888.88")
        
        # CREAR DATOS DE ACTUALIZACIÓN
        nuevos_datos = TransaccionFlujoCajaUpdate(
            monto=8888.88,
            descripcion="TEST TRANSACCIONES DB"
        )
        
        print(f"\n3. ⚡ EJECUTANDO actualizar_transaccion CON COMMIT REAL:")
        resultado = servicio.actualizar_transaccion(
            transaccion_id=id_transaccion,
            transaccion_data=nuevos_datos,
            usuario_id=1
        )
        
        if resultado:
            print(f"   ✅ Transacción actualizada exitosamente")
        else:
            print(f"   ❌ Error actualizando transacción")
            return
        
        print(f"\n4. 📊 Estado después (sin rollback):")
        subtotal_despues = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": fecha_hoy}).fetchone()
        
        suma_manual = db.execute(text("""
            SELECT COALESCE(SUM(monto), 0) as suma_total 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id BETWEEN 5 AND 49 AND cuenta_id = 1 AND area = 'tesoreria'
        """), {"fecha": fecha_hoy}).fetchone()
        
        print(f"   SUBTOTAL después: ${subtotal_despues[0] if subtotal_despues else '0.00'}")
        print(f"   Suma manual: ${suma_manual[0]}")
        
        diferencia_esperada = float(nuevos_datos.monto) - float(monto_original)
        
        if subtotal_antes and subtotal_despues:
            diferencia_real = float(subtotal_despues[0]) - float(subtotal_antes[0])
            
            print(f"\n5. 📈 ANÁLISIS FINAL:")
            print(f"   🔢 Diferencia esperada: ${diferencia_esperada}")
            print(f"   🔢 Diferencia real: ${diferencia_real}")
            print(f"   🔢 Suma manual: ${suma_manual[0]}")
            print(f"   🔢 SUBTOTAL actual: ${subtotal_despues[0]}")
            
            if abs(diferencia_real - diferencia_esperada) < 0.01:
                print(f"   ✅ AUTO-CÁLCULO FUNCIONÓ CORRECTAMENTE")
            elif float(suma_manual[0]) == float(subtotal_despues[0]):
                print(f"   ✅ AUTO-CÁLCULO FUNCIONÓ - coinciden suma y subtotal")
            else:
                print(f"   ❌ AUTO-CÁLCULO FALLÓ")
        
        # FORZAR COMMIT FINAL
        print(f"\n6. 💾 FORZANDO COMMIT FINAL:")
        db.commit()
        print(f"   ✅ Cambios confirmados en base de datos")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_transacciones_db()