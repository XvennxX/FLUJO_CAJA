"""
Script para agregar TRMs del 1 y 2 de septiembre 2025
"""
import sys
import os

CURRENT_FILE = os.path.abspath(__file__)
BACK_FC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
if BACK_FC_ROOT not in sys.path:
    sys.path.append(BACK_FC_ROOT)

import requests
import urllib3
from app.core.database import SessionLocal
from app.models.trm import TRM
from datetime import date
from decimal import Decimal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def agregar_sept_1_2():
    print("Consultando TRM para septiembre 1 y 2...")
    
    url = "https://www.datos.gov.co/resource/32sa-8pi3.json"
    params = {
        "$where": "vigenciadesde >= '2025-09-01' AND vigenciadesde <= '2025-09-02'",
        "$order": "vigenciadesde ASC"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30, verify=False)
        resp.raise_for_status()
        data = resp.json()
        print(f"Registros encontrados en API: {len(data)}")
        
        for item in data:
            print(f"  {item['vigenciadesde'][:10]}: {item['valor']}")
        
        if len(data) > 0:
            db = SessionLocal()
            try:
                for item in data:
                    fecha = date.fromisoformat(item["vigenciadesde"][:10])
                    valor = Decimal(item["valor"])
                    db.merge(TRM(fecha=fecha, valor=valor))
                
                db.commit()
                print("\n✅ Insertados en BD")
                
                # Verificar
                verificar = db.query(TRM).filter(
                    TRM.fecha >= date(2025, 9, 1),
                    TRM.fecha <= date(2025, 9, 5)
                ).order_by(TRM.fecha).all()
                
                print("\nTRMs septiembre 1-5:")
                for t in verificar:
                    print(f"  {t.fecha}: {t.valor}")
                
            finally:
                db.close()
        else:
            print("\n⚠️ No hay datos en la API para esas fechas")
            print("Probablemente fueron días festivos o no había mercado cambiario")
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = agregar_sept_1_2()
    sys.exit(0 if success else 1)
