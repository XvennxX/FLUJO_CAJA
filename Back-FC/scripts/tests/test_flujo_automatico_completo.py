#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico: Verificar que cambios en valores base 
automáticamente recalculan SUBTOTAL MOVIMIENTO y VENTANILLA
"""

import os
import sys
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST: CAMBIO VALORES BASE → AUTO-CALCULA SUBTOTAL → SYNC VENTANILLA ===")
    print("🎯 Simulando el flujo real del usuario")
    
    db = SessionLocal()
    try:
        fecha_test = date(2025, 9, 10)
        print(f"📅 Fecha: {fecha_test}")
        
        # 1. LIMPIAR datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (3, 55, 56, 82)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. CREAR valores base iniciales
        print("\n2. Creando valores base iniciales...")
        
        ingreso_inicial = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=55,  # INGRESO (código I)
            cuenta_id=1,
            monto=Decimal('500.00'),
            descripcion="Test - INGRESO inicial",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "valores_base", "fase": "inicial"}
        )
        
        egreso_inicial = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=56,  # EGRESO (código E)
            cuenta_id=1,
            monto=Decimal('100.00'),
            descripcion="Test - EGRESO inicial",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "valores_base", "fase": "inicial"}
        )
        
        db.add_all([ingreso_inicial, egreso_inicial])
        db.commit()
        
        print(f"   💰 INGRESO inicial: ${ingreso_inicial.monto}")
        print(f"   💰 EGRESO inicial: ${egreso_inicial.monto}")
        
        # 3. EJECUTAR procesamiento pagaduría para auto-calcular SUBTOTAL
        print("\n3. Ejecutando procesamiento pagaduría (auto-calcula SUBTOTAL)...")
        service = DependenciasFlujoCajaService(db)
        
        # Este es el método que se ejecuta cuando cambias valores base
        resultados_pagaduria = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📊 Actualizaciones pagaduría: {len(resultados_pagaduria)}")
        
        # Buscar si se actualizó SUBTOTAL MOVIMIENTO
        subtotal_actualizado = None
        ventanilla_trigger = None
        
        for update in resultados_pagaduria:
            if update.get("concepto_id") == 82:  # SUBTOTAL MOVIMIENTO
                subtotal_actualizado = update
                print(f"   ✅ SUBTOTAL MOVIMIENTO auto-calculado: ${update.get('monto_nuevo')}")
            
            if update.get("concepto_id") == 3:  # VENTANILLA
                ventanilla_trigger = update
                print(f"   🏪 VENTANILLA trigger encontrado: ${update.get('monto_nuevo')}")
                print(f"       Tipo: {update.get('tipo_trigger')}")
        
        # 4. VERIFICAR estado después del procesamiento
        print("\n4. Verificando estado en BD...")
        
        # SUBTOTAL MOVIMIENTO
        subtotal_bd = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        # VENTANILLA
        ventanilla_bd = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        monto_subtotal_bd = subtotal_bd[0] if subtotal_bd else None
        monto_ventanilla_bd = ventanilla_bd[0] if ventanilla_bd else None
        
        print(f"   📊 SUBTOTAL MOVIMIENTO en BD: ${monto_subtotal_bd}")
        print(f"   🏪 VENTANILLA en BD: ${monto_ventanilla_bd}")
        
        # 5. CALCULAR valores esperados
        esperado_subtotal = Decimal('500.00') - Decimal('100.00')  # 400 (I+ E-)
        
        print(f"\n5. Validación:")
        print(f"   Esperado SUBTOTAL: ${esperado_subtotal}")
        
        # Validar SUBTOTAL
        if monto_subtotal_bd == esperado_subtotal:
            print(f"   ✅ SUBTOTAL MOVIMIENTO correcto: ${monto_subtotal_bd}")
        else:
            print(f"   ❌ SUBTOTAL MOVIMIENTO incorrecto: esperado ${esperado_subtotal}, obtenido ${monto_subtotal_bd}")
        
        # Validar VENTANILLA = SUBTOTAL
        if monto_ventanilla_bd == monto_subtotal_bd == esperado_subtotal:
            print(f"   ✅ VENTANILLA sincronizado automáticamente: ${monto_ventanilla_bd}")
            print(f"   🎉 ¡TRIGGER AUTOMÁTICO FUNCIONANDO!")
        else:
            print(f"   ❌ VENTANILLA no sincronizado: esperado ${monto_subtotal_bd}, obtenido ${monto_ventanilla_bd}")
        
        # 6. CAMBIAR valores base y probar de nuevo
        print(f"\n6. SEGUNDA PRUEBA: Cambiando valores base...")
        
        # Cambiar INGRESO de 500 a 800
        ingreso_inicial.monto = Decimal('800.00')
        ingreso_inicial.descripcion = "Test - INGRESO modificado"
        ingreso_inicial.auditoria = {"test": "valores_base", "fase": "modificacion"}
        db.commit()
        
        print(f"   💰 INGRESO cambiado: $500 → $800")
        
        nuevo_esperado = Decimal('800.00') - Decimal('100.00')  # 700
        print(f"   📊 Nuevo SUBTOTAL esperado: ${nuevo_esperado}")
        
        # Ejecutar procesamiento de nuevo
        print("\n7. Re-ejecutando procesamiento...")
        
        resultados_segunda = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📊 Segunda ronda - actualizaciones: {len(resultados_segunda)}")
        
        for update in resultados_segunda:
            if update.get("concepto_id") == 82:
                print(f"   ✅ SUBTOTAL re-calculado: ${update.get('monto_nuevo')}")
            if update.get("concepto_id") == 3:
                print(f"   🏪 VENTANILLA re-sincronizado: ${update.get('monto_nuevo')}")
        
        # 8. VERIFICAR estado final
        print("\n8. Estado final:")
        
        subtotal_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 82 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        ventanilla_final = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 3 AND cuenta_id = 1
        """), {"fecha": fecha_test}).fetchone()
        
        monto_subtotal_final = subtotal_final[0] if subtotal_final else None
        monto_ventanilla_final = ventanilla_final[0] if ventanilla_final else None
        
        print(f"   📊 SUBTOTAL final: ${monto_subtotal_final}")
        print(f"   🏪 VENTANILLA final: ${monto_ventanilla_final}")
        
        # RESULTADO FINAL
        if (monto_subtotal_final == nuevo_esperado and 
            monto_ventanilla_final == monto_subtotal_final):
            print(f"\n🎉 ¡ÉXITO TOTAL! El flujo automático funciona:")
            print(f"   1. Cambios en valores base → Auto-calcula SUBTOTAL")
            print(f"   2. SUBTOTAL actualizado → Dispara trigger automático")
            print(f"   3. VENTANILLA sincronizado automáticamente")
            print(f"   ✨ El usuario ya NO necesita tocar tesorería para que se actualice VENTANILLA")
        else:
            print(f"\n❌ FALLO: El flujo automático no está completo")
            print(f"   Revisar la lógica del trigger automático")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
