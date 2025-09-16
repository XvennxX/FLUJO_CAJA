#!/usr/bin/env python3
"""
Script para verificar que el saldo inicial del día 4 se calcule correctamente
desde el SALDO FINAL CUENTAS del día 3.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from decimal import Decimal
from datetime import date
from app.core.database import get_db_context
from app.services.saldo_inicial_service import SaldoInicialService

def test_saldo_inicial_dia_4():
    """Prueba el cálculo del saldo inicial para el día 4 de septiembre"""
    
    with get_db_context() as db:
        saldo_service = SaldoInicialService(db)
        
        # Fecha para la cual queremos calcular el saldo inicial
        fecha_actual = date(2025, 9, 4)
        
        print(f"\n🔍 Calculando saldo inicial para {fecha_actual}...")
        
        # Calcular el saldo inicial que debería ser el SALDO FINAL CUENTAS del día anterior
        saldo_inicial = saldo_service.calcular_saldo_final_dia_anterior(
            fecha=fecha_actual,
            area='TESORERIA'
        )
        
        print(f"\n📊 Resultado del cálculo:")
        print(f"   Fecha: {fecha_actual}")
        print(f"   Saldo Inicial: ${saldo_inicial:,.2f}")
        
        # Verificar que el valor sea el esperado ($176.00)
        valor_esperado = Decimal('176.00')
        
        if saldo_inicial == valor_esperado:
            print(f"   ✅ Correcto: El saldo inicial es ${valor_esperado:,.2f}")
            print(f"   ✅ El sistema está funcionando correctamente")
        else:
            print(f"   ❌ Error: Se esperaba ${valor_esperado:,.2f} pero se obtuvo ${saldo_inicial:,.2f}")
        
        print(f"\n📋 Resumen:")
        print(f"   - SALDO FINAL CUENTAS del 2025-09-03: ${valor_esperado:,.2f}")
        print(f"   - Saldo inicial calculado para 2025-09-04: ${saldo_inicial:,.2f}")
        print(f"   - Estado: {'✅ CORRECTO' if saldo_inicial == valor_esperado else '❌ ERROR'}")

if __name__ == "__main__":
    test_saldo_inicial_dia_4()
