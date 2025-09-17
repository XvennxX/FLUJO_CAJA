#!/usr/bin/env python3
"""
Verificar transacciones específicas del viernes
"""

import sys
import os
from datetime import date

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion

def main():
    db = next(get_db())
    
    viernes = date(2025, 9, 19)
    lunes = date(2025, 9, 22)
    
    print("📊 ANÁLISIS DETALLADO - TRANSACCIONES")
    print("=" * 60)
    
    # Transacciones del viernes con monto
    print(f"🗓️ VIERNES {viernes}:")
    transacciones_viernes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == viernes,
        TransaccionFlujoCaja.monto != 0
    ).all()
    
    if transacciones_viernes:
        for t in transacciones_viernes:
            area_str = "PAG" if t.area == AreaTransaccion.pagaduria else "TES"
            print(f"  [{area_str}] ID{t.concepto_id}: ${t.monto:,.2f} (Cuenta {t.cuenta_id})")
            print(f"       📝 {t.descripcion}")
            print()
    else:
        print("  ❌ No hay transacciones con monto")
    
    # Buscar específicamente SALDO TOTAL (ID 53) del viernes
    print("🔍 BUSCANDO SALDO TOTAL (ID 53) DEL VIERNES:")
    saldo_total_viernes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == viernes,
        TransaccionFlujoCaja.concepto_id == 53
    ).all()
    
    if saldo_total_viernes:
        for s in saldo_total_viernes:
            area_str = "PAG" if s.area == AreaTransaccion.pagaduria else "TES"
            print(f"  [{area_str}] ${s.monto:,.2f} (Cuenta {s.cuenta_id}) - {s.descripcion}")
    else:
        print("  ❌ NO existe SALDO TOTAL del viernes")
    
    print()
    print(f"🗓️ LUNES {lunes}:")
    
    # Transacciones del lunes con monto
    transacciones_lunes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == lunes,
        TransaccionFlujoCaja.monto != 0
    ).all()
    
    if transacciones_lunes:
        for t in transacciones_lunes:
            area_str = "PAG" if t.area == AreaTransaccion.pagaduria else "TES"
            print(f"  [{area_str}] ID{t.concepto_id}: ${t.monto:,.2f} (Cuenta {t.cuenta_id})")
            print(f"       📝 {t.descripcion}")
            print()
    else:
        print("  ❌ No hay transacciones con monto")
    
    # Buscar específicamente SALDO DÍA ANTERIOR (ID 54) del lunes
    print("🔍 BUSCANDO SALDO DÍA ANTERIOR (ID 54) DEL LUNES:")
    saldo_anterior_lunes = db.query(TransaccionFlujoCaja).filter(
        TransaccionFlujoCaja.fecha == lunes,
        TransaccionFlujoCaja.concepto_id == 54
    ).all()
    
    if saldo_anterior_lunes:
        for s in saldo_anterior_lunes:
            area_str = "PAG" if s.area == AreaTransaccion.pagaduria else "TES"
            print(f"  [{area_str}] ${s.monto:,.2f} (Cuenta {s.cuenta_id}) - {s.descripcion}")
    else:
        print("  ❌ NO existe SALDO DÍA ANTERIOR del lunes")
    
    print()
    print("💡 CONCLUSIÓN:")
    if not saldo_total_viernes and saldo_anterior_lunes:
        print("   ⚠️  HAY PROYECCIÓN pero NO hay SALDO TOTAL original")
        print("   📌 Problema: Los datos del viernes se perdieron después de la proyección")
    elif saldo_total_viernes and saldo_anterior_lunes:
        print("   ✅ Proyección funcionando correctamente")
    elif saldo_total_viernes and not saldo_anterior_lunes:
        print("   ❌ HAY datos del viernes pero NO se proyectaron al lunes")
    else:
        print("   ❓ No hay datos suficientes para analizar")

if __name__ == "__main__":
    main()