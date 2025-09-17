#!/usr/bin/env python3
"""
Debug: Verificar tipos de conceptos ID 5 e ID 6
"""
import os
import sys
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import ConceptoFlujoCaja, TransaccionFlujoCaja, TipoMovimiento
from sqlalchemy import text

def main():
    print("🔍 DEBUG: Verificando tipos de conceptos ID 5 e ID 6")
    
    db = SessionLocal()
    try:
        # 1. Verificar conceptos en BD
        print("\n1. Información de conceptos:")
        
        concepto_5 = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 5).first()
        concepto_6 = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == 6).first()
        
        if concepto_5:
            print(f"   ID 5: {concepto_5.nombre} - Tipo: {concepto_5.tipo} ({concepto_5.tipo.value if hasattr(concepto_5.tipo, 'value') else concepto_5.tipo})")
        else:
            print("   ❌ Concepto ID 5 no encontrado")
            
        if concepto_6:
            print(f"   ID 6: {concepto_6.nombre} - Tipo: {concepto_6.tipo} ({concepto_6.tipo.value if hasattr(concepto_6.tipo, 'value') else concepto_6.tipo})")
        else:
            print("   ❌ Concepto ID 6 no encontrado")
        
        # 2. Verificar transacciones existentes
        print(f"\n2. Transacciones del día 2025-09-16:")
        
        fecha_test = date(2025, 9, 16)
        
        trans_5 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 5,
            TransaccionFlujoCaja.fecha == fecha_test
        ).first()
        
        trans_6 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 6,
            TransaccionFlujoCaja.fecha == fecha_test
        ).first()
        
        if trans_5:
            print(f"   ID 5: Monto guardado = {trans_5.monto} (descripción: {trans_5.descripcion})")
        else:
            print("   ℹ️ No hay transacción ID 5 para hoy")
            
        if trans_6:
            print(f"   ID 6: Monto guardado = {trans_6.monto} (descripción: {trans_6.descripcion})")
        else:
            print("   ℹ️ No hay transacción ID 6 para hoy")
        
        # 3. Calcular suma esperada vs real
        if trans_5 and trans_6:
            suma_actual = trans_5.monto + trans_6.monto
            print(f"\n3. Cálculo:")
            print(f"   {trans_5.monto} + {trans_6.monto} = {suma_actual}")
            
            # ¿Cómo debería ser?
            if concepto_5.tipo == TipoMovimiento.ingreso and concepto_6.tipo == TipoMovimiento.egreso:
                print(f"   ✅ Esperado: +300 + (-200) = +100")
                if suma_actual == 100:
                    print(f"   ✅ CORRECTO: La suma es correcta")
                else:
                    print(f"   ❌ ERROR: La suma debería ser +100, no {suma_actual}")
            else:
                print(f"   ⚠️ Tipos de concepto inesperados")
        
        # 4. Probar la función de signo directamente
        print(f"\n4. Prueba directa de función de signos:")
        from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
        
        service = TransaccionFlujoCajaService(db)
        
        # Simular ingreso de +300 en concepto 5 (debería mantenerse +300)
        resultado_5_pos = service._aplicar_signo_por_tipo_concepto(300, 5)
        print(f"   Concepto 5 (+300): {resultado_5_pos}")
        
        # Simular ingreso de +200 en concepto 6 (debería convertirse a -200)
        resultado_6_pos = service._aplicar_signo_por_tipo_concepto(200, 6)
        print(f"   Concepto 6 (+200): {resultado_6_pos}")
        
        suma_esperada = resultado_5_pos + resultado_6_pos
        print(f"   Suma con función: {resultado_5_pos} + {resultado_6_pos} = {suma_esperada}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()