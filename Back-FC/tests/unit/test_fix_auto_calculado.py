"""
Script para verificar que la corrección del atributo es_auto_calculado funcione correctamente
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def test_concepto_attributes():
    """Verificar que los conceptos tengan los atributos correctos"""
    db = SessionLocal()
    try:
        print("🔍 Verificando atributos de ConceptoFlujoCaja...")
        
        # Obtener un concepto de ejemplo
        concepto = db.query(ConceptoFlujoCaja).first()
        
        if not concepto:
            print("⚠️ No hay conceptos en la base de datos")
            return
        
        print(f"\n✅ Concepto encontrado: {concepto.nombre}")
        print(f"   ID: {concepto.id}")
        print(f"   Código: {concepto.codigo}")
        print(f"   Área: {concepto.area}")
        
        # Verificar atributos clave
        atributos_esperados = [
            'id', 'nombre', 'codigo', 'tipo', 'area', 'orden_display', 
            'activo', 'depende_de_concepto_id', 'tipo_dependencia', 'formula_dependencia'
        ]
        
        print("\n📋 Verificando atributos:")
        for attr in atributos_esperados:
            if hasattr(concepto, attr):
                valor = getattr(concepto, attr)
                print(f"   ✅ {attr}: {valor}")
            else:
                print(f"   ❌ {attr}: NO EXISTE")
        
        # Verificar que NO exista es_auto_calculado
        if hasattr(concepto, 'es_auto_calculado'):
            print("\n❌ ERROR: El atributo 'es_auto_calculado' existe y NO DEBERÍA")
        else:
            print("\n✅ CORRECTO: El atributo 'es_auto_calculado' NO existe")
        
        # Verificar lógica de auto-calculado
        conceptos_auto_calculados = [2, 52, 54, 82, 83, 84, 85]
        es_auto_calculado = (
            concepto.id in conceptos_auto_calculados or
            concepto.depende_de_concepto_id is not None
        )
        
        print(f"\n🔍 Lógica de auto-calculado para concepto {concepto.id}:")
        print(f"   - Está en lista de auto-calculados: {concepto.id in conceptos_auto_calculados}")
        print(f"   - Tiene dependencias (depende_de_concepto_id): {concepto.depende_de_concepto_id is not None}")
        print(f"   - ES AUTO-CALCULADO: {es_auto_calculado}")
        
        # Probar con varios conceptos
        print("\n📊 Verificando varios conceptos:")
        conceptos = db.query(ConceptoFlujoCaja).limit(10).all()
        for c in conceptos:
            es_auto = (
                c.id in conceptos_auto_calculados or
                c.depende_de_concepto_id is not None
            )
            icono = "🔒" if es_auto else "✏️"
            print(f"   {icono} ID {c.id}: {c.nombre[:40]:40} - Auto-calculado: {es_auto}")
        
        print("\n✅ Verificación completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_concepto_attributes()
