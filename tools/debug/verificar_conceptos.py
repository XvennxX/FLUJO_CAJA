#!/usr/bin/env python3
"""
Verificar conceptos del sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def main():
    db = next(get_db())
    
    conceptos_importantes = [50, 51, 52, 53, 54, 85]
    
    print("🔍 VERIFICANDO CONCEPTOS IMPORTANTES:")
    print("=" * 50)
    
    for concept_id in conceptos_importantes:
        concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concept_id).first()
        if concepto:
            print(f"ID {concept_id}: {concepto.nombre}")
        else:
            print(f"ID {concept_id}: ❌ NO ENCONTRADO")
    
    print()
    print("🔍 CONCEPTOS QUE CONTIENEN 'SALDO':")
    conceptos_saldo = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre.contains('SALDO')).all()
    for c in conceptos_saldo:
        print(f"ID {c.id}: {c.nombre}")

if __name__ == "__main__":
    main()