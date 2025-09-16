#!/usr/bin/env python3
"""
Verificar la configuración del concepto 50 (SUB-TOTAL TESORERÍA)
"""

import sys
import os
from datetime import date

# Configurar el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
settings = Settings()

def verificar_concepto_50():
    """Verificar configuración del concepto 50"""
    print("🔍 === VERIFICACIÓN CONCEPTO 50 (SUB-TOTAL TESORERÍA) === 🔍")
    
    # Preparar base de datos
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n1. 📋 Configuración del concepto 50:")
        concepto_50 = db.execute(text("""
            SELECT id, nombre, formula_dependencia, depende_de_concepto_id, tipo_dependencia, area, activo
            FROM conceptos_flujo_caja 
            WHERE id = 50
        """)).fetchone()
        
        if concepto_50:
            print(f"   ✅ ID: {concepto_50[0]}")
            print(f"   ✅ Nombre: {concepto_50[1]}")
            print(f"   ✅ Fórmula: {concepto_50[2]}")
            print(f"   ✅ Depende de concepto: {concepto_50[3]}")
            print(f"   ✅ Tipo dependencia: {concepto_50[4]}")
            print(f"   ✅ Área: {concepto_50[5]}")
            print(f"   ✅ Activo: {concepto_50[6]}")
        else:
            print("   ❌ Concepto 50 no encontrado")
            return
            
        print(f"\n2. 🔍 Verificando si hay transacciones para conceptos 5-49:")
        transacciones_componentes = db.execute(text("""
            SELECT concepto_id, COUNT(*) as cantidad, SUM(monto) as suma_total
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha 
            AND concepto_id BETWEEN 5 AND 49 
            AND cuenta_id = 1 
            AND area = 'tesoreria'
            GROUP BY concepto_id
            ORDER BY concepto_id
        """), {"fecha": date(2025, 9, 16)}).fetchall()
        
        if transacciones_componentes:
            total_esperado = 0
            print("   📊 Transacciones encontradas:")
            for tx in transacciones_componentes:
                print(f"      • Concepto {tx[0]}: {tx[1]} transacciones, suma = ${tx[2]}")
                total_esperado += float(tx[2])
            print(f"   📊 SUMA TOTAL ESPERADA: ${total_esperado}")
        else:
            print("   ❌ No hay transacciones en conceptos 5-49")
            
        print(f"\n3. 🔍 Estado actual del concepto 50:")
        subtotal_actual = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja 
            WHERE fecha = :fecha AND concepto_id = 50 AND cuenta_id = 1
        """), {"fecha": date(2025, 9, 16)}).fetchone()
        
        if subtotal_actual:
            print(f"   📊 SUB-TOTAL TESORERÍA actual: ${subtotal_actual[0]}")
            if transacciones_componentes:
                diferencia = float(subtotal_actual[0]) - total_esperado
                print(f"   📊 Diferencia: ${diferencia}")
                if abs(diferencia) < 0.01:
                    print(f"   ✅ CORRECTO: SUB-TOTAL coincide con la suma")
                else:
                    print(f"   ❌ INCORRECTO: SUB-TOTAL NO coincide con la suma")
        else:
            print("   ❌ No se encontró transacción para concepto 50")
            
        print(f"\n4. 🔧 Probando cálculo manual de fórmula:")
        if concepto_50 and concepto_50[2]:  # Si tiene fórmula
            formula = concepto_50[2]
            print(f"   Fórmula: {formula}")
            
            # Simular cálculo manual
            if "SUMA(" in formula:
                # Extraer IDs de la fórmula
                import re
                matches = re.findall(r'SUMA\((.*?)\)', formula)
                if matches:
                    ids_str = matches[0]
                    print(f"   IDs en fórmula: {ids_str}")
                    
                    # Calcular suma manual
                    suma_manual = db.execute(text("""
                        SELECT COALESCE(SUM(monto), 0) as suma_total
                        FROM transacciones_flujo_caja 
                        WHERE fecha = :fecha 
                        AND concepto_id BETWEEN 5 AND 49 
                        AND cuenta_id = 1 
                        AND area = 'tesoreria'
                    """), {"fecha": date(2025, 9, 16)}).fetchone()
                    
                    print(f"   📊 Suma manual calculada: ${suma_manual[0] if suma_manual else 0}")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    verificar_concepto_50()