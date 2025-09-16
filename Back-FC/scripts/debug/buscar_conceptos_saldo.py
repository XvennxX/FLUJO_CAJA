#!/usr/bin/env python3
"""
Script para encontrar los conceptos de SALDO INICIAL y verificar la estructura
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def buscar_conceptos_saldo():
    """Buscar conceptos relacionados con saldo inicial"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Buscar conceptos que contengan 'SALDO'
        conceptos = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre.like('%SALDO%')
        ).all()
        
        print("=== CONCEPTOS CON 'SALDO' ===")
        for concepto in conceptos:
            print(f"ID: {concepto.id} | {concepto.nombre} | Tipo: {concepto.tipo} | Formula: {concepto.formula_dependencia}")
        
        # Buscar conceptos que contengan 'INICIAL'
        conceptos_inicial = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre.like('%INICIAL%')
        ).all()
        
        print("\n=== CONCEPTOS CON 'INICIAL' ===")
        for concepto in conceptos_inicial:
            print(f"ID: {concepto.id} | {concepto.nombre} | Tipo: {concepto.tipo} | Formula: {concepto.formula_dependencia}")
            
        # Buscar conceptos que contengan 'FINAL'
        conceptos_final = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre.like('%FINAL%')
        ).all()
        
        print("\n=== CONCEPTOS CON 'FINAL' ===")
        for concepto in conceptos_final:
            print(f"ID: {concepto.id} | {concepto.nombre} | Tipo: {concepto.tipo} | Formula: {concepto.formula_dependencia}")
            
    finally:
        db.close()

if __name__ == "__main__":
    buscar_conceptos_saldo()
