#!/usr/bin/env python3
"""
Script para probar la nueva funcionalidad de auto-cálculo de SALDO INICIAL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.schemas.flujo_caja import AreaTransaccionSchema
from datetime import date

def test_saldo_inicial_automatico():
    """Probar el auto-cálculo del SALDO INICIAL"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        service = DependenciasFlujoCajaService(db)
        
        # Probar para el día 10 de septiembre (día siguiente al 9 que ya tiene saldo final)
        fecha_test = date(2025, 9, 10)
        
        print(f"=== PROBANDO AUTO-CÁLCULO SALDO INICIAL PARA {fecha_test} ===")
        print("Base: Día 9 ya tiene SALDO FINAL, día 10 debe auto-calcular SALDO INICIAL")
        
        # Ejecutar el procesamiento de dependencias
        resultado = service.procesar_dependencias_avanzadas(
            fecha=fecha_test,
            area=AreaTransaccionSchema.tesoreria,
            usuario_id=6
        )
        
        print(f"\n=== RESULTADOS ===")
        for update in resultado:
            print(f"Concepto {update['concepto_id']}: {update['concepto_nombre']}")
            print(f"  Cuenta: {update.get('cuenta_id', 'N/A')}")
            print(f"  Monto anterior: ${update['monto_anterior']}")
            print(f"  Monto nuevo: ${update['monto_nuevo']}")
            print(f"  Fecha: {update['fecha']}")
            print()
        
        print(f"Total actualizaciones: {len(resultado)}")
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_saldo_inicial_automatico()
