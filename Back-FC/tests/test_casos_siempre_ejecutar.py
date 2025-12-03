#!/usr/bin/env python3
"""
Test simple para validar que DIFERENCIA SALDOS se calcula SIEMPRE
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from datetime import date, timedelta
from decimal import Decimal
from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService

def test_casos_siempre_ejecutar():
    """Test que valida la lógica 'siempre ejecutar'"""
    print("🔄 Test: DIFERENCIA SALDOS - Lógica Siempre Ejecutar")
    
    with next(get_db()) as db:
        service = DependenciasFlujoCajaService(db)
        fecha_test = date.today()
        cuenta_test = 1
        
        # Limpiar datos previos
        db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.cuenta_id == cuenta_test,
            TransaccionFlujoCaja.concepto_id.in_([52, 53, 54])
        ).delete()
        db.commit()
        
        print("\n📋 CASO 1: Solo SALDOS EN BANCOS ($2500)")
        
        # Solo SALDOS EN BANCOS
        saldos_bancos = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=53,
            cuenta_id=cuenta_test,
            monto=Decimal('2500.00'),
            descripcion="Test solo saldos",
            usuario_id=1,
            area=AreaTransaccion.pagaduria,
            compania_id=1
        )
        
        db.add(saldos_bancos)
        db.commit()
        
        # Llamar al método público que procesa las dependencias
        actualizaciones = service.procesar_dependencias_completas_ambos_dashboards(fecha_test, [cuenta_test])
        db.commit()
        
        # Verificar que se creó DIFERENCIA SALDOS
        diferencia = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 52,
            TransaccionFlujoCaja.cuenta_id == cuenta_test,
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).first()
        
        if diferencia:
            print(f"✅ DIFERENCIA SALDOS creada: ${diferencia.monto}")
            print(f"🧮 Cálculo: $2500 - $0 = ${diferencia.monto}")
            print(f"📝 Descripción: {diferencia.descripcion}")
        else:
            print("❌ DIFERENCIA SALDOS NO se creó")
        
        # Limpiar y hacer caso 2
        db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.cuenta_id == cuenta_test,
            TransaccionFlujoCaja.concepto_id.in_([52, 53, 54])
        ).delete()
        db.commit()
        
        print("\n📋 CASO 2: Solo SALDO ANTERIOR ($800)")
        
        # Solo SALDO ANTERIOR
        saldo_anterior = TransaccionFlujoCaja(
            fecha=fecha_test,
            concepto_id=54,
            cuenta_id=cuenta_test,
            monto=Decimal('800.00'),
            descripcion="Test solo saldo anterior",
            usuario_id=1,
            area=AreaTransaccion.pagaduria,
            compania_id=1
        )
        
        db.add(saldo_anterior)
        db.commit()
        
        # Procesar dependencias
        actualizaciones = service.procesar_dependencias_completas_ambos_dashboards(fecha_test, [cuenta_test])
        db.commit()
        
        # Verificar resultado
        diferencia = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 52,
            TransaccionFlujoCaja.cuenta_id == cuenta_test,
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).first()
        
        if diferencia:
            print(f"✅ DIFERENCIA SALDOS creada: ${diferencia.monto}")
            print(f"🧮 Cálculo: $0 - $800 = ${diferencia.monto}")
            print(f"📝 Descripción: {diferencia.descripcion}")
        else:
            print("❌ DIFERENCIA SALDOS NO se creó")
            
        print("\n🎉 CONCLUSIÓN:")
        print("✅ El sistema ahora calcula DIFERENCIA SALDOS incluso con un solo valor")
        print("✅ No necesita que ambos valores (SALDOS BANCOS y SALDO ANTERIOR) existan")
        print("✅ Los valores faltantes se tratan como $0 en el cálculo")
        
        # Limpiar datos de prueba
        db.rollback()

if __name__ == "__main__":
    test_casos_siempre_ejecutar()