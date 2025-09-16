#!/usr/bin/env python3
"""
Script para analizar la estructura actual de conceptos y encontrar el SALDO INICIAL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from datetime import date

def analizar_conceptos():
    """Analizar conceptos para encontrar SALDO INICIAL"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Buscar todos los conceptos ordenados por orden_display
        conceptos = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.area == 'tesoreria'
        ).order_by(ConceptoFlujoCaja.orden_display).all()
        
        print("=== TODOS LOS CONCEPTOS DE TESORERÍA ===")
        for concepto in conceptos:
            print(f"ID: {concepto.id:2d} | Orden: {concepto.orden_display:2d} | {concepto.nombre} | Tipo: {concepto.tipo}")
            if concepto.formula_dependencia:
                print(f"     Formula: {concepto.formula_dependencia}")
        
        # Buscar transacciones del día 9 y 10 para ver el patrón
        print(f"\n=== TRANSACCIONES DÍA 9 (cuenta 1) ===")
        trans_dia9 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 9),
            TransaccionFlujoCaja.cuenta_id == 1
        ).order_by(TransaccionFlujoCaja.concepto_id).all()
        
        for trans in trans_dia9:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == trans.concepto_id).first()
            nombre = concepto.nombre if concepto else "DESCONOCIDO"
            print(f"Concepto {trans.concepto_id:2d}: {nombre} = ${trans.monto}")
        
        print(f"\n=== TRANSACCIONES DÍA 10 (cuenta 1) ===")
        trans_dia10 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == date(2025, 9, 10),
            TransaccionFlujoCaja.cuenta_id == 1
        ).order_by(TransaccionFlujoCaja.concepto_id).all()
        
        for trans in trans_dia10:
            concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == trans.concepto_id).first()
            nombre = concepto.nombre if concepto else "DESCONOCIDO"
            print(f"Concepto {trans.concepto_id:2d}: {nombre} = ${trans.monto}")
            
    finally:
        db.close()

if __name__ == "__main__":
    analizar_conceptos()
