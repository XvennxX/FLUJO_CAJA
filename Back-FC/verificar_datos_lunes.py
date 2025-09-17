#!/usr/bin/env python3
"""
Script para verificar por qué no aparece SALDO INICIAL en el frontend del lunes
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
from sqlalchemy.orm import Session

def verificar_datos_lunes():
    """Verificar qué datos existen para el lunes 22 de septiembre"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        lunes = date(2025, 9, 22)
        
        print(f"🔍 VERIFICANDO DATOS PARA EL LUNES {lunes}")
        print("=" * 60)
        
        # 1. Verificar TODAS las transacciones de Tesorería para el lunes
        print(f"1️⃣ TODAS LAS TRANSACCIONES DE TESORERÍA DEL {lunes}:")
        transacciones_tesoreria = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        if transacciones_tesoreria:
            for t in transacciones_tesoreria:
                print(f"   📊 Concepto ID {t.concepto_id}: ${t.monto} (Cuenta {t.cuenta_id})")
                print(f"      Descripción: {t.descripcion}")
        else:
            print(f"   ❌ NO hay transacciones de Tesorería para {lunes}")
        
        # 2. Verificar específicamente SALDO INICIAL (ID 1)
        print(f"\n2️⃣ SALDO INICIAL (ID 1) DEL {lunes}:")
        saldos_iniciales = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        if saldos_iniciales:
            for saldo in saldos_iniciales:
                print(f"   ✅ Cuenta {saldo.cuenta_id}: ${saldo.monto}")
                print(f"      Descripción: {saldo.descripcion}")
                print(f"      Creado: {saldo.created_at}")
        else:
            print(f"   ❌ NO existe SALDO INICIAL para {lunes}")
        
        # 3. Verificar si existe pero con monto 0
        print(f"\n3️⃣ VERIFICANDO SALDOS INICIALES CON MONTO 0:")
        saldos_cero = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
            TransaccionFlujoCaja.monto == 0
        ).all()
        
        if saldos_cero:
            for saldo in saldos_cero:
                print(f"   ⚠️ Cuenta {saldo.cuenta_id}: ${saldo.monto} (CERO)")
                print(f"      Descripción: {saldo.descripcion}")
        else:
            print(f"   ✅ No hay saldos iniciales con monto 0")
        
        # 4. Verificar datos del viernes para comparar
        viernes = date(2025, 9, 19)
        print(f"\n4️⃣ SALDO FINAL CUENTAS DEL VIERNES {viernes} (para comparar):")
        saldos_finales_viernes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == viernes,
            TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        for saldo in saldos_finales_viernes:
            print(f"   📊 Cuenta {saldo.cuenta_id}: ${saldo.monto}")
        
        # 5. Verificar si el problema es que se eliminó la data proyectada
        print(f"\n5️⃣ BUSCANDO EVIDENCIA DE PROYECCIÓN ELIMINADA:")
        # Buscar transacciones con descripciones que indiquen proyección
        proyecciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.descripcion.like('%Auto-calculado%')
        ).all()
        
        if proyecciones:
            print(f"   🔍 Encontradas {len(proyecciones)} transacciones auto-calculadas:")
            for p in proyecciones:
                print(f"      Concepto {p.concepto_id}, Cuenta {p.cuenta_id}: ${p.monto}")
                print(f"      Desc: {p.descripcion}")
        else:
            print(f"   ❌ No se encontraron transacciones auto-calculadas")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    verificar_datos_lunes()