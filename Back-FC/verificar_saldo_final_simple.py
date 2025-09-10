#!/usr/bin/env python3
"""
Script simple para verificar que SALDO FINAL CUENTAS del día 3 esté guardado correctamente.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from decimal import Decimal
from datetime import date
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def verificar_saldo_final_cuentas():
    """Verifica que el SALDO FINAL CUENTAS del día 3 esté guardado correctamente"""
    
    db = SessionLocal()
    try:
        # Buscar el concepto SALDO FINAL CUENTAS
        concepto_saldo_final = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == "SALDO FINAL CUENTAS"
        ).first()
        
        if not concepto_saldo_final:
            print("❌ No se encontró el concepto 'SALDO FINAL CUENTAS'")
            return
        
        print(f"✅ Concepto encontrado: {concepto_saldo_final.nombre} (ID: {concepto_saldo_final.id})")
        print(f"   Fórmula de dependencia: {concepto_saldo_final.formula_dependencia}")
        
        # Buscar transacciones del SALDO FINAL CUENTAS para el 3 de septiembre
        fecha_buscar = date(2025, 9, 3)
        
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == concepto_saldo_final.id,
            TransaccionFlujoCaja.fecha == fecha_buscar,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        print(f"\n📅 Transacciones de 'SALDO FINAL CUENTAS' para {fecha_buscar}:")
        print(f"   Cantidad encontrada: {len(transacciones)}")
        
        if transacciones:
            for trans in transacciones:
                print(f"   - ID: {trans.id}")
                print(f"     Monto: ${trans.monto:,.2f}")
                print(f"     Cuenta ID: {trans.cuenta_id}")
                print(f"     Descripción: {trans.descripcion}")
                print(f"     Fecha de creación: {trans.created_at}")
        else:
            print("   ❌ No se encontraron transacciones")
        
        # Verificar que el valor sea $176.00
        valor_esperado = Decimal('176.00')
        valor_encontrado = sum(t.monto for t in transacciones) if transacciones else Decimal('0.00')
        
        print(f"\n📊 Resumen:")
        print(f"   Valor esperado: ${valor_esperado:,.2f}")
        print(f"   Valor encontrado: ${valor_encontrado:,.2f}")
        
        if valor_encontrado == valor_esperado:
            print(f"   ✅ CORRECTO: El SALDO FINAL CUENTAS está guardado correctamente")
            print(f"   ✅ El saldo inicial del día 4 debería ser ${valor_esperado:,.2f}")
        else:
            print(f"   ❌ ERROR: El valor no coincide")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_saldo_final_cuentas()
