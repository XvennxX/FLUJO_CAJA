#!/usr/bin/env python3
"""
Test de flujo completo de varios días con SALDO INICIAL y SALDO FINAL
Simula el funcionamiento real donde cada día debe tener SALDO FINAL para el siguiente día
"""

import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from decimal import Decimal
from sqlalchemy import text

def limpiar_datos_test():
    """Limpia datos de prueba anteriores"""
    print("🧹 Limpiando datos de prueba...")
    db = SessionLocal()
    try:
        fechas_limpiar = [
            datetime(2025, 9, 10).date(),
            datetime(2025, 9, 11).date(),
            datetime(2025, 9, 12).date(),
            datetime(2025, 9, 13).date(),
        ]
        
        for fecha in fechas_limpiar:
            # Eliminar SALDO INICIAL y SALDO FINAL de prueba
            for concepto_id in [1, 51]:
                db.execute(text("""
                    DELETE FROM transacciones_flujo_caja
                    WHERE fecha = :fecha
                    AND concepto_id = :concepto_id
                    AND area = 'tesoreria'
                """), {"fecha": fecha, "concepto_id": concepto_id})
        
        db.commit()
        print("✅ Limpieza completada")
    finally:
        db.close()

def crear_saldo_final_dia(fecha, cuenta_id, monto):
    """Crea un SALDO FINAL para un día específico"""
    db = SessionLocal()
    try:
        transaccion = TransaccionFlujoCaja(
            fecha=fecha,
            concepto_id=51,  # SALDO FINAL CUENTAS
            cuenta_id=cuenta_id,
            monto=monto,
            descripcion="SALDO FINAL para prueba",
            usuario_id=6,
            area="tesoreria",
            compania_id=1,
            auditoria='{"test": "flujo_completo"}'
        )
        
        db.add(transaccion)
        db.commit()
        print(f"   💰 Creado SALDO FINAL día {fecha}: Cuenta {cuenta_id} = ${monto}")
        
    finally:
        db.close()

def verificar_dia(fecha):
    """Verifica estado de un día específico"""
    db = SessionLocal()
    try:
        # Verificar SALDO INICIAL
        count_inicial = db.execute(text("""
            SELECT COUNT(*) as cantidad
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 1
            AND area = 'tesoreria'
        """), {"fecha": fecha}).fetchone()[0]
        
        # Verificar SALDO FINAL
        count_final = db.execute(text("""
            SELECT COUNT(*) as cantidad
            FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 51
            AND area = 'tesoreria'
        """), {"fecha": fecha}).fetchone()[0]
        
        print(f"📊 Día {fecha}: SALDO INICIAL={count_inicial}, SALDO FINAL={count_final}")
        
        if count_inicial > 0:
            inicial_data = db.execute(text("""
                SELECT cuenta_id, monto, created_at
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 1
                AND area = 'tesoreria'
                ORDER BY cuenta_id
            """), {"fecha": fecha}).fetchall()
            
            for cuenta_id, monto, created_at in inicial_data:
                print(f"   ✅ SALDO INICIAL Cuenta {cuenta_id}: ${monto} (creado: {created_at})")
        
        if count_final > 0:
            final_data = db.execute(text("""
                SELECT cuenta_id, monto
                FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 51
                AND area = 'tesoreria'
                ORDER BY cuenta_id
            """), {"fecha": fecha}).fetchall()
            
            for cuenta_id, monto in final_data:
                print(f"   💰 SALDO FINAL Cuenta {cuenta_id}: ${monto}")
                
    finally:
        db.close()

def main():
    print("=== TEST FLUJO COMPLETO DE VARIOS DÍAS ===")
    
    # 1. Limpiar datos anteriores
    limpiar_datos_test()
    
    # 2. Estado inicial: día 9 ya tiene SALDO FINAL de $30
    print("\n📅 Estado inicial - Día 9 con SALDO FINAL existente")
    verificar_dia(datetime(2025, 9, 9).date())
    
    # 3. Simular flujo de 4 días consecutivos
    db = SessionLocal()
    service = DependenciasFlujoCajaService(db)
    
    try:
        fechas_procesamiento = [
            datetime(2025, 9, 10).date(),
            datetime(2025, 9, 11).date(),
            datetime(2025, 9, 12).date(),
            datetime(2025, 9, 13).date(),
        ]
        
        for i, fecha in enumerate(fechas_procesamiento):
            print(f"\n🗓️ === DÍA {i+1}: {fecha} ===")
            
            # Verificar estado antes
            print("ANTES del procesamiento:")
            verificar_dia(fecha)
            
            # Procesar SALDO INICIAL automático
            print(f"\n🔄 Procesando SALDO INICIAL automático para {fecha}...")
            try:
                transacciones_procesadas = service._procesar_saldo_inicial_automatico(fecha)
                print(f"   RESULTADO: {transacciones_procesadas} transacciones creadas")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
            
            # Verificar estado después del SALDO INICIAL
            print("\nDESPUÉS del SALDO INICIAL:")
            verificar_dia(fecha)
            
            # Simular creación de SALDO FINAL para que el siguiente día tenga base
            # (excepto para el último día del test)
            if i < len(fechas_procesamiento) - 1:
                print(f"\n💰 Creando SALDO FINAL simulado para {fecha}...")
                # Incrementar el saldo un poco cada día (simulando flujo de caja)
                saldo_final = Decimal("30.00") + Decimal(str((i + 1) * 5))  # 30, 35, 40, 45...
                crear_saldo_final_dia(fecha, 1, saldo_final)
                
                print("DESPUÉS de crear SALDO FINAL:")
                verificar_dia(fecha)
        
    finally:
        db.close()
    
    # 4. Verificar continuidad completa
    print("\n🔗 === VERIFICACIÓN FINAL DE CONTINUIDAD ===")
    for fecha in fechas_procesamiento:
        verificar_dia(fecha)
    
    print(f"\n🎉 Test de flujo completo terminado!")
    print("📝 Resumen: Cada día debe tener SALDO FINAL para que el siguiente tenga SALDO INICIAL")

if __name__ == "__main__":
    main()
