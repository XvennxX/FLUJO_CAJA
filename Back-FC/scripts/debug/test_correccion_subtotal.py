#!/usr/bin/env python3
"""
Test para verificar que la corrección del SUBTOTAL TESORERÍA funciona correctamente.
"""
import os
import sys
from datetime import datetime, date

# Agregar directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root_dir, "Back-FC"))

from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate, TransaccionFlujoCajaUpdate, AreaTransaccionSchema
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST VERIFICACIÓN CORRECCIÓN SUBTOTAL TESORERÍA ===")
    print("🎯 Verificando que la actualización de transacciones recalcule el SUBTOTAL correctamente")
    
    db = SessionLocal()
    service = TransaccionFlujoCajaService(db)
    
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
        
        # 2. Crear transacción inicial de tesorería
        print("\n2. Creando transacción inicial...")
        transaccion_data = TransaccionFlujoCajaCreate(
            fecha=fecha_test,
            concepto_id=5,  # PAGOS INTERCOMPAÑÍAS (debe contribuir a SUBTOTAL TESORERÍA)
            cuenta_id=1,
            monto=Decimal("1000.00"),
            descripcion="Test corrección - PAGOS INTERCOMPAÑÍAS",
            area=AreaTransaccionSchema.tesoreria,
            compania_id=1
        )
        
        transaccion_creada = service.crear_transaccion(transaccion_data, usuario_id=6)
        print(f"   ✅ Transacción creada: ID {transaccion_creada.id}, monto ${transaccion_creada.monto}")
        
        # 3. Verificar SUBTOTAL TESORERÍA inicial
        subtotal_inicial = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == 1
        ).first()
        
        if subtotal_inicial:
            print(f"   📊 SUBTOTAL TESORERÍA inicial: ${subtotal_inicial.monto}")
        else:
            print("   ❌ SUBTOTAL TESORERÍA no se creó - test fallido")
            return
        
        # 4. ACTUALIZAR la transacción existente
        print(f"\n4. MODIFICANDO transacción de ${transaccion_creada.monto} a $2500...")
        
        update_data = TransaccionFlujoCajaUpdate(
            monto=Decimal("2500.00"),
            descripcion="Test corrección ACTUALIZADA - PAGOS INTERCOMPAÑÍAS"
        )
        
        transaccion_actualizada = service.actualizar_transaccion(
            transaccion_creada.id, 
            update_data, 
            usuario_id=6
        )
        
        print(f"   ✅ Transacción actualizada: ${transaccion_actualizada.monto}")
        
        # 5. Verificar que el SUBTOTAL TESORERÍA se actualizó automáticamente
        subtotal_actualizado = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == 1
        ).first()
        
        print(f"\n5. Verificando SUBTOTAL TESORERÍA tras actualización:")
        if subtotal_actualizado:
            print(f"   📊 SUBTOTAL anterior: ${subtotal_inicial.monto}")
            print(f"   📊 SUBTOTAL actual: ${subtotal_actualizado.monto}")
            
            # El SUBTOTAL debe reflejar el nuevo monto
            if subtotal_actualizado.monto == Decimal("2500.00"):
                print("   ✅ ¡CORRECCIÓN EXITOSA! SUBTOTAL se actualizó correctamente")
                print("   🎉 El bug ha sido solucionado")
            else:
                print(f"   ⚠️  SUBTOTAL actualizado pero con valor inesperado: ${subtotal_actualizado.monto}")
                print(f"   💡 Esperado: $2500.00, Actual: ${subtotal_actualizado.monto}")
                
                # Verificar si hay otros conceptos contribuyendo
                print("\n   🔍 Verificando otros conceptos de tesorería...")
                otros_conceptos = db.execute(text("""
                    SELECT concepto_id, monto, descripcion
                    FROM transacciones_flujo_caja
                    WHERE fecha = :fecha
                    AND concepto_id BETWEEN 5 AND 49
                    AND cuenta_id = 1
                    AND area = 'tesoreria'
                """), {"fecha": fecha_test}).fetchall()
                
                total_componentes = Decimal('0')
                for concepto_id, monto, desc in otros_conceptos:
                    print(f"      • Concepto {concepto_id}: ${monto} - {desc}")
                    total_componentes += monto
                
                print(f"   📊 Total componentes: ${total_componentes}")
                
                if subtotal_actualizado.monto == total_componentes:
                    print("   ✅ SUBTOTAL es correcto (suma de todos los componentes)")
                else:
                    print("   ❌ SUBTOTAL no coincide con la suma de componentes")
        else:
            print("   ❌ SUBTOTAL TESORERÍA desapareció tras actualización")
        
        # 6. Test adicional: Segunda modificación
        print(f"\n6. Test adicional: Segunda modificación a $3000...")
        
        segunda_update = TransaccionFlujoCajaUpdate(
            monto=Decimal("3000.00"),
            descripcion="Segunda modificación para verificar consistencia"
        )
        
        transaccion_final = service.actualizar_transaccion(
            transaccion_creada.id, 
            segunda_update, 
            usuario_id=6
        )
        
        subtotal_final = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == 1
        ).first()
        
        if subtotal_final:
            print(f"   📊 SUBTOTAL tras segunda modificación: ${subtotal_final.monto}")
            # Verificar consistencia
            if "3000" in str(subtotal_final.monto):
                print("   ✅ Segunda modificación también funciona correctamente")
            else:
                print("   ⚠️  Segunda modificación con valor inesperado")
        
        print(f"\n=== RESUMEN FINAL ===")
        print(f"🔍 Transacción original: $1000.00")
        print(f"🔄 Primera modificación: $2500.00")
        print(f"🔄 Segunda modificación: $3000.00")
        print(f"📊 SUBTOTAL final: ${subtotal_final.monto if subtotal_final else 'N/A'}")
        
        if subtotal_final and "3000" in str(subtotal_final.monto):
            print("🎉 ¡CORRECCIÓN COMPLETA! El sistema ahora actualiza correctamente el SUBTOTAL TESORERÍA")
        else:
            print("❌ La corrección necesita ajustes adicionales")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()