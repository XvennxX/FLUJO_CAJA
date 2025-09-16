#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo para SALDO TOTAL EN BANCOS = SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA
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
    print("=== TEST SALDO TOTAL EN BANCOS ===")
    print("🎯 Probando: SALDO TOTAL EN BANCOS (ID 85) = SUBTOTAL SALDO INICIAL (ID 83) + MOVIMIENTO TESORERIA (ID 84)")
    
    db = SessionLocal()
    try:
        fecha_test = datetime(2025, 9, 10).date()
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (50, 54, 55, 56, 82, 83, 84, 85)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Configurar datos base para la cadena completa
        print("\n2. Configurando datos base...")
        
        # Crear SUB-TOTAL TESORERÍA (necesario para MOVIMIENTO TESORERIA)
        subtotal_tesoreria_monto = Decimal('1000.00')
        subtotal_tesoreria = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=50,  # SUB-TOTAL TESORERÍA
            cuenta_id=1,
            monto=subtotal_tesoreria_monto,
            descripcion="Test - SUB-TOTAL TESORERÍA",
            usuario_id=6,
            area=AreaTransaccion.tesoreria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        
        # Crear algunos conceptos de movimiento (para SUBTOTAL MOVIMIENTO)
        concepto_ingreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=55,  # INGRESO (código I)
            cuenta_id=1,
            monto=Decimal('500.00'),
            descripcion="Test - INGRESO",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        
        concepto_egreso = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=56,  # EGRESO (código E)
            cuenta_id=1,
            monto=Decimal('200.00'),
            descripcion="Test - EGRESO",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        
        # Crear SALDO DIA ANTERIOR manualmente para simplificar
        saldo_anterior_monto = Decimal('300.00')
        saldo_anterior = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=54,  # SALDO DIA ANTERIOR
            cuenta_id=1,
            monto=saldo_anterior_monto,
            descripcion="Test - SALDO DIA ANTERIOR",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        
        db.add_all([subtotal_tesoreria, concepto_ingreso, concepto_egreso, saldo_anterior])
        db.commit()
        
        print(f"   ✅ SUB-TOTAL TESORERÍA: ${subtotal_tesoreria_monto}")
        print(f"   ✅ INGRESO: ${concepto_ingreso.monto}")
        print(f"   ✅ EGRESO: ${concepto_egreso.monto}")
        print(f"   ✅ SALDO DIA ANTERIOR: ${saldo_anterior_monto}")
        
        # 3. Calcular valores esperados
        print("\n3. Calculando valores esperados...")
        
        # SUBTOTAL MOVIMIENTO = INGRESO(+) + EGRESO(-) = 500 + (-200) = 300
        subtotal_movimiento_esperado = Decimal('500.00') - Decimal('200.00')  # I(+) E(-)
        
        # SUBTOTAL SALDO INICIAL = SUBTOTAL MOVIMIENTO + SALDO DIA ANTERIOR = 300 + 300 = 600
        subtotal_saldo_inicial_esperado = subtotal_movimiento_esperado + saldo_anterior_monto
        
        # MOVIMIENTO TESORERIA = SUB-TOTAL TESORERÍA = 1000
        movimiento_tesoreria_esperado = subtotal_tesoreria_monto
        
        # SALDO TOTAL EN BANCOS = SUBTOTAL SALDO INICIAL + MOVIMIENTO TESORERIA = 600 + 1000 = 1600
        saldo_total_esperado = subtotal_saldo_inicial_esperado + movimiento_tesoreria_esperado
        
        print(f"   📊 SUBTOTAL MOVIMIENTO esperado: ${subtotal_movimiento_esperado}")
        print(f"   📊 SUBTOTAL SALDO INICIAL esperado: ${subtotal_saldo_inicial_esperado}")
        print(f"   📊 MOVIMIENTO TESORERIA esperado: ${movimiento_tesoreria_esperado}")
        print(f"   📊 SALDO TOTAL EN BANCOS esperado: ${saldo_total_esperado}")
        
        # 4. Verificar estado ANTES del procesamiento
        print("\n4. Estado ANTES del procesamiento...")
        for concepto_id, nombre in [(82, "SUBTOTAL MOVIMIENTO"), (83, "SUBTOTAL SALDO INICIAL"), 
                                   (84, "MOVIMIENTO TESORERIA"), (85, "SALDO TOTAL EN BANCOS")]:
            count = db.execute(text("""
                SELECT COUNT(*) FROM transacciones_flujo_caja
                WHERE fecha = :fecha AND concepto_id = :concepto_id 
                AND area = 'pagaduria' AND cuenta_id = 1
            """), {"fecha": fecha_test, "concepto_id": concepto_id}).scalar()
            print(f"   {nombre}: {count} registros")
        
        # 5. Ejecutar procesamiento
        print("\n5. Ejecutando procesamiento de dependencias...")
        service = DependenciasFlujoCajaService(db)
        actualizaciones = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Actualizaciones realizadas: {len(actualizaciones)}")
        
        # 6. Verificar resultados
        print("\n6. Verificando resultados...")
        
        resultados = {}
        for concepto_id, nombre in [(82, "SUBTOTAL MOVIMIENTO"), (83, "SUBTOTAL SALDO INICIAL"), 
                                   (84, "MOVIMIENTO TESORERIA"), (85, "SALDO TOTAL EN BANCOS")]:
            monto = db.execute(text("""
                SELECT COALESCE(SUM(monto), 0) FROM transacciones_flujo_caja
                WHERE fecha = :fecha AND concepto_id = :concepto_id 
                AND area = 'pagaduria' AND cuenta_id = 1
            """), {"fecha": fecha_test, "concepto_id": concepto_id}).scalar()
            
            resultados[concepto_id] = monto
            print(f"   • {nombre}: ${monto}")
        
        # 7. Validar cada resultado
        print("\n7. Validación de resultados...")
        
        validaciones = [
            (82, "SUBTOTAL MOVIMIENTO", resultados[82], subtotal_movimiento_esperado),
            (83, "SUBTOTAL SALDO INICIAL", resultados[83], subtotal_saldo_inicial_esperado),
            (84, "MOVIMIENTO TESORERIA", resultados[84], movimiento_tesoreria_esperado),
            (85, "SALDO TOTAL EN BANCOS", resultados[85], saldo_total_esperado)
        ]
        
        todas_correctas = True
        for concepto_id, nombre, obtenido, esperado in validaciones:
            es_correcto = obtenido == esperado
            estado = "✅" if es_correcto else "❌"
            print(f"   {estado} {nombre}: ${obtenido} {'=' if es_correcto else '≠'} ${esperado}")
            
            if not es_correcto:
                todas_correctas = False
        
        # 8. Resultado final
        print(f"\n8. Resultado final:")
        if todas_correctas:
            print(f"   🎉 ¡ÉXITO TOTAL! Toda la cadena de dependencias funciona correctamente")
            print(f"   💰 SALDO TOTAL EN BANCOS final: ${resultados[85]}")
        else:
            print(f"   ❌ Algunas validaciones fallaron")
        
        # 9. Mostrar resumen de actualizaciones
        print(f"\n9. Resumen de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            # Mostrar componentes si existen
            componentes = update.get('componentes')
            if componentes:
                print(f"     ↳ Componentes:")
                for key, value in componentes.items():
                    print(f"       - {key}: ${value}")
        
        # 10. Test de modificación en cascada
        print(f"\n10. Test de modificación en cascada...")
        print(f"    Modificando INGRESO de $500 a $800...")
        
        concepto_ingreso.monto = Decimal('800.00')
        db.commit()
        
        # Re-ejecutar procesamiento
        actualizaciones2 = service._procesar_dependencias_pagaduria(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        # Verificar nuevo SALDO TOTAL
        nuevo_saldo_total = db.execute(text("""
            SELECT COALESCE(SUM(monto), 0) FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 85 
            AND area = 'pagaduria' AND cuenta_id = 1
        """), {"fecha": fecha_test, "concepto_id": 85}).scalar()
        
        # Calcular nuevo valor esperado: 800 - 200 + 300 + 1000 = 1900
        nuevo_esperado = Decimal('800.00') - Decimal('200.00') + saldo_anterior_monto + subtotal_tesoreria_monto
        
        if nuevo_saldo_total == nuevo_esperado:
            print(f"    🎉 Modificación en cascada exitosa!")
            print(f"    💰 Nuevo SALDO TOTAL EN BANCOS: ${nuevo_saldo_total} = ${nuevo_esperado}")
        else:
            print(f"    ❌ Modificación en cascada falló: esperado ${nuevo_esperado}, obtenido ${nuevo_saldo_total}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
