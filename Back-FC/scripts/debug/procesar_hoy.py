#!/usr/bin/env python3
"""
Script para ver transacciones en la fecha actual (2025)
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date

def main():
    db = next(get_db())
    fecha_actual = date(2025, 9, 3)  # Fecha actual

    print('📊 Transacciones del día 3 de septiembre de 2025:')
    todas_trans = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_actual
    ).all()

    print(f'Total: {len(todas_trans)} transacciones')
    
    for t in todas_trans:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
        print(f'ID:{t.concepto_id} - {concepto.nombre if concepto else "Unknown"}: ${t.monto} (Area: {t.area})')

    # Ahora procesemos las dependencias para ESTA fecha
    from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
    
    print('\n🔄 Procesando dependencias para 2025-09-03...')
    service = DependenciasFlujoCajaService(db)
    
    try:
        service.procesar_dependencias_avanzadas(
            fecha=fecha_actual,
            area='TESORERIA',
            concepto_modificado_id=None,
            cuenta_id=1,
            compania_id=1
        )
        print('✅ Dependencias procesadas')
        
        # Verificar si se actualizó SALDO FINAL CUENTAS
        saldo_final_concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO FINAL CUENTAS'
        ).first()
        
        if saldo_final_concepto:
            transaccion = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_actual,
                TransaccionFlujoCaja.concepto_id == saldo_final_concepto.id
            ).first()
            
            if transaccion:
                print(f'✅ SALDO FINAL CUENTAS para hoy: ${transaccion.monto}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    main()
