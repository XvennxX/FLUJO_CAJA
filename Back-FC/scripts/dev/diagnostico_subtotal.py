"""
Script para diagnosticar el problema del SUB-TOTAL TESORERÍA
"""
import sys
import os
from decimal import Decimal
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.schemas.flujo_caja import AreaTransaccionSchema

def diagnosticar_subtotal():
    """Diagnosticar por qué el SUB-TOTAL está incorrecto"""
    db = SessionLocal()
    try:
        service = DependenciasFlujoCajaService(db)
        
        # Fecha de hoy
        fecha_hoy = date.today()
        
        print("🔍 DIAGNÓSTICO: SUB-TOTAL TESORERÍA")
        print("=" * 80)
        
        # 1. Obtener el concepto SUB-TOTAL
        subtotal = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SUB-TOTAL TESORERÍA'
        ).first()
        
        if not subtotal:
            print("❌ No se encontró el concepto SUB-TOTAL TESORERÍA")
            return
        
        print(f"\n📋 Concepto SUB-TOTAL TESORERÍA:")
        print(f"   ID: {subtotal.id}")
        print(f"   Código: {subtotal.codigo}")
        print(f"   Fórmula: {subtotal.formula_dependencia}")
        
        # 2. Obtener transacciones del día para los conceptos de la fórmula
        # Extraer IDs de la fórmula
        formula = subtotal.formula_dependencia
        if formula and formula.startswith('SUMA('):
            ids_str = formula[5:-1]  # Quitar "SUMA(" y ")"
            conceptos_ids = [int(x.strip()) for x in ids_str.split(',')]
            
            print(f"\n📊 Conceptos en la fórmula: {len(conceptos_ids)} conceptos")
            print(f"   IDs: {conceptos_ids[:10]}... (mostrando primeros 10)")
            
            # Obtener transacciones
            print(f"\n💰 Transacciones para fecha {fecha_hoy}:")
            print("-" * 80)
            
            total_manual = Decimal('0.00')
            
            for concepto_id in conceptos_ids:
                concepto = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
                transaccion = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_hoy,
                    TransaccionFlujoCaja.concepto_id == concepto_id,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if transaccion:
                    total_manual += transaccion.monto
                    print(f"   [{concepto.codigo or 'N':1}] {concepto.nombre:40} ${transaccion.monto:>12.2f}")
            
            print("-" * 80)
            print(f"   TOTAL CALCULADO MANUALMENTE:  ${total_manual:>12.2f}")
            
            # 3. Ver qué tiene actualmente el SUB-TOTAL en la BD
            subtotal_transaccion = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_hoy,
                TransaccionFlujoCaja.concepto_id == subtotal.id,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).first()
            
            if subtotal_transaccion:
                print(f"\n   VALOR ACTUAL EN BD:             ${subtotal_transaccion.monto:>12.2f}")
                
                if subtotal_transaccion.monto != total_manual:
                    print(f"\n   ⚠️ ¡DISCREPANCIA DETECTADA!")
                    print(f"      Esperado: ${total_manual:>12.2f}")
                    print(f"      Real:     ${subtotal_transaccion.monto:>12.2f}")
                else:
                    print(f"\n   ✅ El valor en BD coincide con el cálculo manual")
            else:
                print(f"\n   ⚠️ No existe transacción de SUB-TOTAL para hoy")
            
            # 4. Probar la aplicación de signo
            print(f"\n🔧 Prueba de aplicación de signo:")
            print(f"   Monto calculado: ${total_manual}")
            print(f"   Código concepto: {subtotal.codigo or 'None'}")
            
            monto_con_signo = service._aplicar_signo_por_tipo_concepto(total_manual, subtotal)
            print(f"   Después de aplicar signo: ${monto_con_signo}")
            
            if total_manual < 0 and monto_con_signo > 0:
                print(f"\n   ❌ ERROR: El signo se invirtió incorrectamente")
            elif monto_con_signo == total_manual:
                print(f"\n   ✅ El signo se mantuvo correctamente")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    diagnosticar_subtotal()
