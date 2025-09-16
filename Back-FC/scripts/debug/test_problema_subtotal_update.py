#!/usr/bin/env python3
"""
Test para reproducir el problema del SUBTOTAL TESORERÍA que no se actualiza
cuando modificas una transacción existente.
"""
import os
import sys
from datetime import datetime, date

# Agregar directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root_dir, "Back-FC"))

from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate, TransaccionFlujoCajaUpdate, AreaTransaccionSchema
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST PROBLEMA SUBTOTAL TESORERÍA UPDATE ===")
    print("🎯 Reproduciendo: Modificar transacción existente no actualiza SUBTOTAL")
    
    db = SessionLocal()
    service = TransaccionFlujoCajaService(db)
    dep_service = DependenciasFlujoCajaService(db)
    
    try:
        fecha_test = date(2025, 9, 16)
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (5, 50)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Crear una transacción de tesorería inicial (ID 5 = PAGOS INTERCOMPAÑÍAS)
        print("\n2. Creando transacción inicial de tesorería...")
        transaccion_data = TransaccionFlujoCajaCreate(
            fecha=fecha_test,
            concepto_id=5,  # PAGOS INTERCOMPAÑÍAS
            cuenta_id=1,
            monto=Decimal("1000.00"),
            descripcion="Test inicial - PAGOS INTERCOMPAÑÍAS",
            area=AreaTransaccionSchema.tesoreria,
            compania_id=1
        )
        
        transaccion_creada = service.crear_transaccion(transaccion_data, usuario_id=6)
        print(f"   ✅ Transacción creada: ID {transaccion_creada.id}, monto ${transaccion_creada.monto}")
        
        # 3. Verificar si se creó el SUBTOTAL TESORERÍA automáticamente
        subtotal_inicial = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == 1
        ).first()
        
        if subtotal_inicial:
            print(f"   ✅ SUBTOTAL TESORERÍA creado automáticamente: ${subtotal_inicial.monto}")
        else:
            print("   ⚠️ SUBTOTAL TESORERÍA NO se creó automáticamente")
            print("   🔄 Ejecutando recálculo manual...")
            dep_service.procesar_dependencias_completas_ambos_dashboards(
                fecha=fecha_test,
                concepto_modificado_id=5,
                cuenta_id=1,
                compania_id=1,
                usuario_id=6
            )
            
            # Verificar nuevamente
            subtotal_inicial = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_test,
                TransaccionFlujoCaja.concepto_id == 50,
                TransaccionFlujoCaja.cuenta_id == 1
            ).first()
            
            if subtotal_inicial:
                print(f"   ✅ SUBTOTAL TESORERÍA creado tras recálculo: ${subtotal_inicial.monto}")
            else:
                print("   ❌ SUBTOTAL TESORERÍA sigue sin crearse")
                return
        
        # 4. PROBLEMA: Modificar la transacción existente
        print(f"\n4. Modificando transacción existente de ${transaccion_creada.monto} a $2000...")
        
        update_data = TransaccionFlujoCajaUpdate(
            monto=Decimal("2000.00"),
            descripcion="Test modificado - PAGOS INTERCOMPAÑÍAS"
        )
        
        transaccion_actualizada = service.actualizar_transaccion(
            transaccion_creada.id, 
            update_data, 
            usuario_id=6
        )
        
        print(f"   ✅ Transacción actualizada: ${transaccion_actualizada.monto}")
        
        # 5. Verificar si el SUBTOTAL TESORERÍA se actualizó automáticamente
        subtotal_actualizado = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == 1
        ).first()
        
        print(f"\n5. Verificando SUBTOTAL TESORERÍA tras actualización:")
        if subtotal_actualizado:
            print(f"   📊 SUBTOTAL anterior: ${subtotal_inicial.monto}")
            print(f"   📊 SUBTOTAL actual: ${subtotal_actualizado.monto}")
            
            if subtotal_actualizado.monto == Decimal("2000.00"):
                print("   ✅ SUBTOTAL se actualizó correctamente")
            else:
                print("   ❌ PROBLEMA: SUBTOTAL NO se actualizó automáticamente")
                print("   🔍 Esto confirma el bug reportado por el usuario")
                
                # 6. Intentar solucionarlo con recálculo completo
                print("\n6. Intentando solución con recálculo completo...")
                dep_service.procesar_dependencias_completas_ambos_dashboards(
                    fecha=fecha_test,
                    concepto_modificado_id=5,
                    cuenta_id=1,
                    compania_id=1,
                    usuario_id=6
                )
                
                # Verificar si ahora sí se actualizó
                subtotal_final = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_test,
                    TransaccionFlujoCaja.concepto_id == 50,
                    TransaccionFlujoCaja.cuenta_id == 1
                ).first()
                
                if subtotal_final and subtotal_final.monto == Decimal("2000.00"):
                    print("   ✅ SOLUCIONADO: Recálculo completo funciona")
                else:
                    print("   ❌ Problema persiste incluso con recálculo completo")
        else:
            print("   ❌ SUBTOTAL TESORERÍA desapareció tras actualización")
        
        print(f"\n=== RESUMEN ===")
        print(f"🔍 Transacción original: ${Decimal('1000.00')}")
        print(f"🔄 Transacción modificada: ${transaccion_actualizada.monto}")
        print(f"📊 SUBTOTAL inicial: ${subtotal_inicial.monto if subtotal_inicial else 'N/A'}")
        print(f"📊 SUBTOTAL final: ${subtotal_actualizado.monto if subtotal_actualizado else 'N/A'}")
        
        if subtotal_actualizado and subtotal_actualizado.monto != Decimal("2000.00"):
            print("❌ CONFIRMADO: El bug existe - actualizar transacción no recalcula SUBTOTAL")
        elif subtotal_actualizado and subtotal_actualizado.monto == Decimal("2000.00"):
            print("✅ Sin problema - SUBTOTAL se actualiza correctamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()