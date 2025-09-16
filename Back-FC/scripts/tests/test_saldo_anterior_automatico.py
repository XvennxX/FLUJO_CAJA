#!/usr/bin/env python3
"""
Test para la nueva lógica: SALDO DIA ANTERIOR (ID 54) = SALDO TOTAL EN BANCOS (ID 85)
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
    """Limpia transacciones de prueba"""
    db = SessionLocal()
    try:
        print("🧹 Limpiando transacciones de prueba...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Eliminar transacciones de los conceptos relacionados
        conceptos_test = [52, 53, 54, 85]  # DIFERENCIA, SALDOS BANCOS, SALDO ANTERIOR, SALDO TOTAL BANCOS
        
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

def crear_datos_test():
    """Crea datos de prueba"""
    db = SessionLocal()
    try:
        print("📊 Creando datos de prueba...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Crear SALDO TOTAL EN BANCOS (ID 85) = $200.00
        transaccion_total_bancos = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=85,
            cuenta_id=1,
            monto=Decimal('200.00'),
            descripcion="SALDO TOTAL EN BANCOS - Prueba",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "pagaduria_saldo_anterior"}
        )
        
        # Crear SALDOS EN BANCOS (ID 53) = $100.00 (para probar DIFERENCIA SALDOS también)
        transaccion_bancos = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=53,
            cuenta_id=1,
            monto=Decimal('100.00'),
            descripcion="SALDOS EN BANCOS - Prueba",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={"test": "pagaduria_saldo_anterior"}
        )
        
        db.add(transaccion_total_bancos)
        db.add(transaccion_bancos)
        db.commit()
        
        print("   ✅ SALDO TOTAL EN BANCOS: $200.00")
        print("   ✅ SALDOS EN BANCOS: $100.00")
        print("   🎯 SALDO DIA ANTERIOR esperado: $200.00")
        print("   🎯 DIFERENCIA SALDOS esperada: $300.00 ($100 + $200)")
        
    finally:
        db.close()

def test_nueva_dependencia():
    """Test principal de la nueva dependencia"""
    db = SessionLocal()
    service = DependenciasFlujoCajaService(db)
    
    try:
        print("\n🔄 Ejecutando test de SALDO DIA ANTERIOR automático...")
        fecha_test = datetime(2025, 9, 10).date()
        
        # Verificar estado ANTES
        saldo_anterior_antes = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 54
            AND area = 'pagaduria'
        """), {"fecha": fecha_test}).fetchone()
        
        count_antes, monto_antes = saldo_anterior_antes
        print(f"   ANTES: {count_antes} SALDO DIA ANTERIOR, Total: ${monto_antes}")
        
        # Ejecutar procesamiento de dependencias
        actualizaciones = service.procesar_dependencias_avanzadas(
            fecha=fecha_test,
            area=AreaTransaccionSchema.pagaduria,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        print(f"   📝 Procesamiento ejecutado: {len(actualizaciones)} actualizaciones")
        
        # Verificar SALDO DIA ANTERIOR
        saldo_anterior_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 54
            AND area = 'pagaduria'
        """), {"fecha": fecha_test}).fetchone()
        
        count_despues, monto_despues = saldo_anterior_despues
        print(f"   DESPUÉS: {count_despues} SALDO DIA ANTERIOR, Total: ${monto_despues}")
        
        # Verificar DIFERENCIA SALDOS también
        diferencia_despues = db.execute(text("""
            SELECT COUNT(*), COALESCE(SUM(monto), 0) as total
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 52
            AND area = 'pagaduria'
        """), {"fecha": fecha_test}).fetchone()
        
        count_diff, monto_diff = diferencia_despues
        print(f"   DIFERENCIA SALDOS: {count_diff} transacciones, Total: ${monto_diff}")
        
        # Verificar resultados
        exito_saldo_anterior = (count_despues > count_antes and monto_despues == Decimal('200.00'))
        exito_diferencia = (monto_diff == Decimal('300.00'))  # $100 + $200
        
        if exito_saldo_anterior:
            print("   🎉 ¡ÉXITO! SALDO DIA ANTERIOR calculado correctamente: $200.00")
        else:
            print(f"   ❌ ERROR SALDO ANTERIOR: Se esperaba $200.00, se obtuvo ${monto_despues}")
            
        if exito_diferencia:
            print("   🎉 ¡ÉXITO! DIFERENCIA SALDOS recalculada correctamente: $300.00")
        else:
            print(f"   ❌ ERROR DIFERENCIA: Se esperaba $300.00, se obtuvo ${monto_diff}")
            
        # Mostrar resumen de actualizaciones
        print(f"\n📊 Resumen de actualizaciones:")
        for update in actualizaciones:
            concepto_id = update.get('concepto_id')
            concepto_nombre = update.get('concepto_nombre', 'N/A')
            monto_nuevo = update.get('monto_nuevo', 0)
            origen = update.get('origen', {})
            
            if origen:
                origen_texto = f" (desde {origen.get('concepto_nombre', 'N/A')})"
            else:
                origen_texto = ""
                
            print(f"   • [{concepto_id}] {concepto_nombre}: ${monto_nuevo}{origen_texto}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        
    finally:
        db.close()

def verificar_estado_final():
    """Verifica el estado final completo"""
    db = SessionLocal()
    try:
        print(f"\n📋 Estado final completo de pagaduría:")
        fecha_test = datetime(2025, 9, 10).date()
        
        transacciones = db.execute(text("""
            SELECT c.id, c.nombre, t.monto, t.descripcion
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.area = 'pagaduria'
            AND c.id IN (52, 53, 54, 85)
            ORDER BY c.orden_display
        """), {"fecha": fecha_test}).fetchall()
        
        for trans in transacciones:
            id_concepto, nombre, monto, desc = trans
            print(f"   • [{id_concepto}] {nombre}: ${monto} ({desc})")
            
    finally:
        db.close()

def main():
    print("=== TEST NUEVA DEPENDENCIA PAGADURÍA ===")
    print("🎯 Probando: SALDO DIA ANTERIOR = SALDO TOTAL EN BANCOS")
    print("🔄 También verifica que DIFERENCIA SALDOS se recalcule")
    
    # 1. Limpiar datos anteriores
    limpiar_transacciones_test()
    
    # 2. Crear datos de prueba
    crear_datos_test()
    
    # 3. Ejecutar test principal
    test_nueva_dependencia()
    
    # 4. Verificar estado final
    verificar_estado_final()
    
    print(f"\n🎉 Test completado!")
    print(f"💡 Resultados esperados:")
    print(f"   • SALDO DIA ANTERIOR = $200.00")
    print(f"   • DIFERENCIA SALDOS = $300.00 ($100 + $200)")

if __name__ == "__main__":
    main()
