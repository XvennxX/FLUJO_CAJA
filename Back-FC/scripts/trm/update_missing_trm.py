"""
Script manual para actualizar TRMs faltantes
Útil cuando el backend estuvo apagado varios días
"""

import sys
import os
from datetime import date, timedelta

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.trm.trm_scraper import TRMScraper
from app.core.database import SessionLocal
from app.models.trm import TRM

def update_missing_trm_for_days(days_back: int = 7):
    """
    Actualiza TRMs faltantes para los últimos N días
    
    Args:
        days_back: Número de días hacia atrás a verificar (default: 7)
    """
    print("=" * 60)
    print("ACTUALIZACION MANUAL DE TRMs FALTANTES")
    print("=" * 60)
    
    scraper = TRMScraper()
    today = date.today()
    
    print(f"Verificando últimos {days_back} días desde {today}")
    print("-" * 60)
    
    missing_count = 0
    updated_count = 0
    
    for i in range(days_back, 0, -1):
        check_date = today - timedelta(days=i)
        
        # Verificar si existe TRM para esta fecha
        db = SessionLocal()
        try:
            existing_trm = db.query(TRM).filter(TRM.fecha == check_date).first()
            
            if not existing_trm:
                print(f"❌ TRM faltante para {check_date}")
                missing_count += 1
                
                # Intentar actualizar
                print(f"   → Obteniendo TRM...")
                success = scraper.update_daily_trm(check_date)
                
                if success:
                    print(f"   ✅ TRM actualizada exitosamente")
                    updated_count += 1
                else:
                    print(f"   ❌ No se pudo obtener TRM (posible día no hábil)")
                    
            else:
                print(f"✅ TRM ya existe para {check_date}: ${existing_trm.valor:,.2f}")
                    
        finally:
            db.close()
    
    print("-" * 60)
    print(f"RESUMEN:")
    print(f"- TRMs faltantes encontradas: {missing_count}")
    print(f"- TRMs actualizadas exitosamente: {updated_count}")
    print(f"- TRMs no actualizadas: {missing_count - updated_count}")
    print("=" * 60)

def update_specific_date(fecha_str: str):
    """
    Actualiza TRM para una fecha específica
    
    Args:
        fecha_str: Fecha en formato YYYY-MM-DD
    """
    try:
        fecha = date.fromisoformat(fecha_str)
        print(f"Actualizando TRM para fecha específica: {fecha}")
        
        scraper = TRMScraper()
        success = scraper.update_daily_trm(fecha)
        
        if success:
            print(f"✅ TRM actualizada exitosamente para {fecha}")
        else:
            print(f"❌ No se pudo actualizar TRM para {fecha}")
            
    except ValueError:
        print(f"❌ Fecha inválida: {fecha_str}. Use formato YYYY-MM-DD")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Verificar si es una fecha (formato YYYY-MM-DD) o número de días
        if '-' in arg and len(arg) == 10:
            # Es una fecha específica
            update_specific_date(arg)
        else:
            # Es número de días
            try:
                days = int(arg)
                update_missing_trm_for_days(days)
            except ValueError:
                print(f"❌ Argumento inválido: {arg}. Use número de días o fecha YYYY-MM-DD")
    else:
        # Verificar últimos 7 días por defecto
        update_missing_trm_for_days(7)
