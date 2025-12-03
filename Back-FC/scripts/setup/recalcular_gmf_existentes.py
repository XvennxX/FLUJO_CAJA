#!/usr/bin/env python3
"""
Recalcula todos los GMF existentes en BD con la configuración corregida.
Borra los GMF actuales y los regenera usando solo conceptos base (sin subtotales).
"""
from datetime import datetime, date
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService

def main():
    db = SessionLocal()
    try:
        # Buscar concepto GMF
        concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == 'GMF').first()
        if not concepto_gmf:
            print("❌ No existe concepto GMF")
            return
        
        print(f"\n✅ Concepto GMF: ID={concepto_gmf.id}")
        
        # Buscar todas las transacciones GMF
        transacciones_gmf = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == concepto_gmf.id
        ).all()
        
        print(f"\n📊 Transacciones GMF encontradas: {len(transacciones_gmf)}")
        
        if not transacciones_gmf:
            print("✅ No hay GMF para recalcular")
            return
        
        # Agrupar por fecha/cuenta para recalcular
        gmf_por_fecha_cuenta = {}
        for t in transacciones_gmf:
            key = (t.fecha, t.cuenta_id)
            gmf_por_fecha_cuenta[key] = t
        
        print(f"\n🔄 Recalculando {len(gmf_por_fecha_cuenta)} combinaciones fecha/cuenta...")
        
        service = DependenciasFlujoCajaService(db)
        recalculados = 0
        errores = 0
        
        for (fecha, cuenta_id), trans_old in gmf_por_fecha_cuenta.items():
            try:
                monto_anterior = trans_old.monto
                usuario_id = trans_old.usuario_id or 1
                compania_id = trans_old.compania_id or 1
                
                # Recalcular con config corregida
                resultado = service.recalcular_gmf(
                    fecha=fecha,
                    cuenta_id=cuenta_id,
                    usuario_id=usuario_id,
                    compania_id=compania_id
                )
                
                if resultado:
                    monto_nuevo = resultado.get('monto_nuevo', 0)
                    print(f"  ✅ Fecha {fecha}, Cuenta {cuenta_id}: {monto_anterior} → {monto_nuevo}")
                    recalculados += 1
                else:
                    print(f"  ⚠️  Fecha {fecha}, Cuenta {cuenta_id}: Sin config o componentes")
            except Exception as e:
                print(f"  ❌ Error en Fecha {fecha}, Cuenta {cuenta_id}: {e}")
                errores += 1
        
        db.commit()
        print(f"\n{'='*80}")
        print(f"✅ Recalculados: {recalculados}")
        print(f"❌ Errores: {errores}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error general: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
