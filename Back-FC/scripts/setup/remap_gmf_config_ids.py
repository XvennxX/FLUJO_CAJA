"""Remapea IDs antiguos erróneos (79->29 EGRESO DIVIDENDOS, 68->43 EMBARGOS) en configuraciones GMF.
Si tras remapeo quedan IDs fuera de la lista permitida, se eliminan. Si la lista queda vacía se asignan todos los permitidos.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.core.database import SessionLocal
from app.models.gmf_config import GMFConfig

PERMITIDOS = {5,9,12,13,29,34,35,43,31,47,36,26,22,32,33,45,25,46}
REMAPPING = {79:29, 68:43}

def run():
    db = SessionLocal()
    try:
        configs = db.query(GMFConfig).filter(GMFConfig.activo==True).all()
        cambios = 0
        for cfg in configs:
            if not cfg.conceptos_seleccionados:
                continue
            try:
                data = json.loads(cfg.conceptos_seleccionados)
            except Exception:
                continue
            original = list(data) if isinstance(data,list) else []
            nuevos = []
            for val in original:
                try:
                    vid = int(val['id']) if isinstance(val,dict) and 'id' in val else int(val)
                except Exception:
                    continue
                vid = REMAPPING.get(vid, vid)
                if vid in PERMITIDOS and vid not in nuevos:
                    nuevos.append(vid)
            if not nuevos:
                nuevos = sorted(PERMITIDOS)
            if set(nuevos) != set(original):
                cfg.conceptos_seleccionados = json.dumps(nuevos)
                cambios += 1
        db.commit()
        print(f"✅ Remapeo completado. Configuraciones modificadas: {cambios}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
