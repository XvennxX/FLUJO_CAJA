"""
Script de prueba para verificar la funcionalidad de TRM
"""

import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trm_scraper import TRMScraper
from app.core.database import SessionLocal
from app.models.trm import TRM

def test_trm_scraper():
    """
    Prueba el scraper de TRM
    """
    print("=" * 60)
    print("PRUEBA DEL SCRAPER DE TRM")
    print("=" * 60)
    
    scraper = TRMScraper()
    
    # Probar obtener TRM actual
    print("\n1. Probando obtención de TRM actual...")
    trm_value = scraper.get_current_trm()
    
    if trm_value:
        print(f"✅ TRM obtenida: {trm_value}")
    else:
        print("❌ No se pudo obtener TRM")
    
    # Probar guardar en base de datos
    print("\n2. Probando guardar en base de datos...")
    if trm_value:
        success = scraper.save_trm_to_database(date.today(), trm_value)
        if success:
            print("✅ TRM guardada en base de datos")
        else:
            print("❌ Error al guardar TRM en base de datos")
    
    # Probar actualización diaria completa
    print("\n3. Probando actualización diaria completa...")
    success = scraper.update_daily_trm()
    if success:
        print("✅ Actualización diaria exitosa")
    else:
        print("❌ Error en actualización diaria")

def test_database_operations():
    """
    Prueba las operaciones de base de datos
    """
    print("\n" + "=" * 60)
    print("PRUEBA DE OPERACIONES DE BASE DE DATOS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Insertar TRM de prueba
        print("\n1. Insertando TRM de prueba...")
        test_trm = TRM(
            fecha=date.today() - timedelta(days=1),
            valor=Decimal("4123.45")
        )
        
        # Verificar si ya existe
        existing = db.query(TRM).filter(TRM.fecha == test_trm.fecha).first()
        if existing:
            print(f"⚠️ Ya existe TRM para {test_trm.fecha}: {existing.valor}")
        else:
            db.add(test_trm)
            db.commit()
            print(f"✅ TRM de prueba insertada: {test_trm.fecha} = {test_trm.valor}")
        
        # Consultar TRMs existentes
        print("\n2. Consultando TRMs existentes...")
        trms = db.query(TRM).order_by(TRM.fecha.desc()).limit(5).all()
        
        if trms:
            print("📊 Últimas 5 TRMs:")
            for trm in trms:
                print(f"  {trm.fecha}: {trm.valor}")
        else:
            print("⚠️ No hay TRMs en la base de datos")
        
        # Consultar TRM más reciente
        print("\n3. Consultando TRM más reciente...")
        latest_trm = db.query(TRM).order_by(TRM.fecha.desc()).first()
        
        if latest_trm:
            print(f"✅ TRM más reciente: {latest_trm.fecha} = {latest_trm.valor}")
        else:
            print("⚠️ No hay TRM más reciente")
            
    except Exception as e:
        print(f"❌ Error en operaciones de base de datos: {e}")
        db.rollback()
    finally:
        db.close()

def test_manual_trm_values():
    """
    Prueba con valores manuales para verificar funcionalidad
    """
    print("\n" + "=" * 60)
    print("PRUEBA CON VALORES MANUALES")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Insertar varios valores de TRM para pruebas
        test_dates_values = [
            (date.today() - timedelta(days=7), Decimal("4100.25")),
            (date.today() - timedelta(days=6), Decimal("4105.50")),
            (date.today() - timedelta(days=5), Decimal("4110.75")),
            (date.today() - timedelta(days=4), Decimal("4115.00")),
            (date.today() - timedelta(days=3), Decimal("4120.25")),
        ]
        
        print("\n1. Insertando TRMs de prueba para los últimos 7 días...")
        
        for fecha, valor in test_dates_values:
            existing = db.query(TRM).filter(TRM.fecha == fecha).first()
            if not existing:
                trm = TRM(fecha=fecha, valor=valor)
                db.add(trm)
                print(f"✅ Insertada: {fecha} = {valor}")
            else:
                print(f"⚠️ Ya existe: {fecha} = {existing.valor}")
        
        db.commit()
        
        # Verificar datos insertados
        print("\n2. Verificando datos insertados...")
        all_trms = db.query(TRM).order_by(TRM.fecha.desc()).limit(10).all()
        
        print("📊 TRMs en base de datos:")
        for trm in all_trms:
            print(f"  {trm.fecha}: {trm.valor} (creada: {trm.fecha_creacion})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """
    Función principal de pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE FUNCIONALIDAD TRM")
    
    # Ejecutar pruebas
    test_manual_trm_values()
    test_database_operations()
    
    # Solo ejecutar scraper si hay conexión a internet
    try:
        test_trm_scraper()
    except Exception as e:
        print(f"\n⚠️ Saltando pruebas de scraper (sin conexión o error): {e}")
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
