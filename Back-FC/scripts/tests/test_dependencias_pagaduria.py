#!/usr/bin/env python3
"""
Test específico para la lógica de dependencias de pagaduría
DIFERENCIA SALDOS = SALDOS EN BANCOS + SALDO DIA ANTERIOR
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

def limpiar_transacciones_test():
    """Limpia transacciones de prueba de pagaduría"""
    db = SessionLocal()
    try:
        print("🧹 Limpiando transacciones de prueba...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Eliminar transacciones de los conceptos de prueba
        conceptos_test = [52, 53, 54]  # DIFERENCIA SALDOS, SALDOS BANCOS, SALDO ANTERIOR
        
        for concepto_id in conceptos_test:
            resultado = db.execute(text("""
                DELETE FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = :concepto_id
                AND area = 'pagaduria'
            """), {"fecha": fecha_test, "concepto_id": concepto_id})
            
            print(f"   ✅ Eliminadas transacciones del concepto {concepto_id}")
        
        db.commit()
        print("✅ Limpieza completada")
        
    finally:
        db.close()

def crear_datos_base():
    """Crea datos base para la prueba"""
    db = SessionLocal()
    try:
        print("📊 Creando datos base para prueba...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Crear SALDOS EN BANCOS (ID 53) = $100.00
        transaccion_bancos = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=53,
            cuenta_id=1,
            monto=Decimal('100.00'),
            descripcion="SALDOS EN BANCOS - Prueba",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "pagaduria_dependencias"}
        )
        
        # Crear SALDO DIA ANTERIOR (ID 54) = $50.00
        transaccion_anterior = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=54,
            cuenta_id=1,
            monto=Decimal('50.00'),
            descripcion="SALDO DIA ANTERIOR - Prueba",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "pagaduria_dependencias"}
        )
        
        db.add(transaccion_bancos)
        db.add(transaccion_anterior)
        db.commit()
        
        print("   ✅ SALDOS EN BANCOS: $100.00")
        print("   ✅ SALDO DIA ANTERIOR: $50.00")
        print("   🎯 DIFERENCIA SALDOS esperada: $150.00")
        
    finally:
        db.close()

def test_dependencia_diferencia_saldos():
    """Test principal de la dependencia"""
    db = SessionLocal()
    service = DependenciasFlujoCajaService(db)
    
    try:
        print("\n🔄 Ejecutando test de dependencias pagaduría...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Verificar estado ANTES
        diferencia_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 52
            AND area = 'pagaduria'
        """), {"fecha": fecha_test}).fetchone()
        
        count_antes, monto_antes = diferencia_antes
        print(f"   ANTES: {count_antes} DIFERENCIA SALDOS, Total: ${monto_antes}")
        
        # Ejecutar procesamiento de dependencias
        actualizaciones = service.procesar_dependencias_avanzadas(
            fecha=fecha_test,
            area=AreaTransaccionSchema.pagaduria,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Procesamiento ejecutado: {len(actualizaciones)} actualizaciones")
        
        # Verificar estado DESPUÉS
        diferencia_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 52
            AND area = 'pagaduria'
        """), {"fecha": fecha_test}).fetchone()
        
        count_despues, monto_despues = diferencia_despues
        print(f"   DESPUÉS: {count_despues} DIFERENCIA SALDOS, Total: ${monto_despues}")
        
        # Verificar el cálculo
        if count_despues > count_antes and monto_despues == Decimal('150.00'):
            print("   🎉 ¡ÉXITO! DIFERENCIA SALDOS calculada correctamente: $150.00")
            
            # Mostrar detalles de la transacción creada
            detalles = db.execute(text("""
                SELECT monto, descripcion, auditoria, created_at
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 52
                AND area = 'pagaduria'
                ORDER BY created_at DESC
                LIMIT 1
            """), {"fecha": fecha_test}).fetchone()
            
            if detalles:
                monto, desc, auditoria, created_at = detalles
                print(f"      💰 Monto: ${monto}")
                print(f"      📋 Descripción: {desc}")
                print(f"      ⏰ Creado: {created_at}")
                
        else:
            print(f"   ❌ ERROR: Se esperaba $150.00, se obtuvo ${monto_despues}")
            
        # Mostrar resumen de actualizaciones
        print(f"\n📊 Resumen de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        
    finally:
        db.close()

def verificar_estado_final():
    """Verifica el estado final de todas las transacciones"""
    db = SessionLocal()
    try:
        print(f"\n📋 Estado final de transacciones pagaduría:")
        fecha_test = datetime(2025, 9, 10).date()
        
        transacciones = db.execute(text("""
            SELECT c.nombre, t.monto, t.descripcion
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.area = 'pagaduria'
            AND c.id IN (52, 53, 54)
            ORDER BY c.orden_display
        """), {"fecha": fecha_test}).fetchall()
        
        for trans in transacciones:
            nombre, monto, desc = trans
            print(f"   • {nombre}: ${monto} ({desc})")
            
    finally:
        db.close()

def main():
    print("=== TEST DEPENDENCIAS PAGADURÍA ===")
    print("🎯 Probando: DIFERENCIA SALDOS = SALDOS EN BANCOS + SALDO DIA ANTERIOR")
    
    # 1. Limpiar datos anteriores
    limpiar_transacciones_test()
    
    # 2. Crear datos base
    crear_datos_base()
    
    # 3. Ejecutar test principal
    test_dependencia_diferencia_saldos()
    
    # 4. Verificar estado final
    verificar_estado_final()
    
    print(f"\n🎉 Test completado!")
    print(f"💡 Si DIFERENCIA SALDOS = $150.00, ¡la lógica funciona correctamente!")

if __name__ == "__main__":
    main()
