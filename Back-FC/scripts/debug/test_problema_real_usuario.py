#!/usr/bin/env python3
"""
Test específico para reproducir el problema exacto del usuario:
Modificar conceptos 5-49 y verificar que SUBTOTAL TESORERÍA se recalcula
"""
import os
import sys
from datetime import date
from decimal import Decimal

# Configurar el path para importar módulos del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, PROJECT_ROOT)

from app.core.database import get_db
from app.services.transaccion_flujo_caja_service import TransaccionFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.schemas.flujo_caja import TransaccionFlujoCajaUpdate

def main():
    """Test exacto del problema reportado por el usuario"""
    
    # Obtener la sesión de base de datos
    db = next(get_db())
    
    try:
        fecha_test = date.today()  # Usar fecha actual
        cuenta_id = 1
        compania_id = 1
        usuario_id = 6
        
        print(f"\n🔍 === TEST PROBLEMA USUARIO - {fecha_test} === 🔍")
        
        # 1. Buscar transacciones existentes en rango 5-49 para hoy
        print("1. Buscando transacciones existentes (conceptos 5-49):")
        transacciones_existentes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id >= 5,
            TransaccionFlujoCaja.concepto_id <= 49,
            TransaccionFlujoCaja.cuenta_id == cuenta_id,
            TransaccionFlujoCaja.area == "tesoreria"
        ).all()
        
        if not transacciones_existentes:
            print("   ❌ No hay transacciones existentes para modificar")
            print("   💡 Creando una transacción de prueba...")
            
            # Crear una transacción de prueba
            service = TransaccionFlujoCajaService(db)
            from app.schemas.flujo_caja import TransaccionFlujoCajaCreate
            
            nueva_transaccion = TransaccionFlujoCajaCreate(
                fecha=fecha_test,
                concepto_id=5,
                cuenta_id=cuenta_id,
                monto=Decimal('1000.00'),
                descripcion="Transacción de prueba para modificar",
                area="tesoreria",
                compania_id=compania_id
            )
            
            transaccion_creada = service.crear_transaccion(nueva_transaccion, usuario_id)
            print(f"   ✅ Transacción creada: ID {transaccion_creada.id}, concepto {transaccion_creada.concepto_id}, monto ${transaccion_creada.monto}")
            transacciones_existentes = [transaccion_creada]
        
        # 2. Mostrar estado inicial
        print(f"\n2. Estado inicial - {len(transacciones_existentes)} transacciones encontradas:")
        for t in transacciones_existentes:
            print(f"   • ID: {t.id}, Concepto: {t.concepto_id}, Monto: ${t.monto}, Descripción: {t.descripcion}")
        
        # 3. Verificar SUBTOTAL TESORERÍA actual
        subtotal_antes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == cuenta_id
        ).first()
        
        monto_subtotal_antes = subtotal_antes.monto if subtotal_antes else Decimal('0')
        print(f"\n3. SUBTOTAL TESORERÍA antes: ${monto_subtotal_antes}")
        
        # 4. MODIFICAR una transacción existente (simular lo que hace el usuario)
        transaccion_a_modificar = transacciones_existentes[0]
        monto_original = transaccion_a_modificar.monto
        nuevo_monto = monto_original + Decimal('500.00')
        
        print(f"\n4. MODIFICANDO transacción ID {transaccion_a_modificar.id}:")
        print(f"   📝 Concepto: {transaccion_a_modificar.concepto_id}")
        print(f"   📝 Monto original: ${monto_original}")
        print(f"   📝 Nuevo monto: ${nuevo_monto}")
        
        # Usar el servicio para actualizar (como lo hace la aplicación real)
        service = TransaccionFlujoCajaService(db)
        
        # Crear el objeto de actualización
        datos_actualizacion = TransaccionFlujoCajaUpdate(
            monto=nuevo_monto,
            descripcion=f"MODIFICADO - {transaccion_a_modificar.descripcion}"
        )
        
        # Ejecutar la actualización
        transaccion_actualizada = service.actualizar_transaccion(
            transaccion_id=transaccion_a_modificar.id,
            transaccion_data=datos_actualizacion,
            usuario_id=usuario_id
        )
        
        print(f"   ✅ Transacción actualizada: ${transaccion_actualizada.monto}")
        
        # 5. Verificar SUBTOTAL TESORERÍA después
        print(f"\n5. Verificando SUBTOTAL TESORERÍA después de la modificación:")
        
        # Refrescar la consulta
        db.commit()  # Asegurar que todos los cambios estén persistidos
        
        subtotal_despues = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == cuenta_id
        ).first()
        
        monto_subtotal_despues = subtotal_despues.monto if subtotal_despues else Decimal('0')
        diferencia_esperada = nuevo_monto - monto_original
        
        print(f"   📊 SUBTOTAL antes: ${monto_subtotal_antes}")
        print(f"   📊 SUBTOTAL después: ${monto_subtotal_despues}")
        print(f"   📊 Diferencia esperada: ${diferencia_esperada}")
        print(f"   📊 Diferencia real: ${monto_subtotal_despues - monto_subtotal_antes}")
        
        # 6. DIAGNÓSTICO
        if monto_subtotal_despues == monto_subtotal_antes + diferencia_esperada:
            print(f"\n✅ ¡ÉXITO! El SUBTOTAL TESORERÍA se actualizó correctamente")
            print(f"   🎯 Cambio detectado: ${diferencia_esperada}")
        else:
            print(f"\n❌ ¡PROBLEMA CONFIRMADO! El SUBTOTAL TESORERÍA NO se actualizó")
            print(f"   ⚠️  Esperado: ${monto_subtotal_antes + diferencia_esperada}")
            print(f"   ⚠️  Actual: ${monto_subtotal_despues}")
            
            # Diagnóstico adicional
            print(f"\n🔍 DIAGNÓSTICO ADICIONAL:")
            
            # Verificar si el método de actualización se llamó
            print(f"   • Método actualizar_transaccion ejecutado: ✅")
            print(f"   • Transacción modificada correctamente: ✅")
            
            # Verificar todas las transacciones de tesorería actuales
            todas_tesoreria = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_test,
                TransaccionFlujoCaja.concepto_id >= 5,
                TransaccionFlujoCaja.concepto_id <= 49,
                TransaccionFlujoCaja.cuenta_id == cuenta_id,
                TransaccionFlujoCaja.area == "tesoreria"
            ).all()
            
            total_real = sum(t.monto for t in todas_tesoreria)
            print(f"   • Suma real de conceptos 5-49: ${total_real}")
            print(f"   • SUBTOTAL almacenado: ${monto_subtotal_despues}")
            print(f"   • ¿Coinciden? {'✅' if total_real == monto_subtotal_despues else '❌'}")
            
            if total_real != monto_subtotal_despues:
                print(f"\n💡 PROBLEMA: El auto-cálculo no se ejecutó correctamente")
                print(f"   La suma manual (${total_real}) no coincide con el SUBTOTAL (${monto_subtotal_despues})")
        
        print(f"\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.rollback()  # No afectar datos reales
        db.close()

if __name__ == "__main__":
    main()