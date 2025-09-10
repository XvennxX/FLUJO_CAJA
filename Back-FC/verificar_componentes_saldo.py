#!/usr/bin/env python3
"""
Script para verificar los componentes del SALDO FINAL CUENTAS
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date

def main():
    db = next(get_db())
    fecha_prueba = date(2024, 9, 3)

    print('🔍 Verificando componentes de SALDO FINAL CUENTAS para 2024-09-03:')

    # Buscar los conceptos
    concepto_4 = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 4).first()
    concepto_50 = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 50).first()

    print(f'📋 Concepto ID 4: {concepto_4.nombre if concepto_4 else "No encontrado"}')
    print(f'📋 Concepto ID 50: {concepto_50.nombre if concepto_50 else "No encontrado"}')

    # Buscar transacciones para estos conceptos en la fecha
    if concepto_4:
        trans_4 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_prueba,
            TransaccionFlujoCaja.concepto_id == 4
        ).all()
        print(f'💰 Transacciones {concepto_4.nombre}: {len(trans_4)}')
        for t in trans_4:
            print(f'  - ${t.monto} (Area: {t.area})')

    if concepto_50:
        trans_50 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_prueba,
            TransaccionFlujoCaja.concepto_id == 50
        ).all()
        print(f'💰 Transacciones {concepto_50.nombre}: {len(trans_50)}')
        for t in trans_50:
            print(f'  - ${t.monto} (Area: {t.area})')

    # También verificar todas las transacciones del día 3 por área
    print('\n📊 Resumen de transacciones del día 3:')
    
    # TESORERIA
    trans_tesoreria = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.area == 'tesoreria'
    ).all()
    
    print(f'\n🏛️ TESORERIA ({len(trans_tesoreria)} transacciones):')
    for t in trans_tesoreria:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
        print(f'  - {concepto.nombre if concepto else "ID:"+str(t.concepto_id)}: ${t.monto}')
    
    # PAGADURIA
    trans_pagaduria = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.area == 'pagaduria'
    ).all()
    
    print(f'\n💼 PAGADURIA ({len(trans_pagaduria)} transacciones):')
    for t in trans_pagaduria:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
        print(f'  - {concepto.nombre if concepto else "ID:"+str(t.concepto_id)}: ${t.monto}')

if __name__ == "__main__":
    main()
