#!/usr/bin/env python3
"""
Test para la nueva lógica: SALDO DIA ANTERIOR = SALDO TOTAL EN BANCOS del día anterior
"""

import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.schemas.flujo_caja import AreaTransaccionSchema
from decimal import Decimal
from sqlalchemy import text

def setup_datos_test():
    """Crea datos de prueba para el test"""
    db = SessionLocal()
    try:
        print("📊 Configurando datos de prueba...")
        
        fecha_ayer = datetime(2025, 9, 9).date()  # Ayer
        fecha_hoy = datetime(2025, 9, 10).date()  # Hoy
        
        # Limpiar datos anteriores
        for fecha in [fecha_ayer, fecha_hoy]:
            for concepto_id in [54, 85]:  # SALDO DIA ANTERIOR, SALDO TOTAL EN BANCOS
                db.execute(text("""
                    DELETE FROM transacciones_flujo_caja
                    WHERE fecha = :fecha
                    AND concepto_id = :concepto_id
                    AND area = 'pagaduria'
                """), {"fecha": fecha, "concepto_id": concepto_id})
        
        # Crear SALDO TOTAL EN BANCOS de AYER = $200.00
        transaccion_ayer = TransaccionFlujoCaja(
            fecha=fecha_ayer,
            concepto_id=85,  # SALDO TOTAL EN BANCOS
            cuenta_id=1,
            monto=Decimal('200.00'),
            descripcion="SALDO TOTAL EN BANCOS - Ayer",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "saldo_dia_anterior"}
        )
        
        db.add(transaccion_ayer)
        db.commit()
        
        print(f"   ✅ SALDO TOTAL EN BANCOS {fecha_ayer}: $200.00")
        print(f"   🎯 SALDO DIA ANTERIOR esperado para {fecha_hoy}: $200.00")
        
    finally:
        db.close()

def test_saldo_dia_anterior_automatico():
    """Test principal de la nueva lógica"""
    db = SessionLocal()
    service = DependenciasFlujoCajaService(db)
    
    try:
        print("\n🔄 Ejecutando test SALDO DIA ANTERIOR automático...")
        fecha_hoy = datetime(2025, 9, 10).date()
        
        # Verificar estado ANTES
        saldo_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 54
            AND area = 'pagaduria'
        """), {"fecha": fecha_hoy}).fetchone()
        
        count_antes, monto_antes = saldo_antes
        print(f"   ANTES: {count_antes} SALDO DIA ANTERIOR, Total: ${monto_antes}")
        
        # Ejecutar procesamiento de dependencias pagaduría
        actualizaciones = service._procesar_dependencias_pagaduria(
            fecha=fecha_hoy,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Procesamiento ejecutado: {len(actualizaciones)} actualizaciones")
        
        # Verificar estado DESPUÉS
        saldo_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 54
            AND area = 'pagaduria'
        """), {"fecha": fecha_hoy}).fetchone()
        
        count_despues, monto_despues = saldo_despues
        print(f"   DESPUÉS: {count_despues} SALDO DIA ANTERIOR, Total: ${monto_despues}")
        
        # Verificar el resultado
        if count_despues > count_antes and monto_despues == Decimal('200.00'):
            print("   🎉 ¡ÉXITO! SALDO DIA ANTERIOR calculado correctamente: $200.00")
            
            # Mostrar detalles de la transacción creada
            detalles = db.execute(text("""
                SELECT monto, descripcion, auditoria, created_at
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 54
                AND area = 'pagaduria'
                ORDER BY created_at DESC
                LIMIT 1
            """), {"fecha": fecha_hoy}).fetchone()
            
            if detalles:
                monto, desc, auditoria, created_at = detalles
                print(f"      💰 Monto: ${monto}")
                print(f"      📋 Descripción: {desc}")
                print(f"      ⏰ Creado: {created_at}")
                
        else:
            print(f"   ❌ ERROR: Se esperaba $200.00, se obtuvo ${monto_despues}")
        
        # Mostrar todas las actualizaciones
        print(f"\n📊 Resumen de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
            if 'origen' in update:
                origen = update['origen']
                if 'fecha_anterior' in origen:
                    print(f"     ↳ Origen: {origen['fecha_anterior']}, ${origen.get('saldo_total_bancos', 0)}")
                    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

def verificar_estado_completo():
    """Verifica el estado completo de ambos días"""
    db = SessionLocal()
    try:
        print(f"\n📋 Estado completo de transacciones:")
        
        fechas = [
            datetime(2025, 9, 9).date(),   # Ayer
            datetime(2025, 9, 10).date(),  # Hoy
        ]
        
        for fecha in fechas:
            print(f"\n📅 {fecha}:")
            transacciones = db.execute(text("""
                SELECT c.nombre, t.monto, t.descripcion
                FROM transacciones_flujo_caja t
                JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
                WHERE t.fecha = :fecha
                AND t.area = 'pagaduria'
                AND c.id IN (54, 85)
                ORDER BY c.id
            """), {"fecha": fecha}).fetchall()
            
            if transacciones:
                for trans in transacciones:
                    nombre, monto, desc = trans
                    print(f"   • {nombre}: ${monto} ({desc})")
            else:
                print(f"   ❌ Sin transacciones de pagaduría")
                
    finally:
        db.close()

def main():
    print("=== TEST SALDO DIA ANTERIOR AUTOMÁTICO ===")
    print("🎯 Probando: SALDO DIA ANTERIOR = SALDO TOTAL EN BANCOS del día anterior")
    
    # 1. Configurar datos de prueba
    setup_datos_test()
    
    # 2. Ejecutar test principal
    test_saldo_dia_anterior_automatico()
    
    # 3. Verificar estado completo
    verificar_estado_completo()
    
    print(f"\n🎉 Test completado!")
    print(f"💡 Si SALDO DIA ANTERIOR = $200.00, ¡la lógica funciona correctamente!")

if __name__ == "__main__":
    main()
