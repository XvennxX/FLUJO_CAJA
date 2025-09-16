#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de depuración para VENTANILLA
"""

import os
import sys
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from sqlalchemy import text

def main():
    print("=== DEBUG VENTANILLA SYNC ===")
    
    db = SessionLocal()
    try:
        fecha_test = date(2025, 9, 10)
        print(f"📅 Fecha: {fecha_test}")
        
        # 1. Verificar estado actual
        print("\n1. Estado actual en BD:")
        
        # SUBTOTAL MOVIMIENTO PAGADURIA (ID 82)
        subtotal_82 = db.execute(text("""
            SELECT monto, descripcion FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        # VENTANILLA (ID 3)
        ventanilla_3 = db.execute(text("""
            SELECT monto, descripcion FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        if subtotal_82:
            print(f"   📊 SUBTOTAL MOVIMIENTO (ID 82): ${subtotal_82[0]} - {subtotal_82[1]}")
        else:
            print(f"   ❌ No se encontró SUBTOTAL MOVIMIENTO (ID 82)")
            
        if ventanilla_3:
            print(f"   🏪 VENTANILLA (ID 3): ${ventanilla_3[0]} - {ventanilla_3[1]}")
        else:
            print(f"   ❌ No se encontró VENTANILLA (ID 3)")
        
        # 2. Ejecutar SOLO el método de VENTANILLA
        print(f"\n2. Ejecutando _procesar_ventanilla_automatico...")
        service = DependenciasFlujoCajaService(db)
        
        ventanilla_updates = service._procesar_ventanilla_automatico(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   🔄 Updates retornados: {len(ventanilla_updates)}")
        for update in ventanilla_updates:
            print(f"   • {update}")
        
        # 3. Verificar estado después
        print(f"\n3. Estado después del procesamiento:")
        
        ventanilla_despues = db.execute(text("""
            SELECT monto, descripcion FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        if ventanilla_despues:
            print(f"   🏪 VENTANILLA después: ${ventanilla_despues[0]} - {ventanilla_despues[1]}")
        else:
            print(f"   ❌ VENTANILLA no encontrado después del procesamiento")
        
        # 4. Verificar directamente en el método
        print(f"\n4. Verificación directa del método...")
        
        # Query directa para SUBTOTAL MOVIMIENTO
        from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
        
        subtotal_directo = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 82,
            TransaccionFlujoCaja.cuenta_id == 1,
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).first()
        
        if subtotal_directo:
            print(f"   ✅ Query directa encuentra SUBTOTAL: ${subtotal_directo.monto}")
        else:
            print(f"   ❌ Query directa NO encuentra SUBTOTAL")
            
        # Query directa para VENTANILLA
        ventanilla_directo = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 3,
            TransaccionFlujoCaja.cuenta_id == 1,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).first()
        
        if ventanilla_directo:
            print(f"   ✅ Query directa encuentra VENTANILLA: ${ventanilla_directo.monto}")
        else:
            print(f"   ❌ Query directa NO encuentra VENTANILLA")
        
        # 5. Probar procesamiento completo
        print(f"\n5. Probando procesamiento completo...")
        
        resultados_completos = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📊 Tesorería: {len(resultados_completos['tesoreria'])} updates")
        print(f"   📊 Pagaduría: {len(resultados_completos['pagaduria'])} updates")
        print(f"   🔗 Cross-dashboard: {len(resultados_completos['cross_dashboard'])} updates")
        
        for update in resultados_completos['cross_dashboard']:
            if update.get('concepto_id') == 3:
                print(f"   🏪 VENTANILLA cross-update: {update}")
        
        # 6. Estado final
        print(f"\n6. Estado final:")
        
        ventanilla_final = db.execute(text("""
            SELECT monto, descripcion, auditoria FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        if ventanilla_final:
            print(f"   🏪 VENTANILLA final: ${ventanilla_final[0]}")
            print(f"   📝 Descripción: {ventanilla_final[1]}")
            if ventanilla_final[2]:
                auditoria = ventanilla_final[2]
                print(f"   📋 Última acción: {auditoria.get('accion', 'N/A')}")
        
        # Comparación final
        if subtotal_82 and ventanilla_final:
            if subtotal_82[0] == ventanilla_final[0]:
                print(f"\n✅ ÉXITO: VENTANILLA sincronizado con SUBTOTAL MOVIMIENTO")
            else:
                print(f"\n❌ FALLO: VENTANILLA ${ventanilla_final[0]} ≠ SUBTOTAL ${subtotal_82[0]}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
