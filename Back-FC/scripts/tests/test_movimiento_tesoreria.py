#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para MOVIMIENTO TESORERIA = SUB-TOTAL TESORERÍA
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST MOVIMIENTO TESORERIA ===")
    print("🎯 Probando: MOVIMIENTO TESORERIA (ID 84) = SUB-TOTAL TESORERÍA (ID 50)")
    
    db = SessionLocal()
    try:
        fecha_test = datetime(2025, 9, 10).date()
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (50, 84)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Crear SUB-TOTAL TESORERÍA en área tesorería
        print("\n2. Creando SUB-TOTAL TESORERÍA...")
        
        monto_subtotal = Decimal('1500.00')
        
        subtotal_tesoreria = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=50,  # SUB-TOTAL TESORERÍA
            cuenta_id=1,
            monto=monto_subtotal,
            descripcion="Test - SUB-TOTAL TESORERÍA",
            usuario_id=6,
            area=AreaTransaccion.tesoreria,  # En área tesorería
            compania_id=1,
            auditoria={"test": "movimiento_tesoreria"}
        )
        
        db.add(subtotal_tesoreria)
        db.commit()
        print(f"   ✅ SUB-TOTAL TESORERÍA creado en área 'tesoreria': ${monto_subtotal}")
        
        # 3. Verificar estado ANTES del procesamiento
        print("\n3. Estado ANTES del procesamiento...")
        movimiento_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 84
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_antes, monto_antes = movimiento_antes
        print(f"   MOVIMIENTO TESORERIA antes: {count_antes} registros, Total: ${monto_antes}")
        
        # 4. Ejecutar procesamiento
        print("\n4. Ejecutando procesamiento de dependencias...")
        service = DependenciasFlujoCajaService(db)
        actualizaciones = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Actualizaciones realizadas: {len(actualizaciones)}")
        
        # 5. Verificar resultado
        print("\n5. Verificando resultado...")
        movimiento_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 84
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_despues, monto_despues = movimiento_despues
        print(f"   MOVIMIENTO TESORERIA después: {count_despues} registros, Total: ${monto_despues}")
        
        # 6. Validar resultado
        if count_despues > count_antes and monto_despues == monto_subtotal:
            print(f"\n🎉 ¡ÉXITO! MOVIMIENTO TESORERIA calculado correctamente")
            print(f"   💰 Resultado: ${monto_despues} = ${monto_subtotal} (SUB-TOTAL TESORERÍA)")
            
            # Mostrar detalles de la transacción creada
            detalles = db.execute(text("""
                SELECT monto, descripcion, auditoria, created_at, area
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 84
                AND cuenta_id = 1
                ORDER BY created_at DESC
                LIMIT 1
            """), {"fecha": fecha_test}).fetchone()
            
            if detalles:
                monto, desc, auditoria, created_at, area = detalles
                print(f"      💰 Monto: ${monto}")
                print(f"      📋 Descripción: {desc}")
                print(f"      🏢 Área: {area}")
                print(f"      ⏰ Creado: {created_at}")
                
        else:
            print(f"\n❌ ERROR:")
            print(f"   Esperado: ${monto_subtotal}")
            print(f"   Obtenido: ${monto_despues}")
            print(f"   Registros antes: {count_antes}, después: {count_despues}")
        
        # 7. Mostrar resumen de actualizaciones
        print(f"\n📊 Resumen de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            # Mostrar detalles específicos del MOVIMIENTO TESORERIA
            if concepto_id == 84:
                origen = update.get('origen', {})
                if origen:
                    print(f"     ↳ Origen: [{origen.get('concepto_id')}] {origen.get('concepto_nombre')}")
                    print(f"       Área origen: {origen.get('area_origen')}")
                    print(f"       Monto origen: ${origen.get('monto_origen')}")
        
        # 8. Verificar estado completo
        print(f"\n🔍 Estado completo:")
        estado_completo = db.execute(text("""
            SELECT c.nombre, t.monto, t.area, t.descripcion
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.concepto_id IN (50, 84)
            AND t.cuenta_id = 1
            ORDER BY t.concepto_id, t.area
        """), {"fecha": fecha_test}).fetchall()
        
        for nombre, monto, area, desc in estado_completo:
            print(f"   • {nombre} ({area}): ${monto} - {desc}")
        
        # 9. Test de actualización - modificar SUB-TOTAL TESORERÍA
        print(f"\n9. Test de auto-recálculo...")
        nuevo_monto = Decimal('2000.00')
        subtotal_tesoreria.monto = nuevo_monto
        subtotal_tesoreria.descripcion = "Test - SUB-TOTAL TESORERÍA MODIFICADO"
        db.commit()
        
        print(f"   📝 SUB-TOTAL TESORERÍA modificado a: ${nuevo_monto}")
        
        # Re-ejecutar procesamiento
        actualizaciones2 = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        # Verificar nuevo resultado
        movimiento_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 84
            AND area = 'pagaduria'
            AND cuenta_id = 1
            LIMIT 1
        """), {"fecha": fecha_test}).scalar()
        
        if movimiento_final == nuevo_monto:
            print(f"   🎉 Auto-recálculo exitoso: MOVIMIENTO TESORERIA = ${movimiento_final}")
        else:
            print(f"   ❌ Auto-recálculo falló: esperado ${nuevo_monto}, obtenido ${movimiento_final}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
