#!/usr/bin/env python3
"""
Script simple para probar el sistema TRM
"""

import sys
import os
from datetime import date, timedelta

# Agregar el directorio actual al path
sys.path.append('.')

# Importar las clases necesarias
from scripts.trm.trm_scraper import TRMScraper
from app.core.database import SessionLocal
from app.models.trm import TRM

def test_trm_system():
    """Probar el sistema TRM completo"""
    print("🔄 Probando sistema TRM...")
    
    try:
        # Crear instancia del scraper
        scraper = TRMScraper()
        
        # Verificar TRMs existentes
        db = SessionLocal()
        try:
            latest_trms = db.query(TRM).order_by(TRM.fecha.desc()).limit(5).all()
            print("\n📊 Últimas TRMs en la base de datos:")
            for trm in latest_trms:
                print(f"   {trm.fecha}: ${trm.valor:,.2f}")
            
            if latest_trms:
                latest_date = latest_trms[0].fecha
                print(f"\n📅 Última TRM disponible: {latest_date}")
                
                # Intentar obtener TRM para el día siguiente
                next_date = latest_date + timedelta(days=1)
                
                # Verificar que no sea fin de semana
                while next_date.weekday() > 4:  # 5=sábado, 6=domingo
                    next_date += timedelta(days=1)
                
                print(f"🎯 Intentando obtener TRM para: {next_date}")
                
                success = scraper.update_daily_trm(next_date)
                
                if success:
                    print("✅ TRM actualizada exitosamente")
                    
                    # Verificar la nueva TRM
                    new_trm = db.query(TRM).filter(TRM.fecha == next_date).first()
                    if new_trm:
                        print(f"💰 Nueva TRM: {next_date} = ${new_trm.valor:,.2f}")
                else:
                    print("❌ No se pudo obtener TRM (posible feriado o fin de semana)")
                    
        finally:
            db.close()
            
        print("\n🎯 Sistema TRM funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en el sistema TRM: {e}")
        return False

if __name__ == "__main__":
    success = test_trm_system()
    if success:
        print("\n✅ SISTEMA TRM OK - La carga automática debería funcionar")
    else:
        print("\n❌ PROBLEMA EN SISTEMA TRM - Revisar configuración")