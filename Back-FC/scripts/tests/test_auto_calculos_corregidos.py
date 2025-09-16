#!/usr/bin/env python3
"""
Script para probar las correcciones de auto-cálculos por cuenta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from sqlalchemy import func
from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.schemas.flujo_caja import AreaTransaccionSchema

def test_auto_calculos_por_cuenta():
    """Probar que los auto-cálculos funcionen para múltiples cuentas."""
    session = next(get_db())
    
    try:
        hoy = date.today()
        servicio = DependenciasFlujoCajaService(session)
        
        print("=== PROBANDO AUTO-CÁLCULOS POR CUENTA ===")
        
        # Simular que se agregaron transacciones a diferentes cuentas
        cuentas_con_datos = [1, 2, 6]  # Cuentas que según los logs tienen transacciones
        
        for cuenta_id in cuentas_con_datos:
            print(f"\n--- Procesando dependencias para cuenta {cuenta_id} ---")
            
            # Procesar dependencias solo para esta cuenta
            resultado = servicio.procesar_dependencias_avanzadas(
                fecha=hoy,
                area=AreaTransaccionSchema.tesoreria,
                cuenta_id=cuenta_id,
                usuario_id=6
            )
            
            print(f"Resultado: {resultado}")
            
            # Verificar los auto-cálculos para esta cuenta
            conceptos_auto = [4, 50, 51]
            for concepto_id in conceptos_auto:
                transaccion = session.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.concepto_id == concepto_id,
                    TransaccionFlujoCaja.cuenta_id == cuenta_id,
                    TransaccionFlujoCaja.fecha == hoy
                ).first()
                
                concepto = session.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
                concepto_nombre = concepto.nombre if concepto else f"Concepto {concepto_id}"
                
                if transaccion:
                    print(f"  ✅ {concepto_nombre}: ${transaccion.monto}")
                else:
                    print(f"  ❌ {concepto_nombre}: No encontrado")
        
        # Resumen final
        print("\n=== RESUMEN FINAL ===")
        for concepto_id in [4, 50, 51]:
            count = session.query(func.count(TransaccionFlujoCaja.id)).filter(
                TransaccionFlujoCaja.concepto_id == concepto_id,
                TransaccionFlujoCaja.fecha == hoy
            ).scalar()
            
            concepto = session.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
            concepto_nombre = concepto.nombre if concepto else f"Concepto {concepto_id}"
            
            print(f"{concepto_nombre}: {count} transacciones")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_auto_calculos_por_cuenta()
