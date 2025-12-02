"""Test para ver TODOS los GMF guardados en BD"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

db: Session = SessionLocal()

try:
    # Buscar concepto GMF
    concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == 'GMF').first()
    if not concepto_gmf:
        print("❌ No existe concepto GMF")
        exit(1)
    
    print(f"\n✅ Concepto GMF: ID={concepto_gmf.id}")
    
    # Buscar TODAS las transacciones GMF
    transacciones_gmf = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.concepto_id == concepto_gmf.id
    ).order_by(TransaccionFlujoCaja.fecha, TransaccionFlujoCaja.cuenta_id).all()
    
    print(f"\n📊 TRANSACCIONES GMF EN BD: {len(transacciones_gmf)}")
    print("="*100)
    
    for t in transacciones_gmf:
        print(f"\nFecha: {t.fecha} | Cuenta: {t.cuenta_id} | Monto: {t.monto} | Área: {t.area.value}")
        if t.auditoria:
            import json
            aud = t.auditoria
            if 'componentes' in aud:
                print(f"  Componentes: {aud['componentes']}")
            if 'base_suma_componentes' in aud:
                print(f"  Base suma: {aud.get('base_suma_componentes', 'N/A')}")
            if 'formula' in aud:
                print(f"  Fórmula: {aud['formula']}")
        print(f"  Descripción: {t.descripcion}")
    
    print("\n" + "="*100)

finally:
    db.close()
