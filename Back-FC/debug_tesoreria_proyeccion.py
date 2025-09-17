#!/usr/bin/env python3
"""
Script para diagnosticar por qué no funciona la proyección de Tesorería
SALDO FINAL CUENTAS ($300 viernes) → SALDO INICIAL (lunes)
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.core.database import get_db
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.services.dias_habiles_service import DiasHabilesService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from sqlalchemy.orm import Session

def debug_proyeccion_tesoreria():
    """Diagnosticar la proyección de Tesorería paso a paso"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        # Fechas específicas del problema
        viernes = date(2025, 9, 19)  # Hay SALDO FINAL CUENTAS = $300
        lunes = date(2025, 9, 22)    # Debería tener SALDO INICIAL = $300
        
        print(f"🔍 DIAGNÓSTICO PROYECCIÓN TESORERÍA")
        print(f"📅 Viernes: {viernes} → Lunes: {lunes}")
        print("=" * 60)
        
        # 1. Verificar SALDO FINAL CUENTAS del viernes
        print(f"1️⃣ VERIFICANDO SALDO FINAL CUENTAS del {viernes}:")
        saldos_finales = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == viernes,
            TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        for saldo in saldos_finales:
            print(f"   ✅ Cuenta {saldo.cuenta_id}: ${saldo.monto}")
            print(f"      Descripción: {saldo.descripcion}")
            print(f"      Área: {saldo.area.value}")
        
        if not saldos_finales:
            print(f"   ❌ NO se encontró SALDO FINAL CUENTAS para {viernes}")
            return
        
        # 2. Verificar días hábiles
        print(f"\n2️⃣ VERIFICANDO DÍAS HÁBILES:")
        dias_habiles_service = DiasHabilesService(db)
        proximo_dia = dias_habiles_service.proximo_dia_habil(viernes, incluir_fecha_actual=False)
        print(f"   📅 Próximo día hábil después del {viernes}: {proximo_dia}")
        
        # 3. Verificar SALDO INICIAL actual del lunes
        print(f"\n3️⃣ VERIFICANDO SALDO INICIAL del {lunes}:")
        saldos_iniciales = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        if saldos_iniciales:
            for saldo in saldos_iniciales:
                print(f"   📊 Cuenta {saldo.cuenta_id}: ${saldo.monto}")
                print(f"      Descripción: {saldo.descripcion}")
        else:
            print(f"   ❌ NO hay SALDO INICIAL para {lunes}")
        
        # 4. Simular la lógica de proyección manualmente
        print(f"\n4️⃣ SIMULANDO PROYECCIÓN MANUAL:")
        
        service = DependenciasFlujoCajaService(db)
        
        # Obtener todas las cuentas
        from app.models.cuentas_bancarias import CuentaBancaria
        cuentas = db.query(CuentaBancaria).all()
        cuentas_ids = [cuenta.id for cuenta in cuentas]
        
        print(f"   📋 Cuentas a procesar: {cuentas_ids}")
        
        for cuenta in cuentas_ids:
            print(f"\n   🔄 Procesando cuenta {cuenta}:")
            
            # Buscar SALDO FINAL CUENTAS del viernes
            saldo_final_cuentas = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == viernes,
                TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
                TransaccionFlujoCaja.cuenta_id == cuenta,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).first()
            
            if saldo_final_cuentas and saldo_final_cuentas.monto != 0:
                print(f"      ✅ SALDO FINAL CUENTAS encontrado: ${saldo_final_cuentas.monto}")
                
                # Verificar si ya existe SALDO INICIAL para el lunes
                saldo_inicial_existente = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == lunes,
                    TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
                    TransaccionFlujoCaja.cuenta_id == cuenta,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if saldo_inicial_existente:
                    print(f"      📊 SALDO INICIAL existente: ${saldo_inicial_existente.monto}")
                    print(f"      ⚡ Se ACTUALIZARÍA a: ${saldo_final_cuentas.monto}")
                else:
                    print(f"      ✨ Se CREARÍA nuevo SALDO INICIAL: ${saldo_final_cuentas.monto}")
                    
            else:
                print(f"      ❌ No hay SALDO FINAL CUENTAS o es $0")
        
        # 5. Ejecutar la proyección real
        print(f"\n5️⃣ EJECUTANDO PROYECCIÓN REAL:")
        try:
            resultado = service._procesar_dependencias_pagaduria(
                fecha=viernes,
                usuario_id=1,
                compania_id=1
            )
            print(f"   ✅ Proyección ejecutada. Resultado: {len(resultado)} actualizaciones")
            
            # Verificar resultado
            saldos_iniciales_nuevos = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == lunes,
                TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).all()
            
            print(f"\n   📊 SALDO INICIAL después de proyección:")
            for saldo in saldos_iniciales_nuevos:
                print(f"      Cuenta {saldo.cuenta_id}: ${saldo.monto}")
                if 'Auto-calculado' in str(saldo.descripcion):
                    print(f"      🚀 PROYECTADO desde viernes")
            
        except Exception as e:
            print(f"   ❌ Error en proyección: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    debug_proyeccion_tesoreria()