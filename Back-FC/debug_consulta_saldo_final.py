#!/usr/bin/env python3
"""
Script para diagnosticar exactamente qué valor devuelve la consulta de SALDO FINAL CUENTAS
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.cuentas_bancarias import CuentaBancaria
from sqlalchemy.orm import Session

def debug_consulta_saldo_final():
    """Debugear exactamente qué devuelve la consulta de SALDO FINAL CUENTAS"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        viernes = date(2025, 9, 19)
        
        print(f"🔍 DEBUGEANDO CONSULTA SALDO FINAL CUENTAS DEL {viernes}")
        print("=" * 70)
        
        # Obtener todas las cuentas como lo hace el código real
        cuentas = db.query(CuentaBancaria).all()
        cuentas_ids = [cuenta.id for cuenta in cuentas]
        
        print(f"📋 Total cuentas: {len(cuentas_ids)}")
        print(f"📋 IDs de cuentas: {cuentas_ids[:10]}..." if len(cuentas_ids) > 10 else f"📋 IDs de cuentas: {cuentas_ids}")
        
        print(f"\n🔍 CONSULTANDO SALDO FINAL CUENTAS PARA CADA CUENTA:")
        
        for cuenta in cuentas_ids[:5]:  # Solo las primeras 5 para no saturar
            print(f"\n   🔄 Procesando cuenta {cuenta}:")
            
            # Exactamente la misma consulta que usa el código
            saldo_final_cuentas = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == viernes,
                TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
                TransaccionFlujoCaja.cuenta_id == cuenta,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).first()
            
            if saldo_final_cuentas:
                print(f"      ✅ ENCONTRADO: ${saldo_final_cuentas.monto}")
                print(f"      📄 Descripción: {saldo_final_cuentas.descripcion}")
                print(f"      🕐 Creado: {saldo_final_cuentas.created_at}")
                
                # Verificar la condición del código
                if saldo_final_cuentas.monto != 0:
                    print(f"      ✅ CONDICIÓN CUMPLIDA: monto != 0")
                else:
                    print(f"      ❌ CONDICIÓN FALLÓ: monto es 0")
            else:
                print(f"      ❌ NO ENCONTRADO para cuenta {cuenta}")
        
        # Verificar específicamente las cuentas que sabemos que tienen datos
        print(f"\n🎯 VERIFICANDO CUENTAS ESPECÍFICAS CON DATOS:")
        cuentas_conocidas = [1, 4]  # Sabemos que estas tienen $300 y $30
        
        for cuenta in cuentas_conocidas:
            print(f"\n   🎯 Cuenta {cuenta}:")
            
            # Todas las transacciones de SALDO FINAL CUENTAS para esa cuenta
            todas_saldo_final = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == viernes,
                TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
                TransaccionFlujoCaja.cuenta_id == cuenta,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).all()
            
            print(f"      📊 Encontrados {len(todas_saldo_final)} registros:")
            for i, saldo in enumerate(todas_saldo_final):
                print(f"         {i+1}. ${saldo.monto} - {saldo.descripcion[:50]}...")
            
            # La consulta .first()
            primer_resultado = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == viernes,
                TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
                TransaccionFlujoCaja.cuenta_id == cuenta,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).first()
            
            if primer_resultado:
                print(f"      🎯 .first() devuelve: ${primer_resultado.monto}")
                print(f"      📝 ID: {primer_resultado.id}")
                print(f"      🗂️ Orden por defecto (created_at): {primer_resultado.created_at}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    debug_consulta_saldo_final()