#!/usr/bin/env python3
"""
Test para trazar exactamente qué pasa durante el auto-cálculo del SUBTOTAL TESORERÍA.
Vamos a inspeccionar paso a paso el flujo de actualización.
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

# Configurar logging específico
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def trace_actualizar_transaccion():
    """Traza paso a paso lo que pasa durante actualizar_transaccion"""
    print("🔍 === TRACE COMPLETO DEL AUTO-CÁLCULO === 🔍")
    
    # Preparar base de datos
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        servicio = TransaccionFlujoCajaService(db)
        servicio_dependencias = DependenciasFlujoCajaService(db)
        
        fecha_hoy = date(2025, 9, 16)
        
        print(f"\n1. 📊 Estado inicial del SUBTOTAL TESORERÍA:")
        subtotal_antes = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": fecha_hoy}).fetchone()
        print(f"   SUBTOTAL antes: ${subtotal_antes[0] if subtotal_antes else '0.00'}")
        
        print(f"\n2. 🔍 Buscando transacción a modificar:")
        transaccion_para_modificar = db.execute(text("""
            SELECT id, concepto_id, monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id BETWEEN 5 AND 49 AND cuenta_id = 1 AND area = 'tesoreria'
            ORDER BY id LIMIT 1
        """), {"fecha": fecha_hoy}).fetchone()
        
        if not transaccion_para_modificar:
            print("   ❌ No hay transacciones para modificar")
            return
        
        id_transaccion = transaccion_para_modificar[0]
        concepto_original = transaccion_para_modificar[1]
        monto_original = transaccion_para_modificar[2]
        
        print(f"   📝 ID: {id_transaccion}, Concepto: {concepto_original}, Monto actual: ${monto_original}")
        
        print(f"\n3. 🔧 EJECUTANDO actualizar_transaccion con logging detallado:")
        
        # Activar logging máximo para el servicio
        logging.getLogger('app.services.transaccion_flujo_caja_service').setLevel(logging.DEBUG)
        logging.getLogger('app.services.dependencias_flujo_caja_service').setLevel(logging.DEBUG)
        
        # Crear datos de actualización
        nuevos_datos = TransaccionFlujoCajaUpdate(
            monto=9999.99,
            descripcion=f"TRACE TEST - Modificado para detectar problema"
        )
        
        print(f"   📊 Nuevo monto: ${nuevos_datos.monto}")
        print(f"   📊 Nueva descripción: {nuevos_datos.descripcion}")
        
        print(f"\n   🚀 Llamando servicio.actualizar_transaccion()...")
        
        try:
            resultado = servicio.actualizar_transaccion(
                transaccion_id=id_transaccion,
                transaccion_data=nuevos_datos,
                usuario_id=1
            )
            
            print(f"   ✅ Resultado del servicio: {resultado.id if resultado else 'None'}")
            
        except Exception as e:
            print(f"   ❌ Error durante actualización: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n4. 📊 Estado después del SUBTOTAL TESORERÍA:")
        subtotal_despues = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": fecha_hoy}).fetchone()
        print(f"   SUBTOTAL después: ${subtotal_despues[0] if subtotal_despues else '0.00'}")
        
        print(f"\n5. 📋 Verificación manual de suma de conceptos 5-49:")
        suma_manual = db.execute(text("""
            SELECT COALESCE(SUM(monto), 0) as suma_total 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id BETWEEN 5 AND 49 AND cuenta_id = 1 AND area = 'tesoreria'
        """), {"fecha": fecha_hoy}).fetchone()
        print(f"   Suma manual: ${suma_manual[0]}")
        
        if subtotal_antes and subtotal_despues:
            diferencia_esperada = float(nuevos_datos.monto) - float(monto_original)
            diferencia_real = float(subtotal_despues[0]) - float(subtotal_antes[0])
            
            print(f"\n6. 📈 ANÁLISIS:")
            print(f"   🔢 Cambio en concepto {concepto_original}: ${monto_original} → ${nuevos_datos.monto}")
            print(f"   🔢 Diferencia esperada: ${diferencia_esperada}")
            print(f"   🔢 Diferencia real en SUBTOTAL: ${diferencia_real}")
            print(f"   🔢 Suma manual actual: ${suma_manual[0]}")
            print(f"   🔢 SUBTOTAL actual: ${subtotal_despues[0]}")
            
            if abs(diferencia_real - diferencia_esperada) < 0.01:
                print(f"   ✅ AUTO-CÁLCULO FUNCIONÓ CORRECTAMENTE")
            else:
                print(f"   ❌ AUTO-CÁLCULO FALLÓ")
                print(f"   💡 La suma manual (${suma_manual[0]}) no coincide con SUBTOTAL (${subtotal_despues[0]})")
        
        print(f"\n7. 🔍 DIAGNÓSTICO DEL SERVICIO DE DEPENDENCIAS:")
        print("   Probando procesar_dependencias_completas_ambos_dashboards directamente...")
        
        try:
            resultado_dependencias = servicio_dependencias.procesar_dependencias_completas_ambos_dashboards(
                fecha=fecha_hoy,
                concepto_modificado_id=concepto_original,
                cuenta_id=1,
                compania_id=1,
                usuario_id=1
            )
            
            print(f"   📊 Resultado dependencias: {resultado_dependencias}")
            
        except Exception as e:
            print(f"   ❌ Error en servicio de dependencias: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n8. 📊 Estado FINAL del SUBTOTAL:")
        subtotal_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": fecha_hoy}).fetchone()
        print(f"   SUBTOTAL final: ${subtotal_final[0] if subtotal_final else '0.00'}")
        
    except Exception as e:
        print(f"💥 Error general: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.rollback()  # No guardar cambios
        db.close()
        print(f"\n🔄 Transacción revertida - base de datos restaurada")

if __name__ == "__main__":
    trace_actualizar_transaccion()