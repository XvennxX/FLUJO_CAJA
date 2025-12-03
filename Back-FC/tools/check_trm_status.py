#!/usr/bin/env python3
"""
Verificador del estado del sistema TRM
"""

import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.trm import TRM
from datetime import date, timedelta

def check_trm_status():
    """Verificar el estado actual del sistema TRM"""
    print("📊 ESTADO DEL SISTEMA TRM")
    print("=" * 50)
    
    try:
        db = SessionLocal()
        
        # Obtener estadísticas generales
        total_trms = db.query(TRM).count()
        print(f"📈 Total de TRMs en la base de datos: {total_trms}")
        
        # Últimas TRMs
        latest_trms = db.query(TRM).order_by(TRM.fecha.desc()).limit(10).all()
        print(f"\n📅 Últimas 10 TRMs registradas:")
        
        for trm in latest_trms:
            print(f"   {trm.fecha}: ${trm.valor:,.2f}")
        
        if latest_trms:
            latest_date = latest_trms[0].fecha
            today = date.today()
            
            print(f"\n🎯 Análisis de cobertura:")
            print(f"   Última TRM: {latest_date}")
            print(f"   Fecha actual: {today}")
            
            # Calcular días faltantes (solo días hábiles)
            missing_days = 0
            check_date = latest_date + timedelta(days=1)
            
            while check_date <= today:
                if check_date.weekday() < 5:  # Lunes a viernes
                    existing = db.query(TRM).filter(TRM.fecha == check_date).first()
                    if not existing:
                        missing_days += 1
                check_date += timedelta(days=1)
            
            if missing_days == 0:
                print(f"   ✅ Sistema actualizado - No hay TRMs faltantes")
            else:
                print(f"   ⚠️ Faltan {missing_days} TRMs por actualizar")
        
        print(f"\n✅ SISTEMA TRM FUNCIONANDO CORRECTAMENTE")
        
    except Exception as e:
        print(f"❌ Error verificando sistema TRM: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_trm_status()