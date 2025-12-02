"""
Script para poblar la tabla TRM desde septiembre 2025 hasta hoy
usando la API de datos.gov.co
"""
import sys
import os

# Asegurar que el paquete 'app' sea importable
CURRENT_FILE = os.path.abspath(__file__)
BACK_FC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
if BACK_FC_ROOT not in sys.path:
    sys.path.append(BACK_FC_ROOT)

import requests
import urllib3
from app.core.database import SessionLocal
from app.models.trm import TRM
from datetime import date, timedelta
from decimal import Decimal

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def poblar_trm_desde_septiembre():
    """Obtiene y guarda TRMs desde septiembre 2025 hasta hoy"""
    print("Obteniendo TRMs desde datos.gov.co...")
    
    url = "https://www.datos.gov.co/resource/32sa-8pi3.json"
    params = {
        "$where": "vigenciadesde >= '2025-08-25'",  # Incluir últimos días de agosto para capturar rangos
        "$limit": 5000,
        "$order": "vigenciadesde ASC"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30, verify=False)
        resp.raise_for_status()
        data = resp.json()
        print(f"Obtenidos {len(data)} registros de la API")
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return False
    
    db = SessionLocal()
    insertados = 0
    dias_insertados = 0
    
    try:
        for item in data:
            try:
                # Obtener fechas de vigencia
                fecha_desde_str = item["vigenciadesde"][:10]
                fecha_desde = date.fromisoformat(fecha_desde_str)
                valor = Decimal(item["valor"])
                
                # Verificar si hay vigenciahasta
                fecha_hasta = fecha_desde
                if "vigenciahasta" in item and item["vigenciahasta"]:
                    fecha_hasta_str = item["vigenciahasta"][:10]
                    fecha_hasta = date.fromisoformat(fecha_hasta_str)
                
                # Insertar para cada día en el rango
                fecha_actual = fecha_desde
                while fecha_actual <= fecha_hasta:
                    db.merge(TRM(fecha=fecha_actual, valor=valor))
                    dias_insertados += 1
                    fecha_actual += timedelta(days=1)
                
                insertados += 1
                
                # Log si el rango tiene más de un día
                if fecha_hasta > fecha_desde:
                    print(f"  TRM {valor}: {fecha_desde} hasta {fecha_hasta} ({(fecha_hasta - fecha_desde).days + 1} días)")
                
            except Exception as e:
                print(f"Error procesando item: {e}")
                continue
        
        db.commit()
        print(f"\n✅ Procesados {insertados} registros de la API")
        print(f"✅ Insertados/actualizados {dias_insertados} días en BD")
        
        # Verificar datos insertados
        verificar = db.query(TRM).filter(
            TRM.fecha >= date(2025, 9, 1)
        ).order_by(TRM.fecha).all()
        
        print(f"\nTotal TRMs en BD desde septiembre 2025: {len(verificar)}")
        
        if verificar:
            print("\nPrimeros 5:")
            for t in verificar[:5]:
                print(f"  {t.fecha}: {t.valor}")
            
            print("\nÚltimos 5:")
            for t in verificar[-5:]:
                print(f"  {t.fecha}: {t.valor}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error en la transacción: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = poblar_trm_desde_septiembre()
    sys.exit(0 if success else 1)
