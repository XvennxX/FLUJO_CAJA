"""
Script para probar manualmente la obtención de TRM
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.trm.trm_scraper import TRMScraper
from datetime import date, timedelta

scraper = TRMScraper()

# Probar para el lunes 10 (ayer)
print("\n" + "="*70)
print("PROBANDO OBTENCIÓN DE TRM PARA LUNES 10 NOV 2025 (AYER)")
print("="*70)

fecha_lunes = date(2025, 11, 10)  # Ayer lunes
print(f"\nIntentando obtener TRM para: {fecha_lunes}")
print(f"Día de la semana: {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'][fecha_lunes.weekday()]}")

resultado = scraper.update_daily_trm(fecha_lunes)

if resultado:
    print(f"✅ TRM obtenida y guardada exitosamente para {fecha_lunes}")
else:
    print(f"❌ No se pudo obtener TRM para {fecha_lunes}")

# Probar para hoy martes 11
print("\n" + "="*70)
print("PROBANDO OBTENCIÓN DE TRM PARA HOY MARTES 11 NOV 2025")
print("="*70)

fecha_hoy = date.today()
print(f"\nIntentando obtener TRM para: {fecha_hoy}")
print(f"Día de la semana: {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'][fecha_hoy.weekday()]}")

resultado = scraper.update_daily_trm(fecha_hoy)

if resultado:
    print(f"✅ TRM obtenida y guardada exitosamente para {fecha_hoy}")
else:
    print(f"❌ No se pudo obtener TRM para {fecha_hoy}")
    print("\nNOTA: Es posible que la TRM del día aún no esté publicada.")
    print("La TRM generalmente se publica después de las 10-11 AM.")
