#!/usr/bin/env python3
"""
Test directo del sistema de dependencias tras actualización de transacciones
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
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja

# Configurar logging para ver las consultas SQL
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def main():
    """Test directo del procesamiento de dependencias"""
    
    # Obtener la sesión de base de datos
    db = next(get_db())
    
    try:
        # Crear instancias de servicios
        transaccion_service = TransaccionFlujoCajaService(db)
        dependencias_service = DependenciasFlujoCajaService(db)
        
        fecha_test = date(2025, 9, 16)
        cuenta_id = 1
        compania_id = 1
        usuario_id = 6
        
        print("\n=== TEST DIRECTO DE DEPENDENCIAS ===")
        
        # 1. Verificar estado inicial del SUBTOTAL TESORERÍA
        print("1. Estado inicial del SUBTOTAL TESORERÍA:")
        subtotal_inicial = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == cuenta_id
        ).first()
        
        if subtotal_inicial:
            print(f"   📊 SUBTOTAL inicial: ${subtotal_inicial.monto}")
        else:
            print("   ❌ No se encontró SUBTOTAL TESORERÍA")
            
        # 2. Verificar componentes actuales (conceptos 5-49)
        print("\n2. Verificando componentes de tesorería (5-49):")
        componentes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id >= 5,
            TransaccionFlujoCaja.concepto_id <= 49,
            TransaccionFlujoCaja.cuenta_id == cuenta_id,
            TransaccionFlujoCaja.area == "tesoreria"
        ).order_by(TransaccionFlujoCaja.concepto_id).all()
        
        total_componentes = sum(t.monto for t in componentes)
        
        for t in componentes:
            print(f"   • Concepto {t.concepto_id}: ${t.monto} - {t.descripcion}")
        
        print(f"\n   📊 Total componentes: ${total_componentes}")
        
        # 3. Procesar dependencias manualmente
        print("\n3. Procesando dependencias completas...")
        
        dependencias_service.procesar_dependencias_completas_ambos_dashboards(
            fecha=fecha_test,
            cuenta_id=cuenta_id,
            compania_id=compania_id,
            usuario_id=usuario_id
        )
        
        # 4. Verificar estado final
        print("\n4. Estado final tras procesamiento:")
        subtotal_final = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 50,
            TransaccionFlujoCaja.cuenta_id == cuenta_id
        ).first()
        
        if subtotal_final:
            print(f"   📊 SUBTOTAL final: ${subtotal_final.monto}")
            
            if subtotal_final.monto == total_componentes:
                print("   ✅ SUBTOTAL actualizado correctamente")
            else:
                print(f"   ❌ SUBTOTAL incorrecto. Esperado: ${total_componentes}, Actual: ${subtotal_final.monto}")
        else:
            print("   ❌ No se encontró SUBTOTAL TESORERÍA")
        
        # 5. Test específico: Actualizar una transacción y ver si se recalcula
        print("\n5. Test de actualización directa:")
        
        # Buscar transacción concepto 5 para modificar
        transaccion_5 = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_test,
            TransaccionFlujoCaja.concepto_id == 5,
            TransaccionFlujoCaja.cuenta_id == cuenta_id,
            TransaccionFlujoCaja.area == "tesoreria"
        ).first()
        
        if transaccion_5:
            monto_original = transaccion_5.monto
            nuevo_monto = Decimal('4000.00')
            
            print(f"   📝 Modificando concepto 5 de ${monto_original} a ${nuevo_monto}")
            
            # Actualizar usando el servicio
            actualizada = transaccion_service.actualizar_transaccion(
                transaccion_id=transaccion_5.id,
                monto=nuevo_monto,
                descripcion="Test directo - Modificado desde script"
            )
            
            print(f"   ✅ Transacción actualizada: ${actualizada.monto}")
            
            # Verificar SUBTOTAL después
            subtotal_post_update = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_test,
                TransaccionFlujoCaja.concepto_id == 50,
                TransaccionFlujoCaja.cuenta_id == cuenta_id
            ).first()
            
            if subtotal_post_update:
                print(f"   📊 SUBTOTAL tras actualización: ${subtotal_post_update.monto}")
                
                # Calcular total esperado
                nuevo_total = (total_componentes - monto_original + nuevo_monto)
                
                if subtotal_post_update.monto == nuevo_total:
                    print(f"   ✅ ¡CORRECCIÓN FUNCIONANDO! SUBTOTAL actualizado correctamente a ${nuevo_total}")
                else:
                    print(f"   ❌ Error: Esperado ${nuevo_total}, Actual: ${subtotal_post_update.monto}")
            else:
                print("   ❌ No se encontró SUBTOTAL tras actualización")
        else:
            print("   ❌ No se encontró transacción concepto 5 para modificar")
        
        print("\n=== FIN DEL TEST ===")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.rollback()  # Rollback para no afectar datos
        db.close()

if __name__ == "__main__":
    main()