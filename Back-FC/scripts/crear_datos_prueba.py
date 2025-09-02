#!/usr/bin/env python3
"""
Script para crear datos de prueba del sistema de flujo de caja
"""
import sys
import os
from datetime import date, datetime
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.schemas.flujo_caja import TransaccionFlujoCajaCreate, AreaTransaccionSchema

def crear_datos_prueba():
    """Crear datos de prueba para el flujo de caja"""
    print("🔧 CREANDO DATOS DE PRUEBA")
    print("=" * 50)
    
    db = SessionLocal()
    service = TransaccionFlujoCajaService(db)
    
    try:
        # Datos de prueba para tesorería (fecha de hoy)
        fecha_hoy = date.today()
        
        transacciones_tesoreria = [
            # Conceptos básicos
            TransaccionFlujoCajaCreate(
                fecha=fecha_hoy,
                concepto_id=1,  # SALDO INICIAL
                cuenta_id=None,
                monto=Decimal('50000000.00'),
                descripcion="Saldo inicial del día",
                area=AreaTransaccionSchema.tesoreria
            ),
            TransaccionFlujoCajaCreate(
                fecha=fecha_hoy,
                concepto_id=7,  # INGRESOS INTERESES 
                cuenta_id=None,
                monto=Decimal('2500000.00'),
                descripcion="Intereses recibidos",
                area=AreaTransaccionSchema.tesoreria
            ),
            TransaccionFlujoCajaCreate(
                fecha=fecha_hoy,
                concepto_id=15,  # COMPRA TÍTULOS
                cuenta_id=None,
                monto=Decimal('10000000.00'),
                descripcion="Compra de títulos valores",
                area=AreaTransaccionSchema.tesoreria
            )
        ]
        
        # Datos de prueba para pagaduría
        transacciones_pagaduria = [
            TransaccionFlujoCajaCreate(
                fecha=fecha_hoy,
                concepto_id=50,  # SALDO INICIAL (pagaduría)
                cuenta_id=None,
                monto=Decimal('25000000.00'),
                descripcion="Saldo inicial pagaduría",
                area=AreaTransaccionSchema.pagaduria
            ),
            TransaccionFlujoCajaCreate(
                fecha=fecha_hoy,
                concepto_id=53,  # APORTES CAJA HONOR
                cuenta_id=None,
                monto=Decimal('5000000.00'),
                descripcion="Aportes caja de honor",
                area=AreaTransaccionSchema.pagaduria
            )
        ]
        
        # Crear transacciones de tesorería
        print("📋 Creando transacciones de TESORERÍA:")
        for transaccion_data in transacciones_tesoreria:
            try:
                transaccion = service.crear_transaccion(transaccion_data, 1)  # Usuario ID 1
                print(f"   ✅ {transaccion.concepto.nombre}: ${transaccion.monto:,.2f}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print()
        
        # Crear transacciones de pagaduría
        print("📋 Creando transacciones de PAGADURÍA:")
        for transaccion_data in transacciones_pagaduria:
            try:
                transaccion = service.crear_transaccion(transaccion_data, 1)
                print(f"   ✅ {transaccion.concepto.nombre}: ${transaccion.monto:,.2f}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print()
        print("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print(f"📅 Fecha: {fecha_hoy}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_datos_prueba()
