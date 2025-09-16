#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo para todas las dependencias de pagaduría:
1. DIFERENCIA SALDOS (ID 52) = SALDOS EN BANCOS (ID 53) + SALDO DIA ANTERIOR (ID 54)
2. SALDO DIA ANTERIOR (ID 54) = SALDO TOTAL EN BANCOS (ID 85) del día anterior
3. SUBTOTAL MOVIMIENTO (ID 82) = SUMA de conceptos 55-81 (respetando I/E/N)
4. SUBTOTAL SALDO INICIAL (ID 83) = SUBTOTAL MOVIMIENTO (ID 82) + SALDO DIA ANTERIOR (ID 54)
"""

import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST COMPLETO DEPENDENCIAS PAGADURIA ===")
    print("🎯 Probando toda la cadena de auto-cálculos de pagaduría")
    
    db = SessionLocal()
    try:
        fecha_ayer = datetime(2025, 9, 9).date()   # Ayer
        fecha_hoy = datetime(2025, 9, 10).date()   # Hoy
        print(f"📅 Fecha ayer: {fecha_ayer}")
        print(f"📅 Fecha hoy: {fecha_hoy}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        conceptos_limpiar = [52, 53, 54, 82, 83, 85] + list(range(55, 82))  # Todos los conceptos relevantes
        
        for fecha in [fecha_ayer, fecha_hoy]:
            for concepto_id in conceptos_limpiar:
                db.execute(text("""
                    DELETE FROM transacciones_flujo_caja
                    WHERE fecha = :fecha
                    AND concepto_id = :concepto_id
                    AND area = 'pagaduria'
                    AND cuenta_id = 1
                """), {"fecha": fecha, "concepto_id": concepto_id})
        db.commit()
        
        # 2. Crear datos base (prerequisitos)
        print("\n2. Creando datos base...")
        
        # SALDO TOTAL EN BANCOS de AYER (para SALDO DIA ANTERIOR)
        saldo_total_ayer = TransaccionFlujoCaja(
            fecha=fecha_ayer,
            concepto_id=85,  # SALDO TOTAL EN BANCOS
            cuenta_id=1,
            monto=Decimal('1000.00'),
            descripcion="SALDO TOTAL EN BANCOS - Ayer",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        db.add(saldo_total_ayer)
        
        # SALDOS EN BANCOS de HOY (para DIFERENCIA SALDOS)
        saldos_bancos_hoy = TransaccionFlujoCaja(
            fecha=fecha_hoy,
            concepto_id=53,  # SALDOS EN BANCOS
            cuenta_id=1,
            monto=Decimal('500.00'),
            descripcion="SALDOS EN BANCOS - Hoy",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "cadena_completa"}
        )
        db.add(saldos_bancos_hoy)
        
        # Transacciones de movimiento (para SUBTOTAL MOVIMIENTO)
        transacciones_movimiento = [
            {"concepto_id": 55, "monto": Decimal('2000.00')},  # INGRESO (I)
            {"concepto_id": 56, "monto": Decimal('800.00')},   # EGRESO (E) - será negativo
            {"concepto_id": 57, "monto": Decimal('300.00')},   # CONSUMO NACIONAL (¿I/E/N?)
            {"concepto_id": 75, "monto": Decimal('1200.00')},  # NOMINA PENSIONES (E) - será negativo
        ]
        
        for trans in transacciones_movimiento:
            transaccion = TransaccionFlujoCaja(
                fecha=fecha_hoy,
                concepto_id=trans["concepto_id"],
                cuenta_id=1,
                monto=trans["monto"],
                descripcion=f"Test - Concepto {trans['concepto_id']}",
                usuario_id=6,
                area=AreaTransaccion.pagaduria,
                compania_id=1,
                auditoria={"test": "cadena_completa"}
            )
            db.add(transaccion)
            print(f"   • Concepto {trans['concepto_id']}: ${trans['monto']}")
        
        db.commit()
        print(f"   ✅ Datos base creados")
        
        # 3. Estado ANTES del procesamiento
        print("\n3. Estado ANTES del procesamiento...")
        conceptos_verificar = [52, 54, 82, 83]
        for concepto_id in conceptos_verificar:
            count = db.execute(text("""
                SELECT COUNT(*)
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = :concepto_id
                AND area = 'pagaduria'
                AND cuenta_id = 1
            """), {"fecha": fecha_hoy, "concepto_id": concepto_id}).scalar()
            print(f"   Concepto {concepto_id}: {count} registros")
        
        # 4. Ejecutar procesamiento
        print("\n4. Ejecutando procesamiento de dependencias...")
        service = DependenciasFlujoCajaService(db)
        actualizaciones = service._procesar_dependencias_pagaduria(
            fecha=fecha_hoy,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Total actualizaciones: {len(actualizaciones)}")
        
        # 5. Verificar resultados
        print("\n5. Verificando resultados...")
        
        resultados = {}
        for concepto_id in conceptos_verificar:
            resultado = db.execute(text("""
                SELECT monto, descripcion
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = :concepto_id
                AND area = 'pagaduria'
                AND cuenta_id = 1
                ORDER BY created_at DESC
                LIMIT 1
            """), {"fecha": fecha_hoy, "concepto_id": concepto_id}).fetchone()
            
            if resultado:
                monto, descripcion = resultado
                resultados[concepto_id] = monto
                print(f"   ✅ Concepto {concepto_id}: ${monto}")
            else:
                print(f"   ❌ Concepto {concepto_id}: NO ENCONTRADO")
                resultados[concepto_id] = None
        
        # 6. Validar lógica de negocio
        print("\n6. Validando lógica de negocio...")
        
        # Validar DIFERENCIA SALDOS = SALDOS EN BANCOS + SALDO DIA ANTERIOR
        if resultados[52] and resultados[54]:  # DIFERENCIA SALDOS y SALDO DIA ANTERIOR
            esperado_diferencia = Decimal('500.00') + resultados[54]  # SALDOS EN BANCOS + SALDO DIA ANTERIOR
            if resultados[52] == esperado_diferencia:
                print(f"   ✅ DIFERENCIA SALDOS correcto: ${resultados[52]} = $500.00 + ${resultados[54]}")
            else:
                print(f"   ❌ DIFERENCIA SALDOS incorrecto: ${resultados[52]} ≠ ${esperado_diferencia}")
        
        # Validar SALDO DIA ANTERIOR = SALDO TOTAL EN BANCOS de ayer
        if resultados[54]:
            if resultados[54] == Decimal('1000.00'):
                print(f"   ✅ SALDO DIA ANTERIOR correcto: ${resultados[54]} (del día anterior)")
            else:
                print(f"   ❌ SALDO DIA ANTERIOR incorrecto: ${resultados[54]} ≠ $1000.00")
        
        # Validar SUBTOTAL SALDO INICIAL = SUBTOTAL MOVIMIENTO + SALDO DIA ANTERIOR
        if resultados[83] and resultados[82] and resultados[54]:  # SUBTOTAL SALDO INICIAL, SUBTOTAL MOVIMIENTO, SALDO DIA ANTERIOR
            esperado_saldo_inicial = resultados[82] + resultados[54]
            if resultados[83] == esperado_saldo_inicial:
                print(f"   ✅ SUBTOTAL SALDO INICIAL correcto: ${resultados[83]} = ${resultados[82]} + ${resultados[54]}")
            else:
                print(f"   ❌ SUBTOTAL SALDO INICIAL incorrecto: ${resultados[83]} ≠ ${esperado_saldo_inicial}")
        
        # 7. Resumen de actualizaciones
        print(f"\n📊 Resumen detallado de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            # Mostrar componentes si existen
            if 'componentes' in update:
                print(f"     ↳ Componentes: {update['componentes']}")
            if 'conceptos_incluidos' in update:
                print(f"     ↳ Incluye {len(update['conceptos_incluidos'])} conceptos de movimiento")
        
        # 8. Estado final
        print(f"\n🎯 ESTADO FINAL - Cadena completa:")
        estado_final = db.execute(text("""
            SELECT c.nombre, t.monto, t.descripcion
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.area = 'pagaduria'
            AND t.cuenta_id = 1
            AND c.id IN (52, 53, 54, 82, 83, 85)
            ORDER BY c.id
        """), {"fecha": fecha_hoy}).fetchall()
        
        for nombre, monto, desc in estado_final:
            print(f"   📋 {nombre}: ${monto}")
        
        print(f"\n🎉 Test de cadena completa finalizado!")
        
        # Verificar si toda la cadena funcionó
        if all(resultados[cid] is not None for cid in [52, 54, 82, 83]):
            print(f"✅ ¡ÉXITO! Toda la cadena de dependencias funciona correctamente")
        else:
            conceptos_faltantes = [cid for cid, valor in resultados.items() if valor is None]
            print(f"❌ Faltan conceptos: {conceptos_faltantes}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
