#!/usr/bin/env python3
"""
Script para probar el bug de proyección de días hábiles.
Reproduce el escenario: viernes → debería proyectar al lunes
"""

import sys
import os
from datetime import date, datetime

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.dias_habiles_service import DiasHabilesService

def test_projection_bug():
    """Test específico para el bug de proyección viernes → sábado en lugar de lunes"""
    
    # Crear una instancia del servicio
    db = next(get_db())
    service = DiasHabilesService(db)
    
    # Casos de prueba
    casos_prueba = [
        # Viernes 24 de enero 2025 → debería ser lunes 27 de enero 2025
        date(2025, 1, 24),  # Viernes
        # Jueves 23 de enero 2025 → debería ser viernes 24 de enero 2025  
        date(2025, 1, 23),  # Jueves
        # Miércoles 22 de enero 2025 → debería ser jueves 23 de enero 2025
        date(2025, 1, 22),  # Miércoles
    ]
    
    print("🧪 Test de proyección de días hábiles")
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
            else:
                print(f"✅ OK: Viernes correctamente proyectado a lunes")
    
    print("\n🔍 Verificación de festivos cercanos:")
    
    # Verificar si hay festivos que puedan afectar
    fechas_verificar = [
        date(2025, 1, 25),  # Sábado
        date(2025, 1, 26),  # Domingo  
        date(2025, 1, 27),  # Lunes
    ]
    
    for fecha in fechas_verificar:
        nombre_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][fecha.weekday()]
        es_habil = service.es_dia_habil(fecha)
        print(f"{nombre_dia} {fecha}: hábil = {es_habil}")

if __name__ == "__main__":
    test_projection_bug()