#!/usr/bin/env python3
"""
Script de prueba para verificar el modelo CuentaBancaria
"""
import sys
import os

# Agregar el directorio padre al path para importar las dependencias
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.cuentas_bancarias import CuentaBancaria

def test_cuentas_bancarias():
    """Probar el acceso a la tabla cuentas_bancarias"""
    db = SessionLocal()
    try:
        print("Conectando a la base de datos...")
        
        # Intentar consultar todas las cuentas bancarias
        cuentas = db.query(CuentaBancaria).all()
        print(f"Número de cuentas bancarias encontradas: {len(cuentas)}")
        
        for cuenta in cuentas:
            print(f"- ID: {cuenta.id}, Número: {cuenta.numero_cuenta}, Compañía: {cuenta.compania_id}, Banco: {cuenta.banco_id}")
            
        return True
        
    except Exception as e:
        print(f"Error al consultar cuentas bancarias: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_cuentas_bancarias()
