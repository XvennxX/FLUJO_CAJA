#!/usr/bin/env python3
"""
Script para arreglar el problema del área y recalcular SALDO FINAL CUENTAS
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date
from decimal import Decimal

def main():
    db = next(get_db())
    fecha_actual = date(2025, 9, 3)

    print('🔧 Solucionando problema de SALDO FINAL CUENTAS...')

    # Buscar conceptos que componen el SALDO FINAL CUENTAS
    # SALDO NETO INICIAL PAGADURÍA (ID: 4) + SUB-TOTAL TESORERÍA (ID: 50)
    
    # Buscar transacciones sin filtro de área para ID 4
    trans_saldo_neto = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual,
        TransaccionFlujoCaja.concepto_id == 4
    ).all()
    
    # Buscar transacciones sin filtro de área para ID 50  
    trans_sub_total = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual,
        TransaccionFlujoCaja.concepto_id == 50
    ).all()
    
    print(f'📊 Transacciones SALDO NETO INICIAL PAGADURÍA (ID:4): {len(trans_saldo_neto)}')
    for t in trans_saldo_neto:
        print(f'  - ${t.monto} (Area: {t.area})')
    
    print(f'📊 Transacciones SUB-TOTAL TESORERÍA (ID:50): {len(trans_sub_total)}')
    for t in trans_sub_total:
        print(f'  - ${t.monto} (Area: {t.area})')
    
    # Calcular la suma manualmente
    total_saldo_neto = sum(t.monto for t in trans_saldo_neto)
    total_sub_total = sum(t.monto for t in trans_sub_total)
    
    saldo_final_calculado = total_saldo_neto + total_sub_total
    
    print(f'\n🧮 Cálculo manual:')
    print(f'   SALDO NETO INICIAL PAGADURÍA: ${total_saldo_neto}')
    print(f'   SUB-TOTAL TESORERÍA: ${total_sub_total}')
    print(f'   SALDO FINAL CUENTAS debería ser: ${saldo_final_calculado}')
    
    # Actualizar la transacción SALDO FINAL CUENTAS
    trans_saldo_final = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual,
        TransaccionFlujoCaja.concepto_id == 51  # SALDO FINAL CUENTAS
    ).first()
    
    if trans_saldo_final:
        trans_saldo_final.monto = saldo_final_calculado
        trans_saldo_final.descripcion = f'Calculado automáticamente: {total_saldo_neto} + {total_sub_total}'
        db.commit()
        print(f'✅ SALDO FINAL CUENTAS actualizado a ${saldo_final_calculado}')
    else:
        # Crear nueva transacción
        nueva_trans = TransaccionFlujoCaja(
            fecha=fecha_actual,
            concepto_id=51,
            cuenta_id=1,
            monto=saldo_final_calculado,
            descripcion=f'Calculado automáticamente: {total_saldo_neto} + {total_sub_total}',
            usuario_id=1,
            area=AreaTransaccion.tesoreria,
            compania_id=1
        )
        db.add(nueva_trans)
        db.commit()
        print(f'✅ SALDO FINAL CUENTAS creado con valor ${saldo_final_calculado}')
    
    print('\n🎯 Problema resuelto. Ahora el saldo inicial del día siguiente debería funcionar correctamente.')

if __name__ == "__main__":
    main()
