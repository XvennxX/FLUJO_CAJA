"""
Script para probar el cálculo automático de DIFERENCIA SALDOS
DIFERENCIA SALDOS = SALDOS EN BANCOS - SALDO DIA ANTERIOR
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService

def test_diferencia_saldos():
    """Probar el cálculo automático de DIFERENCIA SALDOS"""
    print("🧪 PRUEBA: Cálculo automático de DIFERENCIA SALDOS")
    print("=" * 60)
    
    db = next(get_db())
    service = DependenciasFlujoCajaService(db)
    
    fecha_prueba = date(2025, 9, 16)
    cuenta_id = 1
    
    print(f"📅 Fecha de prueba: {fecha_prueba}")
    print(f"🏦 Cuenta: {cuenta_id}")
    print()
    
    # 1️⃣ Estado inicial - mostrar valores actuales
    print("1️⃣ Estado ANTES:")
    
    # SALDOS EN BANCOS (ID 53)
    saldos_bancos = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.concepto_id == 53,
        TransaccionFlujoCaja.cuenta_id == cuenta_id,
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    # SALDO DIA ANTERIOR (ID 54) 
    saldo_anterior = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.concepto_id == 54,
        TransaccionFlujoCaja.cuenta_id == cuenta_id,
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    # DIFERENCIA SALDOS (ID 52)
    diferencia_actual = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.concepto_id == 52,
        TransaccionFlujoCaja.cuenta_id == cuenta_id,
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    monto_saldos = saldos_bancos.monto if saldos_bancos else Decimal('0')
    monto_anterior = saldo_anterior.monto if saldo_anterior else Decimal('0')
    monto_diferencia = diferencia_actual.monto if diferencia_actual else Decimal('0')
    
    print(f"   💰 SALDOS EN BANCOS (ID 53): ${monto_saldos}")
    print(f"   📊 SALDO DÍA ANTERIOR (ID 54): ${monto_anterior}")  
    print(f"   🔢 DIFERENCIA SALDOS (ID 52): ${monto_diferencia}")
    print(f"   🧮 Cálculo esperado: ${monto_saldos} - ${monto_anterior} = ${monto_saldos - monto_anterior}")
    print()
    
    # 2️⃣ Simular cambio en SALDOS EN BANCOS
    print("2️⃣ Simulando cambio en SALDOS EN BANCOS...")
    nuevo_saldo_bancos = Decimal('1500.00')
    
    if saldos_bancos:
        valor_anterior = saldos_bancos.monto
        saldos_bancos.monto = nuevo_saldo_bancos
        saldos_bancos.descripcion = "Prueba automática - valor modificado"
        print(f"   ✏️  Cambiando SALDOS EN BANCOS: ${valor_anterior} → ${nuevo_saldo_bancos}")
    else:
        # Crear nueva transacción
        nueva_transaccion = TransaccionFlujoCaja(
            fecha=fecha_prueba,
            concepto_id=53,
            cuenta_id=cuenta_id,
            monto=nuevo_saldo_bancos,
            descripcion="Prueba automática - valor creado",
            usuario_id=6,
            area=AreaTransaccion.pagaduria,
            compania_id=1
        )
        db.add(nueva_transaccion)
        print(f"   ➕ Creando SALDOS EN BANCOS: ${nuevo_saldo_bancos}")
    
    db.commit()
    
    # 3️⃣ Ejecutar recálculo automático
    print("3️⃣ Ejecutando recálculo automático...")
    resultados = service.procesar_dependencias_completas_ambos_dashboards(
        fecha=fecha_prueba,
        concepto_modificado_id=53,  # SALDOS EN BANCOS
        cuenta_id=cuenta_id,
        compania_id=1,
        usuario_id=6
    )
    
    updates_pagaduria = len(resultados.get("pagaduria", []))
    print(f"   ✅ Procesamiento completado: {updates_pagaduria} actualizaciones")
    
    # 4️⃣ Estado final - verificar resultado
    print()
    print("4️⃣ Estado DESPUÉS:")
    
    # Refrescar datos
    db.refresh_all = lambda: None
    
    # DIFERENCIA SALDOS actualizada
    diferencia_nueva = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.concepto_id == 52,
        TransaccionFlujoCaja.cuenta_id == cuenta_id,
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    # SALDO DIA ANTERIOR (para recálculo)
    saldo_anterior_actual = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == fecha_prueba,
        TransaccionFlujoCaja.concepto_id == 54,
        TransaccionFlujoCaja.cuenta_id == cuenta_id,
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    monto_anterior_actual = saldo_anterior_actual.monto if saldo_anterior_actual else Decimal('0')
    monto_diferencia_nueva = diferencia_nueva.monto if diferencia_nueva else Decimal('0')
    
    print(f"   💰 SALDOS EN BANCOS (ID 53): ${nuevo_saldo_bancos}")
    print(f"   📊 SALDO DÍA ANTERIOR (ID 54): ${monto_anterior_actual}")
    print(f"   🔢 DIFERENCIA SALDOS (ID 52): ${monto_diferencia_nueva}")
    print(f"   🧮 Cálculo esperado: ${nuevo_saldo_bancos} - ${monto_anterior_actual} = ${nuevo_saldo_bancos - monto_anterior_actual}")
    
    # 5️⃣ Verificación
    print()
    print("5️⃣ Verificación:")
    diferencia_esperada = nuevo_saldo_bancos - monto_anterior_actual
    
    if diferencia_nueva and abs(diferencia_nueva.monto - diferencia_esperada) < Decimal('0.01'):
        print(f"   ✅ CORRECTO: DIFERENCIA SALDOS = ${monto_diferencia_nueva}")
        print(f"   ✅ Fórmula aplicada correctamente: SALDOS EN BANCOS - SALDO DÍA ANTERIOR")
        if diferencia_nueva.descripcion:
            print(f"   📝 Descripción: {diferencia_nueva.descripcion}")
    else:
        print(f"   ❌ ERROR: DIFERENCIA SALDOS = ${monto_diferencia_nueva}")
        print(f"   ❌ Esperado: ${diferencia_esperada}")
        print(f"   ❌ La fórmula no se aplicó correctamente")
    
    db.rollback()  # No guardar cambios de prueba
    print()
    print("🔄 Transacción revertida (datos de prueba)")

if __name__ == "__main__":
    test_diferencia_saldos()