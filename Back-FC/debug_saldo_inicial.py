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

def debug_saldo_inicial():
    db = SessionLocal()
    try:
        print("=== DEBUG SALDO INICIAL AUTOMÁTICO ===")
        
        # Verificar data del día 9 (día anterior)
        print("\n1. Verificando SALDO FINAL del día 9...")
        fecha_anterior = date(2025, 9, 9)
        
        query = text("""
        SELECT 
            t.concepto_id,
            c.nombre as concepto_nombre,
            t.cuenta_id,
            t.monto
        FROM transacciones_flujo_caja t
        JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
        WHERE t.fecha = :fecha_anterior
        AND t.concepto_id = 51
        AND t.area = 'tesoreria'
        ORDER BY t.cuenta_id
        """)
        
        result = db.execute(query, {"fecha_anterior": fecha_anterior})
        saldos_dia_9 = result.fetchall()
        
        print(f"SALDO FINAL encontrados para día 9:")
        for row in saldos_dia_9:
            print(f"  - Concepto: {row[1]} (ID: {row[0]})")
            print(f"    Cuenta ID: {row[2]}")
            print(f"    Monto: ${row[3]}")
        
        # Verificar si existe SALDO INICIAL en día 10
        print("\n2. Verificando SALDO INICIAL del día 10...")
        fecha_actual = date(2025, 9, 10)
        
        query = text("""
        SELECT 
            t.concepto_id,
            c.nombre as concepto_nombre,
            t.cuenta_id,
            t.monto
        FROM transacciones_flujo_caja t
        JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
        WHERE t.fecha = :fecha_actual
        AND t.concepto_id = 1
        AND t.area = 'tesoreria'
        ORDER BY t.cuenta_id
        """)
        
        result = db.execute(query, {"fecha_actual": fecha_actual})
        saldos_dia_10 = result.fetchall()
        
        print(f"SALDO INICIAL encontrados para día 10:")
        if not saldos_dia_10:
            print("  - NO HAY SALDO INICIAL para día 10")
        else:
            for row in saldos_dia_10:
                print(f"  - Concepto: {row[1]} (ID: {row[0]})")
                print(f"    Cuenta ID: {row[2]}")
                print(f"    Monto: ${row[3]}")
        
        # Probar directamente la función _procesar_saldo_inicial_automatico
        print("\n3. Ejecutando directamente _procesar_saldo_inicial_automatico...")
        
        service = DependenciasFlujoCajaService(db)
        usuario_id = 6
        compania_id = 1
        area = AreaTransaccionSchema.tesoreria
        
        # Llamar directamente al método
        result = service._procesar_saldo_inicial_automatico(
            fecha=fecha_actual,
            usuario_id=usuario_id,
            compania_id=compania_id
        )
        
        print(f"Resultado de _procesar_saldo_inicial_automatico: {result}")
        
        # Verificar nuevamente después de ejecutar
        print("\n4. Verificando SALDO INICIAL del día 10 después del procesamiento...")
        result = db.execute(query, {"fecha_actual": fecha_actual})
        saldos_dia_10_despues = result.fetchall()
        
        print(f"SALDO INICIAL encontrados para día 10 DESPUÉS:")
        if not saldos_dia_10_despues:
            print("  - AÚN NO HAY SALDO INICIAL para día 10")
        else:
            for row in saldos_dia_10_despues:
                print(f"  - Concepto: {row[1]} (ID: {row[0]})")
                print(f"    Cuenta ID: {row[2]}")
                print(f"    Monto: ${row[3]}")
                
    except Exception as e:
        print(f"Error en debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_saldo_inicial()
