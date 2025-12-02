#!/usr/bin/env python3
"""
Inicializa configuraciones GMF por cuenta con "punto cero":
- Crea una GMFConfig activa por cada cuenta que no tenga una.
- Selecciona como componentes TODOS los conceptos activos excepto el propio 'GMF'.
- Fecha de creación = ahora; esto servirá como vigencia desde hoy en adelante.

Se puede re-ejecutar; no duplica si ya existe una configuración activa.
"""
from datetime import datetime
import json
import sys
from pathlib import Path

# Asegurar que el root del proyecto (Back-FC) esté en sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.models import CuentaBancaria, ConceptoFlujoCaja
from app.models.gmf_config import GMFConfig


def main():
    db = SessionLocal()
    try:
        cuentas = db.query(CuentaBancaria).all()
        concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == 'GMF').first()
        gmf_id = concepto_gmf.id if concepto_gmf else None
        
        # ⚠️ SOLO conceptos BASE/MANUALES - NO incluir calculados/subtotales
        # Excluir: GMF(49), SALDO NETO INICIAL PAGADURÍA(4), SUB-TOTAL TESORERÍA(50), 
        # SALDO FINAL CUENTAS(51), DIFERENCIA SALDOS(52), SUBTOTAL MOVIMIENTO PAGADURIA(82),
        # SUBTOTAL SALDO INICIAL PAGADURIA(83), MOVIMIENTO TESORERIA(84), SALDO TOTAL EN BANCOS(85),
        # SALDO DIA ANTERIOR(54), CONSUMO(2), VENTANILLA(3)
        conceptos_excluidos = {2, 3, 4, 49, 50, 51, 52, 54, 82, 83, 84, 85}
        
        conceptos = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.activo == 1
        ).all()
        
        componentes_ids = [
            c.id for c in conceptos 
            if c.id not in conceptos_excluidos and (gmf_id is None or c.id != gmf_id)
        ]
        
        print(f"📊 Conceptos base seleccionados para GMF: {len(componentes_ids)} conceptos")
        print(f"   IDs: {componentes_ids}")

        creadas = 0
        actualizadas = 0
        for cuenta in cuentas:
            existe = db.query(GMFConfig).filter(
                GMFConfig.cuenta_bancaria_id == cuenta.id,
                GMFConfig.activo == True
            ).first()
            if existe:
                # Actualizar la config existente con los componentes correctos
                existe.conceptos_seleccionados = json.dumps(componentes_ids)
                existe.fecha_creacion = datetime.now()
                actualizadas += 1
            else:
                cfg = GMFConfig(
                    cuenta_bancaria_id=cuenta.id,
                    conceptos_seleccionados=json.dumps(componentes_ids),
                    activo=True,
                    fecha_creacion=datetime.now(),
                )
                db.add(cfg)
                creadas += 1
        db.commit()
        print(f"✅ Configuraciones GMF creadas: {creadas}")
        print(f"✅ Configuraciones GMF actualizadas: {actualizadas}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
