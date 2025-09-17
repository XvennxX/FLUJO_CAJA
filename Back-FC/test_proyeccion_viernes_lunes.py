#!/usr/bin/env python3
"""
Test para verificar la proyección automática de viernes a lunes
"""

import sys
import os
from datetime import date

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion

def test_proyeccion_viernes_lunes():
    """Test específico para proyección viernes → lunes"""
    
    db = next(get_db())
    service = DependenciasFlujoCajaService(db)
    
    # Fechas de prueba
    viernes = date(2025, 9, 19)  # Viernes 19 septiembre
    lunes = date(2025, 9, 22)    # Lunes 22 septiembre
    
    print("🧪 TEST PROYECCIÓN VIERNES → LUNES")
    print("=" * 50)
    print(f"Viernes: {viernes}")
    print(f"Lunes esperado: {lunes}")
    print()
    
    # Verificar que son días hábiles
    es_viernes_habil = service.dias_habiles_service.es_dia_habil(viernes)
    es_lunes_habil = service.dias_habiles_service.es_dia_habil(lunes)
    
    print(f"¿Viernes es hábil? {es_viernes_habil}")
    print(f"¿Lunes es hábil? {es_lunes_habil}")
    
    # Verificar próximo día hábil
    proximo_habil = service.dias_habiles_service.proximo_dia_habil(viernes, incluir_fecha_actual=False)
    print(f"Próximo día hábil después del viernes: {proximo_habil}")
    
    if proximo_habil != lunes:
        print(f"❌ ERROR: Esperaba {lunes}, pero obtuve {proximo_habil}")
        return
    
    print("✅ Lógica de días hábiles correcta")
    print()
    
    # Simular que hay un SALDO TOTAL el viernes
    # Buscar transacciones existentes del viernes
    saldo_total_viernes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == viernes,
        TransaccionFlujoCaja.concepto_id == 53,  # SALDO TOTAL EN BANCOS
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).first()
    
    if saldo_total_viernes:
        print(f"📊 SALDO TOTAL encontrado el viernes: ${saldo_total_viernes.monto}")
        print(f"   Cuenta: {saldo_total_viernes.cuenta_id}")
        print(f"   Descripción: {saldo_total_viernes.descripcion}")
    else:
        print("❓ No hay SALDO TOTAL registrado el viernes")
    
    # Buscar SALDO DÍA ANTERIOR proyectado al lunes
    saldo_dia_anterior_lunes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == lunes,
        TransaccionFlujoCaja.concepto_id == 54,  # SALDO DÍA ANTERIOR
        TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
    ).all()
    
    print()
    if saldo_dia_anterior_lunes:
        print(f"📈 SALDO DÍA ANTERIOR encontrado el lunes:")
        for saldo in saldo_dia_anterior_lunes:
            print(f"   Cuenta {saldo.cuenta_id}: ${saldo.monto}")
            print(f"   Descripción: {saldo.descripcion}")
    else:
        print("❌ NO hay SALDO DÍA ANTERIOR proyectado al lunes")
        print("   Esto indica que la proyección automática NO funcionó")
    
    print()
    print("💡 RECOMENDACIÓN:")
    print("   Si no hay proyección automática, significa que:")
    print("   1. El SALDO TOTAL del viernes no se guardó correctamente")
    print("   2. La lógica de proyección no se ejecutó")
    print("   3. Hay un error en el servicio de dependencias")

if __name__ == "__main__":
    test_proyeccion_viernes_lunes()