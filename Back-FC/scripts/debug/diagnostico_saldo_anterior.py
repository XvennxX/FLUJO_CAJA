#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico: ¿De dónde vienen los valores de SALDO DIA ANTERIOR?
"""

import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from sqlalchemy import text

def main():
    print("=== DIAGNÓSTICO SALDO DIA ANTERIOR ===")
    print("🔍 Investigando origen de valores en SALDO DIA ANTERIOR")
    
    db = SessionLocal()
    try:
        fecha_hoy = datetime(2025, 9, 10).date()
        fecha_ayer = fecha_hoy - timedelta(days=1)
        
        print(f"📅 Fecha hoy: {fecha_hoy}")
        print(f"📅 Fecha ayer: {fecha_ayer}")
        
        # 1. Verificar SALDO DIA ANTERIOR de hoy
        print(f"\n1. 📊 SALDO DIA ANTERIOR del {fecha_hoy}:")
        saldos_hoy = db.execute(text("""
            SELECT t.cuenta_id, t.monto, t.descripcion, 
                   t.auditoria, t.created_at, t.updated_at
            FROM transacciones_flujo_caja t
            WHERE t.fecha = :fecha
            AND t.concepto_id = 54
            AND t.area = 'pagaduria'
            ORDER BY t.cuenta_id
        """), {"fecha": fecha_hoy}).fetchall()
        
        if saldos_hoy:
            for cuenta_id, monto, desc, auditoria, created, updated in saldos_hoy:
                print(f"   • Cuenta {cuenta_id}: ${monto}")
                print(f"     📋 Descripción: {desc}")
                print(f"     🕐 Creado: {created}")
                print(f"     🕑 Actualizado: {updated}")
                print(f"     📝 Auditoría: {auditoria}")
                print()
        else:
            print(f"   ❌ No hay SALDO DIA ANTERIOR para {fecha_hoy}")
        
        # 2. Verificar SALDO TOTAL EN BANCOS de ayer
        print(f"\n2. 🏦 SALDO TOTAL EN BANCOS del {fecha_ayer}:")
        saldos_ayer = db.execute(text("""
            SELECT t.cuenta_id, t.monto, t.descripcion, 
                   t.auditoria, t.created_at
            FROM transacciones_flujo_caja t
            WHERE t.fecha = :fecha
            AND t.concepto_id = 85
            AND t.area = 'pagaduria'
            ORDER BY t.cuenta_id
        """), {"fecha": fecha_ayer}).fetchall()
        
        if saldos_ayer:
            for cuenta_id, monto, desc, auditoria, created in saldos_ayer:
                print(f"   • Cuenta {cuenta_id}: ${monto}")
                print(f"     📋 Descripción: {desc}")
                print(f"     🕐 Creado: {created}")
                print(f"     📝 Auditoría: {auditoria}")
                print()
        else:
            print(f"   ❌ No hay SALDO TOTAL EN BANCOS para {fecha_ayer}")
        
        # 3. Buscar SALDO TOTAL EN BANCOS en otras fechas recientes
        print(f"\n3. 🔍 Buscando SALDO TOTAL EN BANCOS en los últimos 5 días:")
        for i in range(1, 6):
            fecha_busqueda = fecha_hoy - timedelta(days=i)
            saldos_fecha = db.execute(text("""
                SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 85
                AND area = 'pagaduria'
            """), {"fecha": fecha_busqueda}).fetchone()
            
            count, total = saldos_fecha
            if count > 0:
                print(f"   📅 {fecha_busqueda}: {count} registros, Total: ${total}")
            else:
                print(f"   📅 {fecha_busqueda}: Sin registros")
        
        # 4. Verificar todas las transacciones de concepto 54 (historial completo)
        print(f"\n4. 📚 Historial completo de SALDO DIA ANTERIOR:")
        historial_completo = db.execute(text("""
            SELECT t.fecha, t.cuenta_id, t.monto, 
                   t.descripcion, t.created_at, t.auditoria
            FROM transacciones_flujo_caja t
            WHERE t.concepto_id = 54
            AND t.area = 'pagaduria'
            ORDER BY t.fecha DESC, t.cuenta_id
            LIMIT 10
        """)).fetchall()
        
        if historial_completo:
            for fecha, cuenta_id, monto, desc, created, auditoria in historial_completo:
                print(f"   📅 {fecha} - Cuenta {cuenta_id}: ${monto}")
                print(f"     📋 {desc}")
                print(f"     🕐 {created}")
                if auditoria:
                    print(f"     📝 Auditoría: {auditoria}")
                print()
        
        # 5. Verificar si hay lógica duplicada que esté creando estos valores
        print(f"\n5. 🔎 Buscando posibles fuentes de SALDO DIA ANTERIOR:")
        
        # Buscar por descripción
        descripciones = db.execute(text("""
            SELECT DISTINCT descripcion, COUNT(*) as cantidad
            FROM transacciones_flujo_caja
            WHERE concepto_id = 54
            AND area = 'pagaduria'
            GROUP BY descripcion
            ORDER BY cantidad DESC
        """)).fetchall()
        
        print("   📋 Tipos de descripciones encontradas:")
        for desc, cantidad in descripciones:
            print(f"     • '{desc}': {cantidad} veces")
        
        # 6. Verificar diferencias con tesorería
        print(f"\n6. 🏢 Comparación con área de tesorería:")
        tesoreria_saldos = db.execute(text("""
            SELECT fecha, COUNT(*), SUM(monto) as total
            FROM transacciones_flujo_caja
            WHERE concepto_id = 54
            AND area = 'tesoreria'
            AND fecha >= :fecha_inicio
            GROUP BY fecha
            ORDER BY fecha DESC
        """), {"fecha_inicio": fecha_hoy - timedelta(days=5)}).fetchall()
        
        if tesoreria_saldos:
            print("   📊 SALDO DIA ANTERIOR en tesorería:")
            for fecha, count, total in tesoreria_saldos:
                print(f"     📅 {fecha}: {count} registros, Total: ${total}")
        else:
            print("   ❌ No hay SALDO DIA ANTERIOR en tesorería")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
