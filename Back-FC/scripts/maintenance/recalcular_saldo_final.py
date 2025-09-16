#!/usr/bin/env python3
"""
Script para recalcular y actualizar el SALDO FINAL CUENTAS del día 3 de septiembre.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from decimal import Decimal
from datetime import date
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def recalcular_saldo_final_cuentas():
    """Recalcula el SALDO FINAL CUENTAS del día 3 usando la fórmula SUMA(4,50)"""
    
    db = SessionLocal()
    try:
        fecha = date(2025, 9, 3)
        
        print(f"🔄 Recalculando SALDO FINAL CUENTAS para {fecha}...")
        
        # Paso 1: Obtener valores de los conceptos 4 (SALDO NETO INICIAL PAGADURÍA) y 50 (SUB-TOTAL TESORERÍA)
        concepto_4_total = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 4,
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        concepto_50_total = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        suma_concepto_4 = sum(t.monto for t in concepto_4_total)
        suma_concepto_50 = sum(t.monto for t in concepto_50_total)
        
        print(f"   📊 Concepto 4 (SALDO NETO INICIAL PAGADURÍA): ${suma_concepto_4:,.2f}")
        print(f"   📊 Concepto 50 (SUB-TOTAL TESORERÍA): ${suma_concepto_50:,.2f}")
        
        # Paso 2: Calcular el total según la fórmula SUMA(4,50)
        total_calculado = suma_concepto_4 + suma_concepto_50
        print(f"   🧮 Total calculado SUMA(4,50): ${total_calculado:,.2f}")
        
        # Paso 3: Actualizar la transacción existente del SALDO FINAL CUENTAS
        transaccion_saldo_final = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).first()
        
        if transaccion_saldo_final:
            valor_anterior = transaccion_saldo_final.monto
            transaccion_saldo_final.monto = total_calculado
            transaccion_saldo_final.descripcion = "Recalculado automáticamente por fórmula SUMA(4,50)"
            
            db.commit()
            
            print(f"   ✅ Transacción actualizada:")
            print(f"      ID: {transaccion_saldo_final.id}")
            print(f"      Valor anterior: ${valor_anterior:,.2f}")
            print(f"      Valor nuevo: ${total_calculado:,.2f}")
            print(f"      Diferencia: ${total_calculado - valor_anterior:,.2f}")
        else:
            print("   ❌ No se encontró la transacción del SALDO FINAL CUENTAS")
        
        # Paso 4: Verificar que el cambio se hizo correctamente
        verificacion = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 51,
            TransaccionFlujoCaja.fecha == fecha,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).first()
        
        if verificacion and verificacion.monto == total_calculado:
            print(f"\n✅ ÉXITO: SALDO FINAL CUENTAS actualizado correctamente")
            print(f"   📅 Fecha: {fecha}")
            print(f"   💰 Valor: ${total_calculado:,.2f}")
            print(f"   📝 Descripción: {verificacion.descripcion}")
            print(f"\n🎯 El saldo inicial del día siguiente (2025-09-04) ahora será: ${total_calculado:,.2f}")
        else:
            print(f"\n❌ ERROR: La verificación falló")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el recálculo: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    recalcular_saldo_final_cuentas()
