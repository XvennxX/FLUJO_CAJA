"""
Script para crear datos iniciales en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import *
from app.services.auth_service import get_password_hash

def create_initial_data():
    """Crear datos iniciales en la base de datos"""
    db = SessionLocal()
    
    try:
        # Verificar usuarios existentes (no crear nuevos usuarios ya que existen)
        existing_users = db.query(Usuario).count()
        if existing_users > 0:
            print(f"✅ Se encontraron {existing_users} usuarios existentes en la base de datos")
        else:
            print("ℹ️  No se encontraron usuarios en la base de datos")
        
        # Crear bancos
        bancos_data = [
            {"nombre": "BANCO DAVIVIENDA"},
            {"nombre": "BANCO REPUBLICA"},
            {"nombre": "CITIBANK COMP"},
            {"nombre": "DAVIVIENDA INT"}
        ]
        
        for banco_data in bancos_data:
            existing_banco = db.query(Banco).filter(Banco.nombre == banco_data["nombre"]).first()
            if not existing_banco:
                banco = Banco(**banco_data)
                db.add(banco)
        
        # Crear compañías
        companias_data = [
            {"nombre": "CAPITALIZADORA", "tipo": TipoCompania.capitalizadora},
            {"nombre": "SEGUROS BOLÍVAR", "tipo": TipoCompania.bolivar},
            {"nombre": "COMERCIALES", "tipo": TipoCompania.comerciales}
        ]
        
        for compania_data in companias_data:
            existing_compania = db.query(Compania).filter(Compania.nombre == compania_data["nombre"]).first()
            if not existing_compania:
                compania = Compania(**compania_data)
                db.add(compania)
        
        # Crear conceptos de flujo de caja
        conceptos_data = [
            {"nombre": "SALDO DIA ANTERIOR", "tipo": TipoMovimiento.neutral, "codigo": ""},
            {"nombre": "INGRESO", "tipo": TipoMovimiento.ingreso, "codigo": "I"},
            {"nombre": "CONSUMO NACIONAL", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "VENTAN PROVEEDORES", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "NOMINA ADMINISTRATIVA", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "NOMINA PENSIONES", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "OTROS PAGOS", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "OTROS IMPTOS", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "RECAUDOS LIBERTADOR", "tipo": TipoMovimiento.ingreso, "codigo": "I"},
            {"nombre": "INGRESOS INTERESES", "tipo": TipoMovimiento.ingreso, "codigo": "I"},
            {"nombre": "PAGOS INTERCOMPAÑÍAS", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "COMPRA TÍTULOS", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "VENTA TÍTULOS", "tipo": TipoMovimiento.ingreso, "codigo": "I"},
            {"nombre": "RENDIMIENTOS", "tipo": TipoMovimiento.ingreso, "codigo": "I"},
            {"nombre": "COMISIONES", "tipo": TipoMovimiento.egreso, "codigo": "E"},
            {"nombre": "IMPUESTOS", "tipo": TipoMovimiento.egreso, "codigo": "E"}
        ]
        
        for concepto_data in conceptos_data:
            existing_concepto = db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.nombre == concepto_data["nombre"]
            ).first()
            if not existing_concepto:
                concepto = ConceptoFlujoCaja(**concepto_data)
                db.add(concepto)
        
        db.commit()
        print("✅ Datos iniciales creados exitosamente")
        
    except Exception as e:
        print(f"❌ Error al crear datos iniciales: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando datos iniciales...")
    create_initial_data()
