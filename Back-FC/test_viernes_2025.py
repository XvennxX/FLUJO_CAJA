#!/usr/bin/env python3
"""
Test para verificar proyección de viernes en 2025
"""

import sys
import os
from datetime import date

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.dias_habiles_service import DiasHabilesService

def main():
    # Crear una instancia del servicio
    db = next(get_db())
    service = DiasHabilesService(db)
    
    # Probar viernes de 2025
    viernes_2025 = [
        date(2025, 9, 19),  # Viernes 19 septiembre 2025 (próximo viernes)
        date(2025, 9, 26),  # Viernes 26 septiembre 2025
        date(2025, 10, 3),  # Viernes 3 octubre 2025
        date(2025, 11, 7),  # Viernes 7 noviembre 2025
        date(2025, 11, 14), # Viernes 14 noviembre 2025
    ]
    
    print("=== TEST VIERNES 2025 ===")
    print("Verificando que viernes proyecte al lunes siguiente")
    print()
    
    for viernes in viernes_2025:
        # Verificar que es viernes
        if viernes.weekday() != 4:
            print(f"❌ ERROR: {viernes} no es viernes")
            continue
            
        # Obtener próximo día hábil
        siguiente = service.proximo_dia_habil(viernes, incluir_fecha_actual=False)
        nombre_siguiente = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][siguiente.weekday()]
        
        print(f"Viernes {viernes} -> {nombre_siguiente} {siguiente}")
        
        # Verificar que sea lunes
        if siguiente.weekday() == 0:  # Lunes
            print("✅ CORRECTO: Proyectó al lunes")
        else:
            print(f"❌ ERROR: Debería ser lunes, pero es {nombre_siguiente}")
        print()
    
    # Probar fecha actual
    hoy = date(2025, 9, 17)  # Martes 17 septiembre 2025
    siguiente_hoy = service.proximo_dia_habil(hoy, incluir_fecha_actual=False)
    nombre_hoy = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][siguiente_hoy.weekday()]
    print(f"Hoy Martes {hoy} -> {nombre_hoy} {siguiente_hoy}")

if __name__ == "__main__":
    main()