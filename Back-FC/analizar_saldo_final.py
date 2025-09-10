#!/usr/bin/env python3
"""
Script para analizar qué conceptos base forman el SALDO FINAL CUENTAS
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date
from decimal import Decimal

def main():
    db = next(get_db())
    fecha_actual = date(2025, 9, 3)

    print('🔍 Analizando conceptos para SALDO FINAL CUENTAS...')
    
    # Obtener todas las transacciones reales del día
    transacciones = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual
    ).all()
    
    # Separar por área
    tesoreria_total = Decimal('0.00')
    pagaduria_total = Decimal('0.00')
    
    print('\n📊 Transacciones por área:')
    
    print('\n🏛️ TESORERÍA:')
    for t in transacciones:
        if 'tesoreria' in str(t.area).lower():
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
            if concepto and concepto.id != 51:  # Excluir SALDO FINAL CUENTAS
                print(f'  - {concepto.nombre}: ${t.monto}')
                tesoreria_total += t.monto
    
    print(f'\n💰 Total TESORERÍA (sin SALDO FINAL): ${tesoreria_total}')
    
    print('\n💼 PAGADURÍA:')
    for t in transacciones:
        if 'pagaduria' in str(t.area).lower():
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
            if concepto:
                print(f'  - {concepto.nombre}: ${t.monto}')
                pagaduria_total += t.monto
    
    print(f'\n💰 Total PAGADURÍA: ${pagaduria_total}')
    
    # El SALDO FINAL CUENTAS debería ser la suma de ambas áreas
    saldo_final_correcto = tesoreria_total + pagaduria_total
    print(f'\n🎯 SALDO FINAL CUENTAS correcto: ${saldo_final_correcto}')
    
    # Verificar si necesitamos actualizar SALDO NETO INICIAL PAGADURÍA
    concepto_saldo_neto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 4).first()
    if concepto_saldo_neto:
        print(f'\n📋 {concepto_saldo_neto.nombre}:')
        print(f'   Fórmula: {concepto_saldo_neto.formula_dependencia}')
        
        # Si la fórmula es "SALDO INICIAL + CONSUMO - VENTANILLA", necesitamos los conceptos base
        if concepto_saldo_neto.formula_dependencia == "SALDO INICIAL + CONSUMO - VENTANILLA":
            print('   ⚠️ Esta es una fórmula textual, necesita conceptos específicos')
    
    # Actualizar SALDO FINAL CUENTAS con el valor correcto
    trans_saldo_final = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual,
        TransaccionFlujoCaja.concepto_id == 51
    ).first()
    
    if trans_saldo_final:
        trans_saldo_final.monto = saldo_final_correcto
        trans_saldo_final.descripcion = f'Suma total: Tesorería ${tesoreria_total} + Pagaduría ${pagaduria_total}'
        db.commit()
        print(f'\n✅ SALDO FINAL CUENTAS actualizado a ${saldo_final_correcto}')

if __name__ == "__main__":
    main()
