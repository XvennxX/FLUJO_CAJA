#!/usr/bin/env python3
"""
Script para verificar datos existentes en días 10 y 11
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from datetime import date

def verificar_datos_existentes():
    """Verificar qué datos existen para días 10 y 11"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar datos del día 10
        print("=== DATOS DÍA 10 ===")
        trans_dia10 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 10)
        ).all()
        
        print(f"Total transacciones día 10: {len(trans_dia10)}")
        
        saldo_final_dia10 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 10),
            TransaccionFlujoCaja.concepto_id == 51  # SALDO FINAL CUENTAS
        ).all()
        
        print(f"Registros SALDO FINAL (ID 51) día 10: {len(saldo_final_dia10)}")
        for saldo in saldo_final_dia10:
            print(f"  Cuenta {saldo.cuenta_id}: ${saldo.monto}")
        
        # Verificar datos del día 11
        print("\n=== DATOS DÍA 11 ===")
        trans_dia11 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 11)
        ).all()
        
        print(f"Total transacciones día 11: {len(trans_dia11)}")
        
        saldo_inicial_dia11 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 11),
            TransaccionFlujoCaja.concepto_id == 1  # SALDO INICIAL
        ).all()
        
        print(f"Registros SALDO INICIAL (ID 1) día 11: {len(saldo_inicial_dia11)}")
        for saldo in saldo_inicial_dia11:
            print(f"  Cuenta {saldo.cuenta_id}: ${saldo.monto}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verificar_datos_existentes()
