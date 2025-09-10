#!/usr/bin/env python3
"""
Script para ver todas las transacciones del día 3 de septiembre.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from decimal import Decimal
from datetime import date
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def ver_transacciones_dia_3():
    """Ve todas las transacciones del día 3 de septiembre"""
    
    db = SessionLocal()
    try:
        fecha = date(2025, 9, 3)
        
        print(f"📅 Transacciones del {fecha}:")
        print("=" * 80)
        
        # Obtener todas las transacciones del día 3
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha
        ).join(ConceptoFlujoCaja).all()
        
        if not transacciones:
            print("❌ No se encontraron transacciones para esta fecha")
            return
        
        # Agrupar por área
        transacciones_tesoreria = []
        transacciones_pagaduria = []
        
        for trans in transacciones:
            if trans.area == AreaTransaccion.tesoreria:
                transacciones_tesoreria.append(trans)
            else:
                transacciones_pagaduria.append(trans)
        
        # Mostrar transacciones de tesorería
        print(f"\n🏛️  TESORERÍA ({len(transacciones_tesoreria)} transacciones):")
        print("-" * 60)
        total_tesoreria = Decimal('0.00')
        
        for trans in transacciones_tesoreria:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == trans.concepto_id).first()
            concepto_nombre = concepto.nombre if concepto else f"Concepto {trans.concepto_id}"
            print(f"  ID: {trans.id:3} | Concepto: {trans.concepto_id:2} - {concepto_nombre[:30]:30} | ${trans.monto:>10,.2f}")
            total_tesoreria += trans.monto
        
        print(f"  {'-'*76}")
        print(f"  {'TOTAL TESORERÍA':48} | ${total_tesoreria:>10,.2f}")
        
        # Mostrar transacciones de pagaduría
        print(f"\n💼 PAGADURÍA ({len(transacciones_pagaduria)} transacciones):")
        print("-" * 60)
        total_pagaduria = Decimal('0.00')
        
        for trans in transacciones_pagaduria:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == trans.concepto_id).first()
            concepto_nombre = concepto.nombre if concepto else f"Concepto {trans.concepto_id}"
            print(f"  ID: {trans.id:3} | Concepto: {trans.concepto_id:2} - {concepto_nombre[:30]:30} | ${trans.monto:>10,.2f}")
            total_pagaduria += trans.monto
        
        print(f"  {'-'*76}")
        print(f"  {'TOTAL PAGADURÍA':48} | ${total_pagaduria:>10,.2f}")
        
        # Resumen
        print(f"\n📊 RESUMEN:")
        print(f"   Total Tesorería: ${total_tesoreria:,.2f}")
        print(f"   Total Pagaduría: ${total_pagaduria:,.2f}")
        print(f"   GRAN TOTAL: ${total_tesoreria + total_pagaduria:,.2f}")
        
        # Buscar específicamente los conceptos que necesitamos
        print(f"\n🔍 CONCEPTOS ESPECÍFICOS:")
        
        conceptos_buscar = [4, 50, 51]  # SALDO NETO INICIAL PAGADURÍA, SUB-TOTAL TESORERÍA, SALDO FINAL CUENTAS
        
        for concepto_id in conceptos_buscar:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
            concepto_nombre = concepto.nombre if concepto else f"Concepto {concepto_id}"
            
            trans_concepto = [t for t in transacciones if t.concepto_id == concepto_id]
            total_concepto = sum(t.monto for t in trans_concepto)
            
            print(f"   Concepto {concepto_id:2} - {concepto_nombre[:35]:35}: ${total_concepto:>8,.2f} ({len(trans_concepto)} transacciones)")

    finally:
        db.close()

if __name__ == "__main__":
    ver_transacciones_dia_3()
