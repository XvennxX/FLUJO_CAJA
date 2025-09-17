#!/usr/bin/env python3
"""
Verificar festivos específicos
"""

import sys
import os
from datetime import date

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.dias_festivos import DiaFestivo

def main():
    db = next(get_db())
    
    # Verificar fechas específicas alrededor del 17 de noviembre 2025
    fechas_verificar = [
        date(2025, 11, 15), # Sábado
        date(2025, 11, 16), # Domingo  
        date(2025, 11, 17), # Lunes
        date(2025, 11, 18), # Martes
        date(2025, 11, 19), # Miércoles
    ]
    
    print("=== VERIFICAR FESTIVOS NOVIEMBRE 2025 ===")
    
    for fecha in fechas_verificar:
        festivo = db.query(DiaFestivo).filter(DiaFestivo.fecha == fecha).first()
        nombre_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][fecha.weekday()]
        
        if festivo:
            print(f"{nombre_dia} {fecha}: ❌ FESTIVO - {festivo.nombre}")
        else:
            print(f"{nombre_dia} {fecha}: ✅ Normal")
    
    # Mostrar todos los festivos de noviembre 2025
    print("\n=== TODOS LOS FESTIVOS NOVIEMBRE 2025 ===")
    festivos_nov = db.query(DiaFestivo).filter(
        DiaFestivo.fecha >= date(2025, 11, 1),
        DiaFestivo.fecha <= date(2025, 11, 30)
    ).all()
    
    for festivo in festivos_nov:
        nombre_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][festivo.fecha.weekday()]
        print(f"{nombre_dia} {festivo.fecha}: {festivo.nombre}")

if __name__ == "__main__":
    main()