"""
Script para probar el recálculo automático y aplicación de signos correctos
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService

def test_aplicar_signo():
    """Probar la aplicación de signos según el código del concepto"""
    db = SessionLocal()
    try:
        service = DependenciasFlujoCajaService(db)
        
        print("🧪 Probando aplicación de signos según código de concepto\n")
        print("=" * 70)
        
        # Obtener algunos conceptos de ejemplo
        conceptos = db.query(ConceptoFlujoCaja).limit(15).all()
        
        for concepto in conceptos:
            print(f"\n📋 Concepto: {concepto.nombre}")
            print(f"   ID: {concepto.id}")
            print(f"   Código: {concepto.codigo}")
            print(f"   Área: {concepto.area}")
            
            # Probar con monto positivo
            monto_positivo = Decimal('1000.00')
            resultado_positivo = service._aplicar_signo_por_tipo_concepto(monto_positivo, concepto)
            
            # Probar con monto negativo
            monto_negativo = Decimal('-1000.00')
            resultado_negativo = service._aplicar_signo_por_tipo_concepto(monto_negativo, concepto)
            
            print(f"\n   💰 Monto positivo (1000.00):")
            print(f"      Resultado: {resultado_positivo}")
            
            print(f"   💸 Monto negativo (-1000.00):")
            print(f"      Resultado: {resultado_negativo}")
            
            # Explicar la lógica
            if concepto.codigo == "I":
                print(f"   ✅ INGRESO: Siempre positivo")
            elif concepto.codigo == "E":
                print(f"   ✅ EGRESO: Siempre negativo")
            elif concepto.codigo == "N":
                print(f"   ✅ NEUTRAL: Mantiene el signo")
            else:
                print(f"   ⚠️ Código '{concepto.codigo}': Mantiene el signo")
        
        print("\n" + "=" * 70)
        print("✅ Prueba completada exitosamente\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_aplicar_signo()
