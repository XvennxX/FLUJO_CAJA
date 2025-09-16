#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que VENTANILLA se sincroniza automáticamente 
cuando se actualiza SUBTOTAL MOVIMIENTO PAGADURIA via trigger automático
"""

import os
import sys
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST: TRIGGER AUTOMÁTICO VENTANILLA ===")
    print("🎯 Verificando que VENTANILLA se sincroniza automáticamente cuando se actualiza SUBTOTAL MOVIMIENTO")
    
    db = SessionLocal()
    try:
        fecha_test = date(2025, 9, 10)
        print(f"📅 Fecha: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (3, 55, 56, 82)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Crear datos base que generen SUBTOTAL MOVIMIENTO
        print("\n2. Creando datos base...")
        
        # Crear conceptos que formarán SUBTOTAL MOVIMIENTO (ID 82)
        concepto_ingreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=55,  # INGRESO (código I)
            cuenta_id=1,
            monto=Decimal('800.00'),
            descripcion="Test - Trigger INGRESO",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "trigger_ventanilla", "tipo": "concepto_base"}
        )
        
        concepto_egreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=56,  # EGRESO (código E)
            cuenta_id=1,
            monto=Decimal('300.00'),
            descripcion="Test - Trigger EGRESO",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "trigger_ventanilla", "tipo": "concepto_base"}
        )
        
        db.add_all([concepto_ingreso, concepto_egreso])
        db.commit()
        
        subtotal_esperado = Decimal('800.00') - Decimal('300.00')  # 500
        print(f"   ✅ INGRESO: ${concepto_ingreso.monto} (+)")
        print(f"   ✅ EGRESO: ${concepto_egreso.monto} (-)")
        print(f"   📊 SUBTOTAL MOVIMIENTO esperado: ${subtotal_esperado}")
        
        # 3. Verificar estado ANTES del procesamiento
        print(f"\n3. Estado ANTES del procesamiento pagaduría...")
        
        ventanilla_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        count_ventanilla_antes, monto_ventanilla_antes = ventanilla_antes
        print(f"   🏪 VENTANILLA antes: {count_ventanilla_antes} registros, Total: ${monto_ventanilla_antes}")
        
        # 4. Ejecutar SOLO procesamiento de pagaduría (que debería disparar trigger)
        print(f"\n4. Ejecutando procesamiento de pagaduría (con trigger automático)...")
        service = DependenciasFlujoCajaService(db)
        
        # Ejecutar SOLO el procesamiento de pagaduría que debería incluir el trigger
        resultados_pagaduria = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📊 Resultados pagaduría: {len(resultados_pagaduria)} actualizaciones")
        
        # 5. Verificar si se procesó SUBTOTAL MOVIMIENTO y se disparó trigger
        subtotal_procesado = False
        ventanilla_trigger = False
        
        for resultado in resultados_pagaduria:
            concepto_id = resultado.get('concepto_id')
            concepto_nombre = resultado.get('concepto_nombre', 'N/A')
            monto_nuevo = resultado.get('monto_nuevo', 0)
            
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            if concepto_id == 82:  # SUBTOTAL MOVIMIENTO
                subtotal_procesado = True
                print(f"     ✅ SUBTOTAL MOVIMIENTO procesado: ${monto_nuevo}")
                
            if concepto_id == 3:  # VENTANILLA
                ventanilla_trigger = True
                tipo_trigger = resultado.get('tipo_trigger')
                print(f"     🔥 TRIGGER VENTANILLA detectado: ${monto_nuevo}")
                if tipo_trigger:
                    print(f"     📝 Tipo trigger: {tipo_trigger}")
        
        # 6. Verificar estado DESPUÉS del procesamiento
        print(f"\n6. Estado DESPUÉS del procesamiento...")
        
        subtotal_despues = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        ventanilla_despues = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        monto_subtotal_final = subtotal_despues[0] if subtotal_despues else Decimal('0')
        monto_ventanilla_final = ventanilla_despues[0] if ventanilla_despues else Decimal('0')
        
        print(f"   📊 SUBTOTAL MOVIMIENTO final: ${monto_subtotal_final}")
        print(f"   🏪 VENTANILLA final: ${monto_ventanilla_final}")
        
        # 7. Validación del trigger automático
        print(f"\n7. Validación del trigger automático...")
        
        trigger_exitoso = (
            subtotal_procesado and 
            ventanilla_trigger and
            monto_subtotal_final == subtotal_esperado and
            monto_ventanilla_final == monto_subtotal_final
        )
        
        if trigger_exitoso:
            print(f"   🎉 ¡TRIGGER AUTOMÁTICO EXITOSO!")
            print(f"   ✅ SUBTOTAL MOVIMIENTO calculado: ${monto_subtotal_final}")
            print(f"   ✅ VENTANILLA sincronizado automáticamente: ${monto_ventanilla_final}")
            print(f"   ✨ La sincronización ahora es automática al procesar pagaduría")
        else:
            print(f"   ❌ TRIGGER AUTOMÁTICO FALLÓ:")
            print(f"   • SUBTOTAL procesado: {subtotal_procesado}")
            print(f"   • VENTANILLA trigger: {ventanilla_trigger}")
            print(f"   • Subtotal correcto: {monto_subtotal_final == subtotal_esperado}")
            print(f"   • Sincronización correcta: {monto_ventanilla_final == monto_subtotal_final}")
        
        # 8. Test de modificación subsecuente
        print(f"\n8. Test: Modificando conceptos base para verificar re-sincronización...")
        
        # Cambiar el INGRESO
        concepto_ingreso.monto = Decimal('1200.00')
        concepto_ingreso.descripcion = "Test - Trigger INGRESO modificado"
        db.commit()
        
        nuevo_subtotal_esperado = Decimal('1200.00') - Decimal('300.00')  # 900
        print(f"   🔄 INGRESO cambiado: $800 → $1200")
        print(f"   📊 Nuevo SUBTOTAL esperado: ${nuevo_subtotal_esperado}")
        
        # Re-procesar pagaduría
        resultados_modificacion = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        # Verificar nueva sincronización
        subtotal_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        ventanilla_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        monto_subtotal_nuevo = subtotal_final[0] if subtotal_final else Decimal('0')
        monto_ventanilla_nuevo = ventanilla_final[0] if ventanilla_final else Decimal('0')
        
        print(f"   📊 SUBTOTAL MOVIMIENTO nuevo: ${monto_subtotal_nuevo}")
        print(f"   🏪 VENTANILLA nuevo: ${monto_ventanilla_nuevo}")
        
        re_sincronizacion_exitosa = (
            monto_subtotal_nuevo == nuevo_subtotal_esperado and
            monto_ventanilla_nuevo == monto_subtotal_nuevo
        )
        
        if re_sincronizacion_exitosa:
            print(f"   🎉 ¡RE-SINCRONIZACIÓN AUTOMÁTICA EXITOSA!")
        else:
            print(f"   ❌ Re-sincronización falló")
        
        # 9. Resultado final
        if trigger_exitoso and re_sincronizacion_exitosa:
            print(f"\n🚀 ¡ÉXITO TOTAL! El trigger automático funciona perfectamente:")
            print(f"   ✅ VENTANILLA se sincroniza automáticamente al procesar pagaduría")
            print(f"   ✅ Los cambios en conceptos base disparan la sincronización automática")
            print(f"   ✅ No necesitas tocar tesorería para que VENTANILLA se actualice")
        else:
            print(f"\n❌ El trigger automático necesita ajustes")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
