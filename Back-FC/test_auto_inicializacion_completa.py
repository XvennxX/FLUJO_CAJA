import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.database import engine
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_auto_inicializacion_completa():
    db = SessionLocal()
    try:
        print("=== TEST AUTO-INICIALIZACIÓN COMPLETA ===")
        
        # 1. Limpiar cualquier SALDO INICIAL de días futuros para empezar limpio
        fechas_futuras = [
            date(2025, 9, 10),
            date(2025, 9, 11),
            date(2025, 9, 12),
            date(2025, 9, 13),
        ]
        
        for fecha in fechas_futuras:
            delete_query = text("""
            DELETE FROM transacciones_flujo_caja 
            WHERE fecha = :fecha 
            AND concepto_id = 1 
            AND area = 'tesoreria'
            """)
            db.execute(delete_query, {"fecha": fecha})
        
        db.commit()
        print("✅ Limpieza inicial completada")
        
        # 2. Verificar que tenemos SALDO FINAL en día 9
        query_saldo_final = text("""
        SELECT cuenta_id, monto 
        FROM transacciones_flujo_caja 
        WHERE fecha = :fecha 
        AND concepto_id = 51 
        AND area = 'tesoreria'
        """)
        
        result = db.execute(query_saldo_final, {"fecha": date(2025, 9, 9)})
        saldos_dia_9 = result.fetchall()
        
        print(f"📊 SALDO FINAL día 9: {[(row[0], f'${row[1]}') for row in saldos_dia_9]}")
        
        if not saldos_dia_9:
            print("❌ ERROR: No hay SALDO FINAL en día 9. Crear primero.")
            return
        
        # 3. Probar auto-inicialización para varios días consecutivos
        dependencias_service = DependenciasFlujoCajaService(db)
        usuario_id = 6
        compania_id = 1
        
        for fecha in fechas_futuras:
            print(f"\n🗓️ Procesando fecha: {fecha}")
            
            # Verificar ANTES
            query_count = text("""
            SELECT COUNT(*) as cantidad 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha 
            AND concepto_id = 1 
            AND area = 'tesoreria'
            """)
            
            result = db.execute(query_count, {"fecha": fecha})
            count_antes = result.fetchone()[0]
            print(f"   ANTES: {count_antes} SALDO INICIAL")
            
            # Ejecutar auto-inicialización
            resultado = dependencias_service._procesar_saldo_inicial_automatico(
                fecha=fecha,
                usuario_id=usuario_id,
                compania_id=compania_id
            )
            
            print(f"   RESULTADO: {len(resultado)} transacciones procesadas")
            
            # Verificar DESPUÉS
            result = db.execute(query_count, {"fecha": fecha})
            count_despues = result.fetchone()[0]
            print(f"   DESPUÉS: {count_despues} SALDO INICIAL")
            
            # Mostrar detalles de los SALDO INICIAL creados
            if count_despues > 0:
                query_detalles = text("""
                SELECT cuenta_id, monto, created_at 
                FROM transacciones_flujo_caja 
                WHERE fecha = :fecha 
                AND concepto_id = 1 
                AND area = 'tesoreria'
                ORDER BY cuenta_id
                """)
                
                result = db.execute(query_detalles, {"fecha": fecha})
                detalles = result.fetchall()
                
                for row in detalles:
                    print(f"     ✅ Cuenta {row[0]}: ${row[1]} (creado: {row[2]})")
        
        # 4. Verificar continuidad: cada día siguiente debe tener SALDO INICIAL = SALDO FINAL del día anterior
        print(f"\n🔗 Verificando continuidad de saldos...")
        
        for i, fecha in enumerate(fechas_futuras[:-1]):  # No incluir el último día
            fecha_siguiente = fechas_futuras[i + 1]
            
            # Obtener SALDO FINAL del día actual
            query_final = text("""
            SELECT cuenta_id, monto 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha 
            AND concepto_id = 51 
            AND area = 'tesoreria'
            ORDER BY cuenta_id
            """)
            
            result = db.execute(query_final, {"fecha": fecha})
            saldos_final = {row[0]: row[1] for row in result.fetchall()}
            
            # Obtener SALDO INICIAL del día siguiente
            query_inicial = text("""
            SELECT cuenta_id, monto 
            FROM transacciones_flujo_caja 
            WHERE fecha = :fecha 
            AND concepto_id = 1 
            AND area = 'tesoreria'
            ORDER BY cuenta_id
            """)
            
            result = db.execute(query_inicial, {"fecha": fecha_siguiente})
            saldos_inicial = {row[0]: row[1] for row in result.fetchall()}
            
            print(f"   {fecha} → {fecha_siguiente}")
            
            # Verificar que coincidan
            for cuenta_id in saldos_final:
                saldo_final = saldos_final.get(cuenta_id, 0)
                saldo_inicial = saldos_inicial.get(cuenta_id, 0)
                
                if saldo_final == saldo_inicial:
                    print(f"     ✅ Cuenta {cuenta_id}: ${saldo_final} → ${saldo_inicial}")
                else:
                    print(f"     ❌ Cuenta {cuenta_id}: ${saldo_final} → ${saldo_inicial} (NO COINCIDE)")
        
        print(f"\n🎉 Test completado!")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auto_inicializacion_completa()
