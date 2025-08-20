"""
Script para crear bancos de prueba en la base de datos
"""
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.bancos import Banco

def create_test_banks():
    """Crear bancos de prueba en la base de datos"""
    
    # Lista de bancos colombianos comunes
    bancos_colombianos = [
        "Banco de Bogotá",
        "Bancolombia",
        "Banco de Occidente",
        "BBVA Colombia",
        "Banco Popular",
        "Banco Davivienda",
        "Banco Caja Social",
        "Banco AV Villas",
        "Banco Agrario",
        "Banco Falabella",
        "Banco Finandina",
        "Banco GNB Sudameris",
        "Banco Itaú",
        "Banco Santander",
        "Banco Serfinanza",
        "Bancamía",
        "Banco Cooperativo Coopcentral",
        "Banco Credifinanciera",
        "Banco de las Microfinanzas",
        "Banco Mundo Mujer"
    ]
    
    # Obtener una sesión de base de datos
    db = next(get_db())
    
    try:
        print("Creando bancos de prueba...")
        
        for nombre_banco in bancos_colombianos:
            # Verificar si el banco ya existe
            existing_banco = db.query(Banco).filter(Banco.nombre == nombre_banco).first()
            
            if not existing_banco:
                nuevo_banco = Banco(nombre=nombre_banco)
                db.add(nuevo_banco)
                print(f"✓ Agregado: {nombre_banco}")
            else:
                print(f"- Ya existe: {nombre_banco}")
        
        # Confirmar los cambios
        db.commit()
        print(f"\n✅ Se han creado los bancos exitosamente!")
        
        # Mostrar todos los bancos en la base de datos
        bancos = db.query(Banco).all()
        print(f"\nTotal de bancos en la base de datos: {len(bancos)}")
        for banco in bancos:
            print(f"  - {banco.id}: {banco.nombre}")
            
    except Exception as e:
        print(f"❌ Error al crear bancos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_banks()
