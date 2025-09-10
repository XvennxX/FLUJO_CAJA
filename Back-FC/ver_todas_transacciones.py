#!/usr/bin/env python3
"""
Script para ver todas las transacciones del día 3
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

    print('📊 TODAS las transacciones del día 3:')
    todas_trans = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba
    ).all()

    for t in todas_trans:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first()
        print(f'ID:{t.concepto_id} - {concepto.nombre if concepto else "Unknown"}: ${t.monto} (Area BD: {t.area})')

if __name__ == "__main__":
    main()
