#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar por qué VENTANILLA no se sincroniza en tiempo real
"""

import os
import sys
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from sqlalchemy import text

def main():
    print("=== DIAGNÓSTICO: VENTANILLA NO SE SINCRONIZA ===")
    
    db = SessionLocal()
    try:
        fecha_test = date(2025, 9, 10)
        print(f"📅 Fecha: {fecha_test}")
        
        # 1. Verificar estado actual exacto
        print("\n1. Estado actual en BD:")
        
        subtotal_82 = db.execute(text("""
            SELECT id, monto, descripcion, auditoria FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        ventanilla_3 = db.execute(text("""
            SELECT id, monto, descripcion, auditoria FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        print(f"   📊 SUBTOTAL MOVIMIENTO (ID 82):")
        if subtotal_82:
            print(f"      ID: {subtotal_82[0]}, Monto: ${subtotal_82[1]}")
            print(f"      Descripción: {subtotal_82[2]}")
        
        print(f"   🏪 VENTANILLA (ID 3):")
        if ventanilla_3:
            print(f"      ID: {ventanilla_3[0]}, Monto: ${ventanilla_3[1]}")
            print(f"      Descripción: {ventanilla_3[2]}")
        
        # 2. Forzar sincronización manual
        print(f"\n2. Forzando sincronización manual...")
        service = DependenciasFlujoCajaService(db)
        
        print("   🔄 Ejecutando procesar_dependencias_completas_ambos_dashboards...")
        resultados = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📊 Cross-dashboard updates: {len(resultados['cross_dashboard'])}")
        for update in resultados['cross_dashboard']:
            if update.get('concepto_id') == 3:
                print(f"   🏪 VENTANILLA update encontrado:")
                print(f"      Monto nuevo: ${update.get('monto_nuevo')}")
                print(f"      Origen: {update.get('origen', {})}")
        
        # 3. Verificar estado después de la sincronización
        print(f"\n3. Estado DESPUÉS de sincronización:")
        
        ventanilla_despues = db.execute(text("""
            SELECT id, monto, descripcion FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        if ventanilla_despues:
            print(f"   🏪 VENTANILLA después: ID {ventanilla_despues[0]}, Monto: ${ventanilla_despues[1]}")
            print(f"      Descripción: {ventanilla_despues[2]}")
        
        # 4. Comparación y diagnóstico
        if subtotal_82 and ventanilla_despues:
            monto_subtotal = subtotal_82[1]
            monto_ventanilla = ventanilla_despues[1]
            
            print(f"\n4. Diagnóstico:")
            print(f"   SUBTOTAL MOVIMIENTO: ${monto_subtotal}")
            print(f"   VENTANILLA:          ${monto_ventanilla}")
            
            if monto_subtotal == monto_ventanilla:
                print(f"   ✅ ¡SINCRONIZACIÓN EXITOSA!")
            else:
                print(f"   ❌ PROBLEMA: Los valores no coinciden")
                print(f"   🔍 Diferencia: ${abs(monto_subtotal - monto_ventanilla)}")
                
                # 5. Investigar por qué no se sincronizó
                print(f"\n5. Investigando el problema...")
                
                # Verificar si el método específico funciona
                print("   🔄 Ejecutando SOLO _procesar_ventanilla_automatico...")
                ventanilla_updates = service._procesar_ventanilla_automatico(
                    fecha=fecha_test,
                    cuenta_id=1,
                    compania_id=1,
                    usuario_id=6
                )
                
                print(f"   📝 Updates retornados: {len(ventanilla_updates)}")
                for update in ventanilla_updates:
                    print(f"      {update}")
                
                # Verificar estado final
                ventanilla_final = db.execute(text("""
                    SELECT monto FROM transacciones_flujo_caja
                    WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
                """), {"fecha": fecha_test}).fetchone()
                
                if ventanilla_final:
                    print(f"   🏪 VENTANILLA final: ${ventanilla_final[0]}")
                    
                    if ventanilla_final[0] == monto_subtotal:
                        print(f"   ✅ ¡El método específico SÍ funcionó!")
                        print(f"   💡 Problema: El procesamiento completo no ejecutó las dependencias cruzadas")
                    else:
                        print(f"   ❌ El método específico tampoco funcionó")
        
        # 6. Verificar logs de la última ejecución
        print(f"\n6. Verificando logs...")
        
        # Verificar si hay registros de auditoría recientes
        auditoria_reciente = db.execute(text("""
            SELECT auditoria, updated_at FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
            ORDER BY updated_at DESC
            LIMIT 1
        """), {"fecha": fecha_test}).fetchone()
        
        if auditoria_reciente and auditoria_reciente[0]:
            print(f"   📋 Última actualización: {auditoria_reciente[1]}")
            # La auditoría puede ser string o dict
            auditoria = auditoria_reciente[0]
            if isinstance(auditoria, str):
                print(f"   📝 Auditoría (string): {auditoria}")
            else:
                print(f"   📝 Última acción: {auditoria.get('accion', 'N/A')}")
                if 'timestamp' in auditoria:
                    print(f"   🕐 Timestamp: {auditoria['timestamp']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
