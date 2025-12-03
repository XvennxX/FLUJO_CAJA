#!/usr/bin/env python3
"""
Script para probar el recálculo automático de SALDO NETO INICIAL PAGADURÍA (ID 4)
"""
from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        service = DependenciasFlujoCajaService(db)
        
        fecha_test = date(2025, 9, 1)
        logger.info(f"🚀 Ejecutando procesamiento de dependencias para {fecha_test}")
        
        result = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            usuario_id=1,
            compania_id=1
        )
        
        db.commit()
        
        print(f"\n✅ Procesadas {len(result)} actualizaciones")
        
        # Mostrar solo el concepto 4
        for r in result:
            if r['concepto_id'] == 4:
                print(f"\n📊 SALDO NETO INICIAL PAGADURÍA:")
                print(f"   Monto: ${float(r['monto_nuevo']):.2f}")
                print(f"   Cuenta ID: {r['cuenta_id']}")
                if 'componentes' in r:
                    print(f"   Componentes: {r['componentes']}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
