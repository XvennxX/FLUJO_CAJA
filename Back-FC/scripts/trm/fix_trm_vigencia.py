"""
Reconciliar TRM en BD usando la fecha oficial de vigencia (vigenciadesde).
- Recalcula los últimos N días desde Datos Abiertos.
- Inserta/actualiza por fecha de vigencia.
- Opcionalmente elimina fechas en el rango que no coincidan con la vigencia oficial.
"""

import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Set

# Asegurar import de 'app' y del scraper
CURRENT_FILE = os.path.abspath(__file__)
BACK_FC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
if BACK_FC_ROOT not in sys.path:
    sys.path.append(BACK_FC_ROOT)

from app.core.database import SessionLocal
from app.models.trm import TRM
from scripts.trm.trm_scraper import TRMScraper


def reconcile_last_days(days_back: int = 14, delete_outliers: bool = True) -> None:
    today = date.today()
    scraper = TRMScraper()

    # 1) Construir mapa deseado por fecha de vigencia
    desired: Dict[date, Decimal] = {}
    for i in range(days_back, -1, -1):
        qdate = today - timedelta(days=i)
        res = scraper.get_trm_from_datos_abiertos(qdate)
        if res and "vigenciadesde" in res and "valor" in res:
            desired[res["vigenciadesde"]] = res["valor"]  # type: ignore[index]

    if not desired:
        print("No se obtuvieron TRM desde Datos Abiertos para el rango solicitado.")
        return

    min_d = min(desired.keys())
    max_d = max(desired.keys())

    # 2) Upsert en BD
    db = SessionLocal()
    try:
        for f, v in desired.items():
            row = db.query(TRM).filter(TRM.fecha == f).first()
            if row:
                row.valor = v
            else:
                db.add(TRM(fecha=f, valor=v))
        db.commit()

        # 3) Eliminar fechas fuera de lo deseado dentro del rango
        if delete_outliers:
            existing_rows = (
                db.query(TRM)
                .filter(TRM.fecha >= min_d)
                .filter(TRM.fecha <= max_d)
                .all()
            )
            keep: Set[date] = set(desired.keys())
            removed = 0
            for r in existing_rows:
                if r.fecha not in keep:
                    db.delete(r)
                    removed += 1
            if removed:
                db.commit()
                print(f"Eliminadas {removed} fechas que no corresponden a vigenciadesde oficial en el rango {min_d}..{max_d}")
    finally:
        db.close()

    print(f"Reconciliación TRM completada para {len(desired)} fechas (rango {min_d}..{max_d}).")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14, help="Días hacia atrás a reconciliar (default: 14)")
    parser.add_argument("--no-delete", action="store_true", help="No eliminar outliers en el rango")
    args = parser.parse_args()

    reconcile_last_days(days_back=args.days, delete_outliers=not args.no_delete)
