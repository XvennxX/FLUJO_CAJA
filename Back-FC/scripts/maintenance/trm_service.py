#!/usr/bin/env python3
"""
Servicio automático de actualización TRM
Ejecuta la actualización cada 30 minutos durante horario laboral
"""

import time
import schedule
import sys
import os
from datetime import date, datetime, timedelta

# Agregar el directorio actual al path
sys.path.append('.')

# Importar las clases necesarias
from scripts.trm.trm_scraper import TRMScraper
from app.core.database import SessionLocal
from app.models.trm import TRM

class TRMService:
    def __init__(self):
        self.scraper = TRMScraper()
        
    def is_business_day(self, check_date):
        """Verificar si es día hábil (lunes a viernes)"""
        return check_date.weekday() < 5
    
    def update_missing_trms(self):
        """Actualizar TRMs faltantes"""
        print(f"🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Verificando TRMs faltantes...")
        
        try:
            db = SessionLocal()
            
            # Obtener la última TRM
            latest_trm = db.query(TRM).order_by(TRM.fecha.desc()).first()
            
            if not latest_trm:
                print("⚠️ No hay TRMs en la base de datos")
                return
            
            # Verificar desde la última fecha hasta hoy
            current_date = latest_trm.fecha + timedelta(days=1)
            today = date.today()
            updated_count = 0
            
            while current_date <= today:
                if self.is_business_day(current_date):
                    # Verificar si ya existe
                    existing = db.query(TRM).filter(TRM.fecha == current_date).first()
                    
                    if not existing:
                        print(f"🎯 Actualizando TRM para: {current_date}")
                        success = self.scraper.update_daily_trm(current_date)
                        
                        if success:
                            updated_count += 1
                            print(f"✅ TRM actualizada: {current_date}")
                        else:
                            print(f"❌ No se pudo obtener TRM para: {current_date}")
                
                current_date += timedelta(days=1)
            
            if updated_count == 0:
                print("✨ Todas las TRMs están actualizadas")
            else:
                print(f"✅ Se actualizaron {updated_count} TRMs")
                
        except Exception as e:
            print(f"❌ Error actualizando TRMs: {e}")
        finally:
            if 'db' in locals():
                db.close()
    
    def run_service(self):
        """Ejecutar el servicio automático"""
        print("🚀 Iniciando servicio automático TRM...")
        print("⏰ Ejecutándose cada 30 minutos de 8:00 AM a 6:00 PM")
        
        # Programar ejecución cada 30 minutos durante horario laboral
        schedule.every(30).minutes.do(self.update_missing_trms)
        
        # Ejecutar inmediatamente al iniciar
        self.update_missing_trms()
        
        while True:
            try:
                # Solo ejecutar durante horario laboral (8 AM - 6 PM)
                current_hour = datetime.now().hour
                if 8 <= current_hour <= 18:
                    schedule.run_pending()
                
                time.sleep(60)  # Verificar cada minuto
                
            except KeyboardInterrupt:
                print("\n🛑 Servicio detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error en el servicio: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    service = TRMService()
    service.run_service()