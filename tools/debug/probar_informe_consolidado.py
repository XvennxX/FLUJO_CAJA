#!/usr/bin/env python3
"""
Script de prueba para verificar datos de informes consolidados
"""

import sys
import os
from datetime import date
from pathlib import Path

# Agregar el directorio del backend al path
backend_root = Path(__file__).parent.parent.parent / "Back-FC"
sys.path.append(str(backend_root))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.companias import Compania
from app.models.cuentas_bancarias import CuentaBancaria
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

def probar_datos_informe():
    """Probar datos disponibles para informe consolidado"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        # Fechas de septiembre 2025
        fecha_inicio = date(2025, 9, 1)
        fecha_fin = date(2025, 9, 30)
        
        print(f"🔍 PROBANDO DATOS PARA INFORME CONSOLIDADO")
        print(f"📅 Período: {fecha_inicio} - {fecha_fin}")
        print("=" * 60)
        
        # Obtener transacciones
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha >= fecha_inicio,
            TransaccionFlujoCaja.fecha <= fecha_fin
        ).all()
        
        print(f"📊 Total transacciones encontradas: {len(transacciones)}")
        
        # Obtener metadata
        companias = db.query(Compania).all()
        cuentas = db.query(CuentaBancaria).all()
        conceptos = db.query(ConceptoFlujoCaja).all()
        
        print(f"🏢 Compañías: {len(companias)}")
        print(f"🏦 Cuentas bancarias: {len(cuentas)}")
        print(f"📋 Conceptos: {len(conceptos)}")
        
        # Análisis por área
        conceptos_tesoreria = [c for c in conceptos if c.id <= 51]
        conceptos_pagaduria = [c for c in conceptos if c.id > 51]
        
        print(f"💰 Conceptos Tesorería (ID 1-51): {len(conceptos_tesoreria)}")
        print(f"👥 Conceptos Pagaduría (ID 52+): {len(conceptos_pagaduria)}")
        print()
        
        # Análisis de transacciones por área
        transacciones_tesoreria = [t for t in transacciones if t.concepto_id <= 51]
        transacciones_pagaduria = [t for t in transacciones if t.concepto_id > 51]
        
        print(f"📈 Transacciones Tesorería: {len(transacciones_tesoreria)}")
        print(f"📈 Transacciones Pagaduría: {len(transacciones_pagaduria)}")
        print()
        
        # Mostrar algunas transacciones de ejemplo
        print("🔍 EJEMPLOS DE TRANSACCIONES:")
        for i, transaccion in enumerate(transacciones[:5]):
            area = "Tesorería" if transaccion.concepto_id <= 51 else "Pagaduría"
            print(f"  {i+1}. {transaccion.fecha} | {area} | Concepto ID: {transaccion.concepto_id} | Monto: ${transaccion.monto}")
        
        if len(transacciones) > 5:
            print(f"  ... y {len(transacciones) - 5} más")
        
        print()
        print("✅ ANÁLISIS COMPLETADO")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_datos_informe()