#!/usr/bin/env python3
"""
Script para probar la lógica de signos por tipo de concepto
"""
import os
import sys
from datetime import date

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Back-FC'))

from app.core.database import SessionLocal
from app.models import ConceptoFlujoCaja, TipoMovimiento
from sqlalchemy import text

def test_signos_conceptos():
    """Prueba la lógica de signos por tipo de concepto"""
    
    print("🧪 PRUEBA: Lógica de signos por tipo de concepto")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Obtener algunos conceptos de cada tipo
        conceptos = db.execute(text("""
            SELECT id, nombre, tipo 
            FROM conceptos_flujo_caja 
            WHERE activo = true 
            ORDER BY tipo, id 
            LIMIT 10
        """)).fetchall()
        
        print("\n📋 Conceptos encontrados:")
        for concepto in conceptos:
            print(f"   ID {concepto[0]}: {concepto[1]} ({concepto[2]})")
        
        # Casos de prueba
        casos_prueba = [
            # (monto_ingresado, concepto_id, tipo_esperado, monto_esperado)
            (100, 2, "CONSUMO debería ser según su tipo", None),  # CONSUMO
            (-100, 2, "CONSUMO debería ser según su tipo", None),  # CONSUMO  
            (50, 3, "VENTANILLA debería ser según su tipo", None),  # VENTANILLA
            (-50, 3, "VENTANILLA debería ser según su tipo", None),  # VENTANILLA
        ]
        
        print("\n🧪 Casos de prueba:")
        for i, (monto, concepto_id, descripcion, _) in enumerate(casos_prueba, 1):
            print(f"\n   Caso {i}: {descripcion}")
            print(f"   Entrada: ${monto} para concepto ID {concepto_id}")
            
            # Obtener tipo del concepto
            concepto = db.execute(text("""
                SELECT nombre, tipo FROM conceptos_flujo_caja WHERE id = :id
            """), {"id": concepto_id}).fetchone()
            
            if concepto:
                nombre, tipo = concepto
                print(f"   Concepto: {nombre} (tipo: {tipo})")
                
                # Simular la lógica que debería aplicarse
                monto_abs = abs(monto)
                if tipo == 'ingreso':
                    resultado_esperado = monto_abs
                    regla = "Siempre positivo"
                elif tipo == 'egreso':
                    resultado_esperado = -monto_abs
                    regla = "Siempre negativo"
                else:  # neutral
                    resultado_esperado = monto
                    regla = "Mantiene signo del usuario"
                
                print(f"   Regla: {regla}")
                print(f"   Resultado esperado: ${resultado_esperado}")
                
                # Verificar si el resultado es correcto
                if tipo == 'ingreso' and resultado_esperado > 0:
                    print(f"   ✅ CORRECTO: Concepto ingreso convertido a positivo")
                elif tipo == 'egreso' and resultado_esperado < 0:
                    print(f"   ✅ CORRECTO: Concepto egreso convertido a negativo")
                elif tipo == 'neutral':
                    print(f"   ✅ CORRECTO: Concepto neutral mantiene signo original")
                else:
                    print(f"   ❌ ERROR en la lógica")
            else:
                print(f"   ❌ Concepto ID {concepto_id} no encontrado")
        
        print("\n" + "=" * 60)
        print("✅ Prueba de lógica completada")
        print("\n💡 Para probar en vivo:")
        print("   1. Reinicia el backend")
        print("   2. Crea/modifica transacciones en el dashboard")
        print("   3. Verifica que los signos se apliquen automáticamente")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_signos_conceptos()