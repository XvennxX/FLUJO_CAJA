#!/usr/bin/env python3
"""
Test para verificar exactamente qué contiene update_data
"""

import sys
import os

# Configurar el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.schemas.flujo_caja import TransaccionFlujoCajaUpdate

def test_update_data():
    print("🔍 === TEST DE UPDATE_DATA === 🔍")
    
    # Crear datos como en el test real
    nuevos_datos = TransaccionFlujoCajaUpdate(
        monto=8888.88,
        descripcion="TEST UPDATE DATA"
    )
    
    print(f"\n1. 📋 Datos creados:")
    print(f"   monto: {nuevos_datos.monto}")
    print(f"   descripcion: {nuevos_datos.descripcion}")
    
    print(f"\n2. 🔍 Evaluando dict(exclude_unset=True):")
    update_data = nuevos_datos.dict(exclude_unset=True)
    print(f"   update_data: {update_data}")
    print(f"   Llaves en update_data: {list(update_data.keys())}")
    
    print(f"\n3. ✅ Verificación de condiciones:")
    print(f"   'fecha' in update_data: {'fecha' in update_data}")
    print(f"   'area' in update_data: {'area' in update_data}")
    print(f"   'monto' in update_data: {'monto' in update_data}")
    
    condicion_completa = 'fecha' in update_data or 'area' in update_data or 'monto' in update_data
    print(f"   Condición completa (OR): {condicion_completa}")
    
    if condicion_completa:
        print(f"   ✅ AUTO-CÁLCULO DEBERÍA EJECUTARSE")
    else:
        print(f"   ❌ AUTO-CÁLCULO NO SE EJECUTA - ¡AHÍ ESTÁ EL PROBLEMA!")

if __name__ == "__main__":
    test_update_data()