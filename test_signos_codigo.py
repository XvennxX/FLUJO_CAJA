#!/usr/bin/env python3
"""
Script para probar la lógica de signos corregida basándose en CODIGO
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import ConceptoFlujoCaja
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService

def main():
    print("🧪 PRUEBA: Lógica de signos basada en CODIGO")
    print("=" * 50)
    
    db = SessionLocal()
    service = TransaccionFlujoCajaService(db)
    
    # Verificar conceptos ID 5 e ID 6
    conceptos_prueba = [5, 6]
    
    for concepto_id in conceptos_prueba:
        concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id == concepto_id
        ).first()
        
        if concepto:
            print(f"\n📋 Concepto ID {concepto_id}:")
            print(f"   Nombre: {concepto.nombre}")
            print(f"   Código: '{concepto.codigo}'")
            
            # Probar diferentes montos
            montos_prueba = [100, -100, 300, -200]
            
            for monto in montos_prueba:
                resultado = service._aplicar_signo_por_tipo_concepto(monto, concepto_id)
                print(f"   Monto {monto:+4} → {resultado:+4}")
        else:
            print(f"❌ Concepto ID {concepto_id} no encontrado")
    
    # Caso específico del problema reportado
    print(f"\n🎯 CASO ESPECÍFICO:")
    print(f"   ID 5 (PAGOS): 300 → {service._aplicar_signo_por_tipo_concepto(300, 5)}")
    print(f"   ID 6 (COBROS): 200 → {service._aplicar_signo_por_tipo_concepto(200, 6)}")
    
    monto_5 = service._aplicar_signo_por_tipo_concepto(300, 5)
    monto_6 = service._aplicar_signo_por_tipo_concepto(200, 6)
    suma = monto_5 + monto_6
    print(f"   Suma esperada: {monto_5} + {monto_6} = {suma}")
    
    db.close()

if __name__ == "__main__":
    main()