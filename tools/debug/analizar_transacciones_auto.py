#!/usr/bin/env python3
"""
Script para analizar las transacciones auto-calculadas del lunes
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path
import json

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from sqlalchemy.orm import Session

def analizar_transacciones_auto_calculadas():
    """Analizar las transacciones auto-calculadas del lunes que tienen $0"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        lunes = date(2025, 9, 22)
        
        print(f"🔍 ANALIZANDO TRANSACCIONES AUTO-CALCULADAS DEL {lunes}")
        print("=" * 70)
        
        # Buscar SALDO INICIAL con descripción auto-calculada
        saldos_iniciales_auto = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
            TransaccionFlujoCaja.descripcion.like('%Auto-calculado%')
        ).all()
        
        print(f"📊 SALDO INICIAL auto-calculados encontrados: {len(saldos_iniciales_auto)}")
        
        for i, saldo in enumerate(saldos_iniciales_auto):
            print(f"\n   {i+1}. CUENTA {saldo.cuenta_id}:")
            print(f"      💰 Monto: ${saldo.monto}")
            print(f"      📝 Descripción: {saldo.descripcion}")
            print(f"      🕐 Creado: {saldo.created_at}")
            print(f"      🆔 ID: {saldo.id}")
            
            # Analizar la auditoría si existe
            if saldo.auditoria:
                try:
                    auditoria = json.loads(saldo.auditoria) if isinstance(saldo.auditoria, str) else saldo.auditoria
                    print(f"      📋 Auditoría:")
                    if 'origen' in auditoria:
                        origen = auditoria['origen']
                        print(f"         🎯 Origen: {origen.get('concepto_origen_nombre')} = ${origen.get('monto_origen')}")
                        print(f"         📅 Fecha origen: {origen.get('fecha_origen')}")
                    if 'accion' in auditoria:
                        print(f"         🔧 Acción: {auditoria['accion']}")
                    if 'tipo' in auditoria:
                        print(f"         📂 Tipo: {auditoria['tipo']}")
                except Exception as e:
                    print(f"      ❌ Error parseando auditoría: {e}")
        
        # Buscar si hay múltiples transacciones SALDO INICIAL para las mismas cuentas
        print(f"\n🔍 VERIFICANDO SI HAY MÚLTIPLES SALDO INICIAL:")
        
        for cuenta in [1, 4]:
            todos_saldo_inicial = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == lunes,
                TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
                TransaccionFlujoCaja.cuenta_id == cuenta,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).order_by(TransaccionFlujoCaja.created_at).all()
            
            print(f"\n   📊 Cuenta {cuenta} - Total SALDO INICIAL: {len(todos_saldo_inicial)}")
            for j, s in enumerate(todos_saldo_inicial):
                print(f"      {j+1}. ${s.monto} - {s.created_at} - {s.descripcion[:50]}...")
                
            if len(todos_saldo_inicial) > 1:
                print(f"      ⚠️ DUPLICADOS DETECTADOS - esto puede causar problemas")
        
        # Verificar si hay lógica que resetee a 0
        print(f"\n🔍 BUSCANDO OTRAS LÓGICAS QUE PUEDAN RESETEAR:")
        
        # Buscar transacciones creadas después de las auto-calculadas
        todas_transacciones_lunes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).order_by(TransaccionFlujoCaja.created_at).all()
        
        print(f"   📊 Total transacciones Tesorería del {lunes}: {len(todas_transacciones_lunes)}")
        print(f"   📅 Rango de creación: {todas_transacciones_lunes[0].created_at} → {todas_transacciones_lunes[-1].created_at}")
        
        # Mostrar solo las últimas creadas
        print(f"\n   🕐 ÚLTIMAS 5 TRANSACCIONES CREADAS:")
        for t in todas_transacciones_lunes[-5:]:
            print(f"      {t.created_at} - Concepto {t.concepto_id}, Cuenta {t.cuenta_id}: ${t.monto}")
            print(f"         {t.descripcion[:60]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    analizar_transacciones_auto_calculadas()