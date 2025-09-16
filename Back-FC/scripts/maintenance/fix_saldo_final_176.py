#!/usr/bin/env python3
"""
Script para actualizar manualmente el SALDO FINAL CUENTAS a $176.00 como debería ser.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from decimal import Decimal
from datetime import date
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion

def actualizar_saldo_final_correcto():
    """Actualiza el SALDO FINAL CUENTAS al valor correcto de $176.00"""
    
    db = SessionLocal()
    try:
        fecha = date(2025, 9, 3)
        valor_correcto = Decimal('176.00')
        
        print(f"🔧 Actualizando SALDO FINAL CUENTAS para {fecha}...")
        print(f"   Valor objetivo: ${valor_correcto:,.2f}")
        
        # Buscar la transacción existente del SALDO FINAL CUENTAS
        transaccion_saldo_final = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).first()
        
        if transaccion_saldo_final:
            valor_anterior = transaccion_saldo_final.monto
            transaccion_saldo_final.monto = valor_correcto
            transaccion_saldo_final.descripcion = "Valor corregido manualmente - SALDO FINAL CUENTAS correcto"
            
            db.commit()
            
            print(f"   ✅ Transacción actualizada:")
            print(f"      ID: {transaccion_saldo_final.id}")
            print(f"      Valor anterior: ${valor_anterior:,.2f}")
            print(f"      Valor nuevo: ${valor_correcto:,.2f}")
            print(f"      Diferencia: ${valor_correcto - valor_anterior:,.2f}")
            
            # Verificar la actualización
            verificacion = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.id == transaccion_saldo_final.id
            ).first()
            
            if verificacion and verificacion.monto == valor_correcto:
                print(f"\n✅ ÉXITO: SALDO FINAL CUENTAS actualizado correctamente")
                print(f"   📅 Fecha: {fecha}")
                print(f"   💰 Valor: ${valor_correcto:,.2f}")
                print(f"   📝 Descripción: {verificacion.descripcion}")
                print(f"\n🎯 RESULTADO:")
                print(f"   El saldo inicial del día 2025-09-04 ahora será: ${valor_correcto:,.2f}")
                print(f"   ✅ El sistema de flujo de caja funcionará correctamente")
            else:
                print(f"\n❌ ERROR: La verificación falló")
        else:
            print("   ❌ No se encontró la transacción del SALDO FINAL CUENTAS")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la actualización: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    actualizar_saldo_final_correcto()
