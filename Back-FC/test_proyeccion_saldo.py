#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la lógica de proyección SALDO TOTAL EN BANCOS → SALDO DÍA ANTERIOR
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models import TransaccionFlujoCaja
from datetime import date, timedelta
from sqlalchemy import text

def test_proyeccion_saldo_dia_anterior():
    print("🧪 === PRUEBA: PROYECCIÓN SALDO TOTAL EN BANCOS → SALDO DÍA ANTERIOR ===")
    
    db = SessionLocal()
    try:
        fecha_hoy = date(2025, 9, 16)
        fecha_manana = fecha_hoy + timedelta(days=1)
        
        print(f"📅 Fecha HOY: {fecha_hoy}")
        print(f"📅 Fecha MAÑANA: {fecha_manana}")
        
        # 1. Verificar SALDO TOTAL EN BANCOS de hoy
        print("\n1️⃣ Estado actual SALDO TOTAL EN BANCOS (ID 85):")
        saldo_total_hoy = db.execute(text("""
            SELECT cuenta_id, monto, descripcion 
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 85
            ORDER BY cuenta_id
        """), {"fecha": fecha_hoy}).fetchall()
        
        if saldo_total_hoy:
            for row in saldo_total_hoy:
                print(f"   💰 Cuenta {row[0]}: ${row[1]} - {row[2]}")
        else:
            print("   ❌ No se encontró SALDO TOTAL EN BANCOS para hoy")
        
        # 2. Verificar SALDO DÍA ANTERIOR de mañana (antes de ejecutar)
        print(f"\n2️⃣ Estado actual SALDO DÍA ANTERIOR (ID 54) para {fecha_manana}:")
        saldo_anterior_manana_antes = db.execute(text("""
            SELECT cuenta_id, monto, descripcion 
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 54
            ORDER BY cuenta_id
        """), {"fecha": fecha_manana}).fetchall()
        
        if saldo_anterior_manana_antes:
            for row in saldo_anterior_manana_antes:
                print(f"   📊 Cuenta {row[0]}: ${row[1]} - {row[2]}")
        else:
            print("   ❌ No existe SALDO DÍA ANTERIOR para mañana (se debe crear)")
        
        # 3. Ejecutar el procesamiento de dependencias para HOY (esto debería crear la proyección)
        print(f"\n3️⃣ Ejecutando procesamiento de dependencias para {fecha_hoy}...")
        service = DependenciasFlujoCajaService(db)
        
        resultados = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_hoy,
            concepto_modificado_id=85,  # Simular que SALDO TOTAL EN BANCOS cambió
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        total_updates = (
            len(resultados.get("tesoreria", [])) + 
            len(resultados.get("pagaduria", [])) + 
            len(resultados.get("cross_dashboard", []))
        )
        print(f"   ✅ Procesamiento completado: {total_updates} actualizaciones")
        
        # 4. Verificar SALDO DÍA ANTERIOR de mañana (después de ejecutar)
        print(f"\n4️⃣ Estado DESPUÉS - SALDO DÍA ANTERIOR (ID 54) para {fecha_manana}:")
        saldo_anterior_manana_despues = db.execute(text("""
            SELECT cuenta_id, monto, descripcion 
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha AND concepto_id = 54
            ORDER BY cuenta_id
        """), {"fecha": fecha_manana}).fetchall()
        
        if saldo_anterior_manana_despues:
            for row in saldo_anterior_manana_despues:
                print(f"   🚀 Cuenta {row[0]}: ${row[1]} - {row[2]}")
        else:
            print("   ❌ PROBLEMA: Aún no existe SALDO DÍA ANTERIOR para mañana")
        
        # 5. Verificar que los montos coincidan
        print(f"\n5️⃣ Verificación de coherencia:")
        for saldo_hoy in saldo_total_hoy:
            cuenta_id = saldo_hoy[0]
            monto_hoy = saldo_hoy[1]
            
            # Buscar el monto correspondiente para mañana
            monto_manana = None
            for saldo_manana in saldo_anterior_manana_despues:
                if saldo_manana[0] == cuenta_id:
                    monto_manana = saldo_manana[1]
                    break
            
            if monto_manana is not None:
                if monto_hoy == monto_manana:
                    print(f"   ✅ Cuenta {cuenta_id}: HOY ${monto_hoy} == MAÑANA ${monto_manana}")
                else:
                    print(f"   ❌ Cuenta {cuenta_id}: HOY ${monto_hoy} != MAÑANA ${monto_manana}")
            else:
                print(f"   ⚠️ Cuenta {cuenta_id}: HOY ${monto_hoy} pero no hay proyección para mañana")
    
    except Exception as e:
        print(f"💥 Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_proyeccion_saldo_dia_anterior()