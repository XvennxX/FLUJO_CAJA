"""Test de debug para GMF - verificar por qué se triplica el valor"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from datetime import date

db: Session = SessionLocal()

try:
    # Fecha y cuenta de ejemplo
    fecha_test = date(2025, 9, 1)
    cuenta_id_test = 2
    
    print("\n" + "="*80)
    print("🔍 DEBUG GMF - Verificando componentes y GMF guardado")
    print("="*80)
    
    # 1. Consultar concepto GMF
    concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == 'GMF').first()
    if concepto_gmf:
        print(f"\n✅ Concepto GMF encontrado: ID={concepto_gmf.id}")
    else:
        print("\n❌ Concepto GMF NO encontrado")
        exit(1)
    
    # 2. Consultar todas las transacciones de esa fecha/cuenta
    transacciones = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_test,
        TransaccionFlujoCaja.cuenta_id == cuenta_id_test
    ).all()
    
    print(f"\n📊 Transacciones encontradas: {len(transacciones)}")
    
    suma_componentes = 0
    transacciones_gmf = []
    
    for t in transacciones:
        concepto_nombre = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == t.concepto_id).first().nombre
        print(f"\n  - Concepto: {concepto_nombre} (ID {t.concepto_id})")
        print(f"    Monto: {t.monto}")
        print(f"    Área: {t.area.value}")
        print(f"    ID transacción: {t.id}")
        
        if concepto_nombre == 'GMF':
            transacciones_gmf.append(t)
        else:
            # Sumar todos los demás (excepto GMF)
            suma_componentes += t.monto
    
    print(f"\n{'='*80}")
    print(f"📈 SUMA DE COMPONENTES (sin GMF): {suma_componentes}")
    print(f"🧮 GMF ESPERADO (suma × 4/1000): {suma_componentes * 4 / 1000}")
    print(f"{'='*80}")
    
    # 3. Mostrar todas las transacciones GMF encontradas
    if transacciones_gmf:
        print(f"\n⚠️  TRANSACCIONES GMF ENCONTRADAS: {len(transacciones_gmf)}")
        for idx, gmf_trans in enumerate(transacciones_gmf, 1):
            print(f"\n  GMF #{idx}:")
            print(f"    ID: {gmf_trans.id}")
            print(f"    Monto: {gmf_trans.monto}")
            print(f"    Área: {gmf_trans.area.value}")
            print(f"    Descripción: {gmf_trans.descripcion}")
            if gmf_trans.auditoria:
                import json
                print(f"    Auditoría: {json.dumps(gmf_trans.auditoria, indent=6)}")
    else:
        print("\n✅ No se encontraron transacciones GMF (correcto si aún no se ha calculado)")
    
    print("\n" + "="*80)

finally:
    db.close()
