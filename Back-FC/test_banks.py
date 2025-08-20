#!/usr/bin/env python3
"""
Script de prueba para verificar el modelo Banco
"""
import sys
import os

# Agregar el directorio padre al path para importar las dependencias
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.bancos import Banco

def test_bancos():
    """Probar el acceso a la tabla bancos"""
    db = SessionLocal()
    try:
        print("Conectando a la base de datos...")
        
        # Intentar consultar todos los bancos
        bancos = db.query(Banco).all()
        print(f"Número de bancos encontrados: {len(bancos)}")
        
        for banco in bancos:
            print(f"- ID: {banco.id}, Nombre: {banco.nombre}")
            
        return True
        
    except Exception as e:
        print(f"Error al consultar bancos: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_bancos()
