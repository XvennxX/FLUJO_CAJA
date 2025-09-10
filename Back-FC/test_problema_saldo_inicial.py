import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.database import engine
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.schemas.flujo_caja import AreaTransaccionSchema

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_problema_saldo_inicial():
    db = SessionLocal()
    try:
        print("=== TEST DETALLADO PROBLEMA SALDO INICIAL ===")
        
        # 1. Verificar que existe SALDO FINAL del día 9
        fecha_dia_9 = date(2025, 9, 9)
        fecha_dia_10 = date(2025, 9, 10)
        
        query = text("""
        SELECT DISTINCT cuenta_id 
        FROM transacciones_flujo_caja 
        WHERE fecha = :fecha 
        AND concepto_id = 51 
        AND area = 'tesoreria'
        """)
        
        result = db.execute(query, {"fecha": fecha_dia_9})
        cuentas_dia_9 = [row[0] for row in result.fetchall()]
        
        print(f"1. Cuentas con SALDO FINAL en día 9: {cuentas_dia_9}")
        
        if not cuentas_dia_9:
            print("❌ ERROR: No hay cuentas con SALDO FINAL en día 9")
            return
        
        # 2. Verificar si hay SALDO INICIAL en día 10
        query = text("""
        SELECT COUNT(*) as cantidad
        FROM transacciones_flujo_caja 
        WHERE fecha = :fecha 
        AND concepto_id = 1 
        AND area = 'tesoreria'
        """)
        
        result = db.execute(query, {"fecha": fecha_dia_10})
        count_saldo_inicial = result.fetchone()[0]
        
        print(f"2. Cantidad de SALDO INICIAL en día 10: {count_saldo_inicial}")
        
        # 3. Ejecutar la función directamente paso a paso
        print("\n3. Ejecutando función _procesar_saldo_inicial_automatico paso a paso...")
        
        service = DependenciasFlujoCajaService(db)
        
        # Simular la llamada exacta
        usuario_id = 6
        compania_id = 1
        
        print(f"   - Fecha objetivo: {fecha_dia_10}")
        print(f"   - Usuario ID: {usuario_id}")
        print(f"   - Compañía ID: {compania_id}")
        
        # Ejecutar con logging detallado
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Ejecutar la función
        resultado = service._procesar_saldo_inicial_automatico(
            fecha=fecha_dia_10,
            usuario_id=usuario_id,
            compania_id=compania_id
        )
        
        print(f"4. Resultado de la función: {resultado}")
        
        # 5. Verificar si ahora existe en la base de datos
        result = db.execute(query, {"fecha": fecha_dia_10})
        count_saldo_inicial_despues = result.fetchone()[0]
        
        print(f"5. Cantidad de SALDO INICIAL en día 10 DESPUÉS: {count_saldo_inicial_despues}")
        
        # 6. Si no se creó, vamos a hacer debug más profundo
        if count_saldo_inicial_despues == 0:
            print("\n6. DEBUG PROFUNDO - La función no creó registros...")
            
            # Verificar las cuentas exactas que debería procesar
            SALDO_FINAL_CUENTAS_ID = 51
            fecha_anterior = fecha_dia_10 - timedelta(days=1)
            
            query_debug = text("""
            SELECT DISTINCT cuenta_id 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha_anterior 
            AND concepto_id = :concepto_id 
            AND area = 'tesoreria'
            """)
            
            result = db.execute(query_debug, {
                "fecha_anterior": fecha_anterior,
                "concepto_id": SALDO_FINAL_CUENTAS_ID
            })
            cuentas_encontradas = [row[0] for row in result.fetchall()]
            
            print(f"   - Cuentas que debería procesar: {cuentas_encontradas}")
            
            # Verificar si existe SALDO INICIAL para cada cuenta
            for cuenta in cuentas_encontradas:
                query_existe = text("""
                SELECT COUNT(*) 
                FROM transacciones_flujo_caja 
                WHERE fecha = :fecha 
                AND concepto_id = 1 
                AND cuenta_id = :cuenta_id 
                AND area = 'tesoreria'
                """)
                
                result = db.execute(query_existe, {
                    "fecha": fecha_dia_10,
                    "cuenta_id": cuenta
                })
                existe = result.fetchone()[0] > 0
                
                print(f"   - Cuenta {cuenta}: SALDO INICIAL existe = {existe}")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_problema_saldo_inicial()
