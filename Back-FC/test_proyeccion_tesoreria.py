#!/usr/bin/env python3
"""
Script para probar la nueva proyección de Tesorería
SALDO FINAL CUENTAS (ID 51) → SALDO INICIAL (ID 1) del próximo día hábil
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
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from sqlalchemy.orm import Session

def probar_proyeccion_tesoreria():
    """Probar la proyección de Tesorería para el viernes 19 de septiembre → lunes 22 de septiembre"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        # Crear servicio
        service = DependenciasFlujoCajaService(db)
        
        # Fecha de prueba: viernes 19 de septiembre de 2025
        fecha_viernes = date(2025, 9, 19)
        
        print(f"🔍 PROBANDO PROYECCIÓN TESORERÍA: {fecha_viernes}")
        print("=" * 60)
        
        # 1. Verificar que existe SALDO FINAL CUENTAS (ID 51) en tesorería para el viernes
        saldos_finales = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_viernes,
            TransaccionFlujoCaja.concepto_id == 51,  # SALDO FINAL CUENTAS
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        print(f"📊 SALDO FINAL CUENTAS encontrados para {fecha_viernes}:")
        for saldo in saldos_finales:
            print(f"   Cuenta {saldo.cuenta_id}: ${saldo.monto}")
        
        # 2. Verificar próximo día hábil
        dias_habiles_service = DiasHabilesService(db)
        fecha_siguiente = dias_habiles_service.proximo_dia_habil(fecha_viernes, incluir_fecha_actual=False)
        print(f"📅 Próximo día hábil después del {fecha_viernes}: {fecha_siguiente}")
        
        # 3. Ver SALDO INICIAL antes de la proyección
        saldos_iniciales_antes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_siguiente,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        print(f"📋 SALDO INICIAL existentes para {fecha_siguiente} (ANTES):")
        for saldo in saldos_iniciales_antes:
            print(f"   Cuenta {saldo.cuenta_id}: ${saldo.monto}")
        
        # 4. Ejecutar el procesamiento que incluye la nueva lógica de proyección
        print(f"\n🚀 EJECUTANDO PROCESAMIENTO CON NUEVA PROYECCIÓN...")
        resultado = service._procesar_dependencias_pagaduria(
            fecha=fecha_viernes,
            usuario_id=1,
            compania_id=1
        )
        
        print(f"✅ Procesamiento completado. Actualizaciones: {len(resultado)}")
        
        # 5. Ver SALDO INICIAL después de la proyección
        saldos_iniciales_despues = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_siguiente,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        print(f"\n📋 SALDO INICIAL después de proyección para {fecha_siguiente}:")
        for saldo in saldos_iniciales_despues:
            print(f"   Cuenta {saldo.cuenta_id}: ${saldo.monto}")
            if hasattr(saldo, 'descripcion') and saldo.descripcion:
                print(f"      Descripción: {saldo.descripcion}")
        
        # 6. Comparar diferencias
        print(f"\n📊 ANÁLISIS DE CAMBIOS:")
        cuentas_antes = {s.cuenta_id: s.monto for s in saldos_iniciales_antes}
        cuentas_despues = {s.cuenta_id: s.monto for s in saldos_iniciales_despues}
        
        # Cuentas con proyección nueva
        for cuenta_id, monto_despues in cuentas_despues.items():
            monto_antes = cuentas_antes.get(cuenta_id, 0)
            if monto_antes != monto_despues:
                print(f"   🔄 Cuenta {cuenta_id}: ${monto_antes} → ${monto_despues}")
            else:
                print(f"   ➖ Cuenta {cuenta_id}: Sin cambios (${monto_despues})")
        
        # Cuentas nuevas
        cuentas_nuevas = set(cuentas_despues.keys()) - set(cuentas_antes.keys())
        if cuentas_nuevas:
            print(f"   ✨ Cuentas con nueva proyección: {list(cuentas_nuevas)}")
        
        print(f"\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    probar_proyeccion_tesoreria()