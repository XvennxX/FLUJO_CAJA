#!/usr/bin/env python3
"""
Script simple para verificar datos de conciliación usando SQL directo
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

def verificar_datos():
    """Verificar datos necesarios para conciliación"""
    
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        print("=" * 60)
        print("VERIFICACIÓN DE DATOS PARA CONCILIACIÓN")
        print("=" * 60)
        
        # 1. Verificar empresas
        print("\n1. EMPRESAS DISPONIBLES:")
        result = conn.execute(text("SELECT id, nombre FROM companias LIMIT 5"))
        empresas = result.fetchall()
        
        if empresas:
            for empresa in empresas:
                print(f"   • ID: {empresa[0]} - {empresa[1]}")
        else:
            print("   ❌ No hay empresas en la base de datos")
            
        # Contar total de empresas
        result = conn.execute(text("SELECT COUNT(*) FROM companias"))
        total_empresas = result.fetchone()[0]
        print(f"   📊 Total empresas: {total_empresas}")
        
        # 2. Verificar transacciones para hoy
        print(f"\n2. TRANSACCIONES PARA HOY:")
        
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN area = 'PAGADURIA' THEN 1 ELSE 0 END) as pagaduria,
                SUM(CASE WHEN area = 'TESORERIA' THEN 1 ELSE 0 END) as tesoreria,
                COUNT(DISTINCT compania_id) as empresas_con_transacciones
            FROM transacciones_flujo_caja 
            WHERE DATE(fecha) = CURDATE()
        """))
        
        resultado = result.fetchone()
        print(f"   📈 Total transacciones: {resultado[0]}")
        print(f"   💼 Pagaduría: {resultado[1]}")
        print(f"   🏦 Tesorería: {resultado[2]}")
        print(f"   🏢 Empresas con transacciones: {resultado[3]}")
        
        # 3. Verificar transacciones de los últimos días
        print(f"\n3. TRANSACCIONES ÚLTIMOS 7 DÍAS:")
        
        result = conn.execute(text("""
            SELECT 
                DATE(fecha) as dia,
                COUNT(*) as total,
                COUNT(DISTINCT compania_id) as empresas
            FROM transacciones_flujo_caja 
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha)
            ORDER BY fecha DESC
            LIMIT 7
        """))
        
        resultado_semana = result.fetchall()
        
        if resultado_semana:
            for row in resultado_semana:
                print(f"   📅 {row[0]}: {row[1]} transacciones de {row[2]} empresas")
        else:
            print("   ❌ No hay transacciones en los últimos 7 días")
            
        # 4. Si no hay transacciones para hoy, crear algunas de prueba
        if resultado[0] == 0:
            print(f"\n4. CREANDO TRANSACCIONES DE PRUEBA:")
            print("   ⚠️  No hay transacciones para hoy. ¿Quieres crear algunas de prueba?")
            print("   💡 Sugerencia: Ejecutar el script de datos de prueba primero")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    verificar_datos()