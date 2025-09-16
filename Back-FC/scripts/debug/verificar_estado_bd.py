import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.database import engine

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verificar_estado_base_datos():
    db = SessionLocal()
    try:
        print("=== VERIFICACIÓN ESTADO BASE DE DATOS ===")
        
        # Verificar varios días
        fechas_a_verificar = [
            date(2025, 9, 8),   # Día 8
            date(2025, 9, 9),   # Día 9 (hoy)
            date(2025, 9, 10),  # Día 10 (mañana)
            date(2025, 9, 11),  # Día 11
            date(2025, 9, 12),  # Día 12
        ]
        
        for fecha in fechas_a_verificar:
            print(f"\n📅 FECHA: {fecha}")
            
            # SALDO INICIAL (concepto_id = 1)
            query_inicial = text("""
            SELECT 
                t.id,
                t.concepto_id,
                c.nombre as concepto_nombre,
                t.cuenta_id,
                t.monto,
                t.created_at
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.concepto_id = 1
            AND t.area = 'tesoreria'
            ORDER BY t.cuenta_id
            """)
            
            result = db.execute(query_inicial, {"fecha": fecha})
            saldos_inicial = result.fetchall()
            
            if saldos_inicial:
                print("  ✅ SALDO INICIAL encontrado:")
                for row in saldos_inicial:
                    print(f"    - ID: {row[0]}, Cuenta: {row[3]}, Monto: ${row[4]}, Creado: {row[5]}")
            else:
                print("  ❌ NO hay SALDO INICIAL")
            
            # SALDO FINAL CUENTAS (concepto_id = 51)
            query_final = text("""
            SELECT 
                t.id,
                t.concepto_id,
                c.nombre as concepto_nombre,
                t.cuenta_id,
                t.monto,
                t.created_at
            FROM transacciones_flujo_caja t
            JOIN conceptos_flujo_caja c ON t.concepto_id = c.id
            WHERE t.fecha = :fecha
            AND t.concepto_id = 51
            AND t.area = 'tesoreria'
            ORDER BY t.cuenta_id
            """)
            
            result = db.execute(query_final, {"fecha": fecha})
            saldos_final = result.fetchall()
            
            if saldos_final:
                print("  ✅ SALDO FINAL CUENTAS encontrado:")
                for row in saldos_final:
                    print(f"    - ID: {row[0]}, Cuenta: {row[3]}, Monto: ${row[4]}, Creado: {row[5]}")
            else:
                print("  ❌ NO hay SALDO FINAL CUENTAS")
        
        # Verificar si hay patrones en las transacciones
        print(f"\n=== RESUMEN GENERAL SALDO INICIAL ===")
        query_resumen = text("""
        SELECT 
            t.fecha,
            COUNT(*) as cantidad,
            GROUP_CONCAT(t.cuenta_id) as cuentas,
            SUM(t.monto) as total_monto
        FROM transacciones_flujo_caja t
        WHERE t.concepto_id = 1
        AND t.area = 'tesoreria'
        GROUP BY t.fecha
        ORDER BY t.fecha
        """)
        
        result = db.execute(query_resumen)
        resumen = result.fetchall()
        
        if resumen:
            print("Fechas con SALDO INICIAL:")
            for row in resumen:
                print(f"  - {row[0]}: {row[1]} registros, Cuentas: {row[2]}, Total: ${row[3]}")
        else:
            print("❌ NO hay ningún SALDO INICIAL en la base de datos")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_estado_base_datos()
