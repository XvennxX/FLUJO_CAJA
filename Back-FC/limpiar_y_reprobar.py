#!/usr/bin/env python3
"""
Script para limpiar las proyecciones incorrectas y volver a ejecutar
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from sqlalchemy.orm import Session

def limpiar_y_reprobar():
    """Limpiar proyecciones incorrectas y volver a ejecutar"""
    
    try:
        # Obtener conexión a la base de datos
        db = next(get_db())
        
        lunes = date(2025, 9, 22)
        viernes = date(2025, 9, 19)
        
        print(f"🧹 LIMPIANDO PROYECCIONES INCORRECTAS DEL {lunes}")
        print("=" * 60)
        
        # 1. Eliminar SALDO INICIAL auto-calculados del lunes
        saldos_auto_calculados = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
            TransaccionFlujoCaja.descripcion.like('%Auto-calculado%')
        ).all()
        
        print(f"🗑️ Eliminando {len(saldos_auto_calculados)} SALDO INICIAL auto-calculados:")
        for saldo in saldos_auto_calculados:
            print(f"   - ID {saldo.id}: Cuenta {saldo.cuenta_id}, ${saldo.monto}")
            db.delete(saldo)
        
        db.commit()
        print(f"✅ Transacciones incorrectas eliminadas")
        
        print(f"\n🚀 EJECUTANDO NUEVA PROYECCIÓN CON DEBUG:")
        
        # 2. Ejecutar nueva proyección
        service = DependenciasFlujoCajaService(db)
        resultado = service._procesar_dependencias_pagaduria(
            fecha=viernes,
            usuario_id=1,
            compania_id=1
        )
        
        print(f"✅ Proyección completada. Actualizaciones: {len(resultado)}")
        
        # 3. Verificar resultados
        print(f"\n📊 VERIFICANDO NUEVOS RESULTADOS:")
        nuevos_saldos = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == lunes,
            TransaccionFlujoCaja.concepto_id == 1,  # SALDO INICIAL
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
        ).all()
        
        for saldo in nuevos_saldos:
            print(f"   ✅ Cuenta {saldo.cuenta_id}: ${saldo.monto}")
            if 'Auto-calculado' in str(saldo.descripcion):
                print(f"      🚀 PROYECTADO correctamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    limpiar_y_reprobar()