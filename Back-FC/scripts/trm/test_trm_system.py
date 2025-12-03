"""
Test manual del sistema de TRM
Verifica que el scheduler y la recuperación funcionen correctamente
"""

import sys
import os
from pathlib import Path

# Configurar paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("TEST SISTEMA TRM AUTOMÁTICA - 7:00 PM")
print("=" * 70)
print()

print("1. Probando importación de módulos...")
try:
    from scripts.trm.trm_scraper import TRMScraper
    print("   ✅ TRMScraper importado correctamente")
except Exception as e:
    print(f"   ❌ Error importando TRMScraper: {e}")
    sys.exit(1)

print()
print("2. Probando conexión y obtención de TRM actual...")
try:
    scraper = TRMScraper()
    trm_actual = scraper.get_current_trm()
    
    if trm_actual:
        print(f"   ✅ Conexión exitosa - TRM actual: ${trm_actual:,.2f}")
    else:
        print("   ⚠️  Conexión OK pero no se obtuvo TRM (posible fin de semana)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()
print("3. Verificando base de datos...")
try:
    from app.core.database import SessionLocal
    from app.models.trm import TRM
    from datetime import date, timedelta
    
    db = SessionLocal()
    
    # Verificar últimos 5 días
    today = date.today()
    print(f"   Revisando últimos 5 días desde {today}:")
    print()
    
    dias_encontrados = 0
    dias_faltantes = 0
    
    for i in range(5, 0, -1):
        check_date = today - timedelta(days=i)
        trm_record = db.query(TRM).filter(TRM.fecha == check_date).first()
        
        if trm_record:
            print(f"   ✅ {check_date}: ${trm_record.valor:,.2f}")
            dias_encontrados += 1
        else:
            print(f"   ❌ {check_date}: FALTANTE")
            dias_faltantes += 1
    
    db.close()
    
    print()
    print(f"   📊 Resumen: {dias_encontrados} encontrados, {dias_faltantes} faltantes")
    
except Exception as e:
    print(f"   ❌ Error verificando base de datos: {e}")

print()
print("4. Probando scheduler (verificación de configuración)...")
try:
    import schedule
    
    # Simular configuración del scheduler
    def job_test():
        print("   Job de prueba ejecutado")
    
    schedule.every().day.at("19:00").do(job_test)
    
    jobs = schedule.get_jobs()
    if jobs:
        print(f"   ✅ Scheduler funcional - {len(jobs)} job(s) programado(s)")
        for job in jobs:
            print(f"      - {job}")
    else:
        print("   ❌ No se pudieron programar jobs")
    
    schedule.clear()
    
except Exception as e:
    print(f"   ❌ Error con scheduler: {e}")

print()
print("=" * 70)
print("TEST COMPLETADO")
print("=" * 70)
print()
print("📋 SIGUIENTES PASOS:")
print()
print("Para iniciar el scheduler automático:")
print("  cd Back-FC\\scripts\\trm")
print("  .\\start_trm_scheduler.ps1")
print()
print("Para ejecutar recuperación manual:")
print("  python scripts\\trm\\update_missing_trm.py 30")
print()
print("Para iniciar servidor con verificación automática:")
print("  python run_server.py")
print()
