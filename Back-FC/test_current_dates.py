#!/usr/bin/env python3
"""
Script para probar proyección con fechas reales de septiembre 2024
"""

import sys
import os
from datetime import date, datetime

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.dias_habiles_service import DiasHabilesService

def test_current_dates():
    """Test con fechas actuales de septiembre 2024"""
    
    # Crear una instancia del servicio
    db = next(get_db())
    service = DiasHabilesService(db)
    
    # Casos de prueba para septiembre 2024
    casos_prueba = [
        # Viernes 13 de septiembre → debería ser lunes 16
        date(2024, 9, 13),  # Viernes
        # Viernes 20 de septiembre → debería ser lunes 23  
        date(2024, 9, 20),  # Viernes
        # Viernes 27 de septiembre → debería ser lunes 30
        date(2024, 9, 27),  # Viernes
    ]
    
    print("🧪 Test de proyección septiembre 2024")
    print("=" * 50)
    
    for fecha_test in casos_prueba:
        nombre_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][fecha_test.weekday()]
        
        # Verificar si la fecha actual es día hábil
        es_habil = service.es_dia_habil(fecha_test)
        
        # Obtener el próximo día hábil
        proximo = service.proximo_dia_habil(fecha_test, incluir_fecha_actual=False)
        nombre_proximo = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][proximo.weekday()]
        
        print(f"{nombre_dia} {fecha_test} (hábil: {es_habil}) → {nombre_proximo} {proximo}")
        
        # Verificar el caso específico del viernes
        if fecha_test.weekday() == 4:  # Viernes
            if proximo.weekday() != 0:  # No es lunes
                print(f"❌ ERROR: Viernes debería proyectar a lunes, pero proyectó a {nombre_proximo}")
                
                # Debug adicional
                sabado = fecha_test.replace(day=fecha_test.day + 1)
                domingo = fecha_test.replace(day=fecha_test.day + 2)
                lunes = fecha_test.replace(day=fecha_test.day + 3)
                
                print(f"  Debug - Sábado {sabado}: hábil = {service.es_dia_habil(sabado)}")
                print(f"  Debug - Domingo {domingo}: hábil = {service.es_dia_habil(domingo)}")
                print(f"  Debug - Lunes {lunes}: hábil = {service.es_dia_habil(lunes)}")
            else:
                print(f"✅ OK: Viernes correctamente proyectado a lunes")

if __name__ == "__main__":
    test_current_dates()