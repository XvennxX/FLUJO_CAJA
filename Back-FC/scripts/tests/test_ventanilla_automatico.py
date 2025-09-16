#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para VENTANILLA = SUBTOTAL MOVIMIENTO PAGADURIA
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
    print("=== TEST VENTANILLA AUTOMATICO ===")
    print("🎯 Probando: VENTANILLA (ID 3) = SUBTOTAL MOVIMIENTO PAGADURIA (ID 82)")
    
    db = SessionLocal()
    try:
        fecha_test = datetime(2025, 9, 10).date()
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (3, 55, 56, 82)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Crear datos base para generar SUBTOTAL MOVIMIENTO PAGADURIA
        print("\n2. Creando datos base...")
        
        # Crear conceptos de movimiento para que se genere SUBTOTAL MOVIMIENTO
        concepto_ingreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=55,  # INGRESO (código I)
            cuenta_id=1,
            monto=Decimal('800.00'),
            descripcion="Test - INGRESO para VENTANILLA",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "ventanilla"}
        )
        
        concepto_egreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=56,  # EGRESO (código E)
            cuenta_id=1,
            monto=Decimal('300.00'),
            descripcion="Test - EGRESO para VENTANILLA",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "ventanilla"}
        )
        
        db.add_all([concepto_ingreso, concepto_egreso])
        db.commit()
        
        print(f"   ✅ INGRESO: ${concepto_ingreso.monto}")
        print(f"   ✅ EGRESO: ${concepto_egreso.monto}")
        
        # Calcular SUBTOTAL MOVIMIENTO esperado: 800 - 300 = 500 (I+ E-)
        subtotal_esperado = Decimal('800.00') - Decimal('300.00')
        print(f"   📊 SUBTOTAL MOVIMIENTO esperado: ${subtotal_esperado}")
        
        # 3. Verificar estado ANTES del procesamiento
        print("\n3. Estado ANTES del procesamiento...")
        
        # Verificar SUBTOTAL MOVIMIENTO
        subtotal_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 82
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        # Verificar VENTANILLA
        ventanilla_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 3
            AND area = 'tesoreria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_subtotal_antes, monto_subtotal_antes = subtotal_antes
        count_ventanilla_antes, monto_ventanilla_antes = ventanilla_antes
        
        print(f"   SUBTOTAL MOVIMIENTO antes: {count_subtotal_antes} registros, Total: ${monto_subtotal_antes}")
        print(f"   VENTANILLA antes: {count_ventanilla_antes} registros, Total: ${monto_ventanilla_antes}")
        
        # 4. Ejecutar procesamiento completo
        print("\n4. Ejecutando procesamiento completo...")
        service = DependenciasFlujoCajaService(db)
        
        # Usar el método completo que procesa ambos dashboards
        resultados = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        total_actualizaciones = len(resultados["tesoreria"]) + len(resultados["pagaduria"]) + len(resultados["cross_dashboard"])
        print(f"   📝 Actualizaciones totales: {total_actualizaciones}")
        print(f"   - Tesorería: {len(resultados['tesoreria'])}")
        print(f"   - Pagaduría: {len(resultados['pagaduria'])}")
        print(f"   - Cross-dashboard: {len(resultados['cross_dashboard'])}")
        
        # 5. Verificar resultados DESPUÉS del procesamiento
        print("\n5. Verificando resultados...")
        
        # Verificar SUBTOTAL MOVIMIENTO
        subtotal_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 82
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        # Verificar VENTANILLA
        ventanilla_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 3
            AND area = 'tesoreria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_subtotal_despues, monto_subtotal_despues = subtotal_despues
        count_ventanilla_despues, monto_ventanilla_despues = ventanilla_despues
        
        print(f"   SUBTOTAL MOVIMIENTO después: {count_subtotal_despues} registros, Total: ${monto_subtotal_despues}")
        print(f"   VENTANILLA después: {count_ventanilla_despues} registros, Total: ${monto_ventanilla_despues}")
        
        # 6. Validar resultados
        print("\n6. Validación de resultados...")
        
        exito_subtotal = (count_subtotal_despues > count_subtotal_antes and 
                         monto_subtotal_despues == subtotal_esperado)
        
        exito_ventanilla = (count_ventanilla_despues > count_ventanilla_antes and 
                           monto_ventanilla_despues == monto_subtotal_despues)
        
        if exito_subtotal:
            print(f"   ✅ SUBTOTAL MOVIMIENTO calculado correctamente: ${monto_subtotal_despues}")
        else:
            print(f"   ❌ SUBTOTAL MOVIMIENTO incorrecto: esperado ${subtotal_esperado}, obtenido ${monto_subtotal_despues}")
        
        if exito_ventanilla and monto_ventanilla_despues == subtotal_esperado:
            print(f"   ✅ VENTANILLA calculado correctamente: ${monto_ventanilla_despues}")
            print(f"   🎉 ¡SINCRONIZACIÓN EXITOSA! VENTANILLA = SUBTOTAL MOVIMIENTO")
        else:
            print(f"   ❌ VENTANILLA incorrecto: esperado ${monto_subtotal_despues}, obtenido ${monto_ventanilla_despues}")
        
        # 7. Mostrar detalles de cross-dashboard
        print(f"\n7. Detalles de actualizaciones cross-dashboard:")
        for update in resultados["cross_dashboard"]:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            area = update.get('area', 'N/A')
            
            print(f"   • [{concepto_id}] {concepto_nombre} ({area}): ${monto_nuevo}")
            
            if concepto_id == 3:  # VENTANILLA
                origen = update.get('origen', {})
                if origen:
                    print(f"     ↳ Origen: [{origen.get('concepto_id')}] {origen.get('concepto_nombre')}")
                    print(f"       Monto origen: ${origen.get('monto_origen')}")
        
        # 8. Verificar estado completo final
        print(f"\n8. Estado completo final:")
        estado_final = db.execute(text("""
            SELECT c.nombre, t.monto, t.area, t.descripcion
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.concepto_id IN (3, 55, 56, 82)
            AND t.cuenta_id = 1
            ORDER BY t.concepto_id
        """), {"fecha": fecha_test}).fetchall()
        
        for nombre, monto, area, desc in estado_final:
            print(f"   • {nombre} ({area}): ${monto}")
        
        # 9. Resultado final
        if exito_subtotal and exito_ventanilla:
            print(f"\n🎉 ¡TEST EXITOSO! La lógica VENTANILLA = SUBTOTAL MOVIMIENTO funciona correctamente")
        else:
            print(f"\n❌ Test falló. Revisar la lógica de sincronización.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
