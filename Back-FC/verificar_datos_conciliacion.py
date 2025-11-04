#!/usr/bin/env python3
"""
Script para verificar los datos necesarios para la conciliación
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import SessionLocal
from app.models.compania import Compania
from app.models.transaccion_flujo_caja import TransaccionFlujoCaja
from app.models.conciliacion_contable import ConciliacionContable
from datetime import datetime, date

def verificar_datos():
    """Verificar datos necesarios para conciliación"""
    
    # Crear conexión a la base de datos    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("VERIFICACIÓN DE DATOS PARA CONCILIACIÓN")
        print("=" * 60)
        
        # 1. Verificar empresas
        print("\n1. EMPRESAS DISPONIBLES:")
        empresas = db.query(Compania).limit(10).all()
        
        if empresas:
            for empresa in empresas:
                print(f"   • ID: {empresa.id} - {empresa.nombre}")
        else:
            print("   ❌ No hay empresas en la base de datos")
            
        print(f"   📊 Total empresas: {len(empresas)}")
        
        # 2. Verificar transacciones para hoy
        print(f"\n2. TRANSACCIONES PARA HOY ({date.today()}):")
        
        # Contar transacciones por área
        resultado = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN area = 'PAGADURIA' THEN 1 ELSE 0 END) as pagaduria,
                SUM(CASE WHEN area = 'TESORERIA' THEN 1 ELSE 0 END) as tesoreria,
                COUNT(DISTINCT compania_id) as empresas_con_transacciones
            FROM transacciones_flujo_caja 
            WHERE DATE(fecha) = CURDATE()
        """)).fetchone()
        
        print(f"   📈 Total transacciones: {resultado.total}")
        print(f"   💼 Pagaduría: {resultado.pagaduria}")
        print(f"   🏦 Tesorería: {resultado.tesoreria}")
        print(f"   🏢 Empresas con transacciones: {resultado.empresas_con_transacciones}")
        
        # 3. Verificar si existen conciliaciones para hoy
        print(f"\n3. CONCILIACIONES EXISTENTES PARA HOY:")
        
        conciliaciones = db.query(ConciliacionContable).filter(
            ConciliacionContable.fecha == date.today()
        ).all()
        
        if conciliaciones:
            print(f"   ✅ Encontradas {len(conciliaciones)} conciliaciones")
            for conc in conciliaciones:
                print(f"      • Empresa ID {conc.compania_id}: ${conc.total_calculado:.2f}")
        else:
            print("   ❌ No hay conciliaciones registradas para hoy")
        
        # 4. Verificar transacciones de días anteriores
        print(f"\n4. TRANSACCIONES DE LOS ÚLTIMOS 7 DÍAS:")
        
        resultado_semana = db.execute(text("""
            SELECT 
                DATE(fecha) as dia,
                COUNT(*) as total,
                COUNT(DISTINCT compania_id) as empresas
            FROM transacciones_flujo_caja 
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(fecha)
            ORDER BY fecha DESC
            LIMIT 7
        """)).fetchall()
        
        if resultado_semana:
            for row in resultado_semana:
                print(f"   📅 {row.dia}: {row.total} transacciones de {row.empresas} empresas")
        else:
            print("   ❌ No hay transacciones en los últimos 7 días")
            
        print("\n" + "=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    verificar_datos()