from app.core.database import SessionLocal
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

db = SessionLocal()

# IDs que debe sumar SUB TOTAL TESORERÍA
ids_a_sumar = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49]

# Crear la fórmula
ids_str = ','.join(map(str, ids_a_sumar))
formula = f'SUMA({ids_str})'
print(f'📐 Fórmula a configurar: {formula}')

try:
    # Buscar y actualizar el concepto SUB TOTAL TESORERÍA
    concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 50).first()
    
    if concepto:
        print(f'🔧 Actualizando SUB TOTAL TESORERÍA...')
        print(f'   Antes: formula_dependencia = {concepto.formula_dependencia}')
        
        # Actualizar la fórmula
        concepto.formula_dependencia = formula
        
        db.commit()
        
        print(f'   Después: formula_dependencia = {concepto.formula_dependencia}')
        print(f'✅ SUB TOTAL TESORERÍA actualizado correctamente')
        
        # Verificar que se guardó
        db.refresh(concepto)
        print(f'🔍 Verificación: {concepto.formula_dependencia}')
        
    else:
        print('❌ No se encontró el concepto SUB TOTAL TESORERÍA')
        
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
