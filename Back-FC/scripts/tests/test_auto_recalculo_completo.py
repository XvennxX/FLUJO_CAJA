#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo para verificar auto-recálculo en tiempo real entre dashboards
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from decimal import Decimal
from sqlalchemy import text

def main():
    print("=== TEST AUTO-RECÁLCULO EN TIEMPO REAL ===")
    print("🎯 Verificando que cambios en tesorería se reflejen automáticamente en pagaduría")
    
    db = SessionLocal()
    try:
        fecha_test = datetime(2025, 9, 10).date()
        print(f"📅 Fecha de prueba: {fecha_test}")
        
        # 1. Limpiar datos anteriores
        print("\n1. Limpiando datos anteriores...")
        db.execute(text("""
            DELETE FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id IN (50, 84)
            AND cuenta_id = 1
        """), {"fecha": fecha_test})
        db.commit()
        
        # 2. Crear SUB-TOTAL TESORERÍA inicial
        print("\n2. Creando SUB-TOTAL TESORERÍA inicial...")
        
        subtotal_inicial = Decimal('1000.00')
        subtotal_tesoreria = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=50,  # SUB-TOTAL TESORERÍA
            cuenta_id=1,
            monto=subtotal_inicial,
            descripcion="Test - SUB-TOTAL TESORERÍA inicial",
            usuario_id=6,
            area=AreaTransaccion.tesoreria,
            compania_id=1,
            auditoria={"test": "auto_recalculo"}
        )
        
        db.add(subtotal_tesoreria)
        db.commit()
        print(f"   ✅ SUB-TOTAL TESORERÍA creado: ${subtotal_inicial}")
        
        # 3. Ejecutar recálculo inicial para crear MOVIMIENTO TESORERIA
        print("\n3. Ejecutando recálculo inicial...")
        service = DependenciasFlujoCajaService(db)
        resultados_inicial = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        # 4. Verificar que se creó MOVIMIENTO TESORERIA
        movimiento_inicial = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 84
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).scalar()
        
        print(f"   📊 MOVIMIENTO TESORERIA inicial: ${movimiento_inicial or 0}")
        
        if movimiento_inicial == subtotal_inicial:
            print(f"   ✅ Sincronización inicial correcta: ${movimiento_inicial}")
        else:
            print(f"   ❌ Error sincronización inicial: esperado ${subtotal_inicial}, obtenido ${movimiento_inicial}")
            return
        
        # 5. MODIFICAR SUB-TOTAL TESORERÍA
        print(f"\n5. Modificando SUB-TOTAL TESORERÍA...")
        nuevo_subtotal = Decimal('1500.00')
        subtotal_tesoreria.monto = nuevo_subtotal
        subtotal_tesoreria.descripcion = "Test - SUB-TOTAL TESORERÍA MODIFICADO"
        db.commit()
        
        print(f"   🔄 SUB-TOTAL TESORERÍA cambiado: ${subtotal_inicial} → ${nuevo_subtotal}")
        
        # 6. Ejecutar recálculo automático
        print("\n6. Ejecutando recálculo automático...")
        resultados_update = service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            concepto_modificado_id=50,  # SUB-TOTAL TESORERÍA
            cuenta_id=1,
            compania_id=1,
            usuario_id=6
        )
        
        # 7. Verificar que MOVIMIENTO TESORERIA se actualizó automáticamente
        movimiento_actualizado = db.execute(text("""
            SELECT monto FROM transacciones_flujo_caja
            WHERE fecha = :fecha
            AND concepto_id = 84
            AND area = 'pagaduria'
            AND cuenta_id = 1
        """), {"fecha": fecha_test}).scalar()
        
        print(f"   📊 MOVIMIENTO TESORERIA actualizado: ${movimiento_actualizado or 0}")
        
        # 8. Validar resultado
        if movimiento_actualizado == nuevo_subtotal:
            print(f"\n🎉 ¡ÉXITO! Auto-recálculo en tiempo real funciona correctamente")
            print(f"   💰 SUB-TOTAL TESORERÍA: ${nuevo_subtotal}")
            print(f"   💰 MOVIMIENTO TESORERIA: ${movimiento_actualizado}")
            print(f"   🔄 Sincronización automática: ✅")
        else:
            print(f"\n❌ ERROR en auto-recálculo:")
            print(f"   SUB-TOTAL TESORERÍA: ${nuevo_subtotal}")
            print(f"   MOVIMIENTO TESORERIA: ${movimiento_actualizado or 0}")
            print(f"   Sincronización: ❌")
        
        # 9. Mostrar detalles del recálculo
        print(f"\n9. Detalles del recálculo:")
        
        total_tesoreria = len(resultados_update.get("tesoreria", []))
        total_pagaduria = len(resultados_update.get("pagaduria", []))
        total_cross = len(resultados_update.get("cross_dashboard", []))
        
        print(f"   • Actualizaciones tesorería: {total_tesoreria}")
        print(f"   • Actualizaciones pagaduría: {total_pagaduria}")
        print(f"   • Actualizaciones cruzadas: {total_cross}")
        
        # Mostrar cross-dashboard updates
        for update in resultados_update.get("cross_dashboard", []):
            concepto = update.get("concepto_nombre", "N/A")
            tipo = update.get("tipo", "N/A")
            origen = update.get("origen_dashboard", "N/A")
            destino = update.get("destino_dashboard", "N/A")
            print(f"     ↳ {concepto}: {origen} → {destino} ({tipo})")
        
        # 10. Test de múltiples cambios
        print(f"\n10. Test de cambios múltiples...")
        
        # Cambiar varias veces para probar robustez
        valores_test = [Decimal('2000.00'), Decimal('2500.00'), Decimal('1800.00')]
        
        for i, valor in enumerate(valores_test, 1):
            print(f"    Cambio {i}: ${valor}")
            subtotal_tesoreria.monto = valor
            db.commit()
            
            # Recálculo
            service.procesar_dependencias_completas_ambos_dashboards(
                fecha=fecha_test,
                concepto_modificado_id=50,
                cuenta_id=1,
                compania_id=1,
                usuario_id=6
            )
            
            # Verificar
            movimiento_test = db.execute(text("""
                SELECT monto FROM transacciones_flujo_caja
                WHERE fecha = :fecha
                AND concepto_id = 84
                AND area = 'pagaduria'
                AND cuenta_id = 1
            """), {"fecha": fecha_test}).scalar()
            
            estado = "✅" if movimiento_test == valor else "❌"
            print(f"      {estado} MOVIMIENTO TESORERIA: ${movimiento_test}")
        
        print(f"\n🎉 Test de auto-recálculo completado!")
        print(f"💡 Los cambios en tesorería se propagan automáticamente a pagaduría")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
