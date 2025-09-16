"""
Script para limpiar y regenerar datos de SALDO DIA ANTERIOR con la lógica correcta
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from datetime import datetime

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def limpiar_y_regenerar_saldo_anterior():
    """
    1. Eliminar todas las transacciones SALDO DIA ANTERIOR (concepto_id=54) del área pagaduría
    2. Regenerar los datos con la lógica correcta usando el servicio
    """
    try:
        print("🧹 INICIANDO LIMPIEZA DE SALDO DIA ANTERIOR...")
        
        # 1. Obtener todas las transacciones SALDO DIA ANTERIOR en pagaduría
        transacciones_saldo_anterior = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 54,  # SALDO DIA ANTERIOR
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).all()
        
        print(f"📊 Encontradas {len(transacciones_saldo_anterior)} transacciones SALDO DIA ANTERIOR a eliminar")
        
        # Mostrar detalles antes de eliminar
        for trans in transacciones_saldo_anterior:
            print(f"  • Fecha: {trans.fecha}, Cuenta: {trans.cuenta_id}, Monto: ${trans.monto}")
        
        # 2. Eliminar transacciones incorrectas
        if transacciones_saldo_anterior:
            count_eliminadas = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.concepto_id == 54,
                TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
            ).delete()
            
            db.commit()
            print(f"✅ Eliminadas {count_eliminadas} transacciones SALDO DIA ANTERIOR")
        
        # 3. Obtener fechas únicas que necesitan regeneración
        fechas_con_saldo_total = db.query(TransaccionFlujoCaja.fecha).filter(
            TransaccionFlujoCaja.concepto_id == 85,  # SALDO TOTAL EN BANCOS
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).distinct().all()
        
        fechas_para_regenerar = [fecha[0] for fecha in fechas_con_saldo_total]
        fechas_para_regenerar.sort()
        
        print(f"📅 Fechas con SALDO TOTAL EN BANCOS: {fechas_para_regenerar}")
        
        # 4. Regenerar SALDO DIA ANTERIOR para cada fecha posterior
        servicio = DependenciasFlujoCajaService(db)
        regeneradas = 0
        
        for i, fecha in enumerate(fechas_para_regenerar):
            if i > 0:  # Solo fechas que tienen día anterior
                fecha_anterior = fechas_para_regenerar[i-1]
                print(f"\n🔄 Regenerando SALDO DIA ANTERIOR para {fecha} desde SALDO TOTAL BANCOS de {fecha_anterior}")
                
                # Usar el servicio para procesar dependencias
                resultado = servicio.procesar_dependencias_pagaduria(
                    fecha=fecha,
                    usuario_id=1,
                    compania_id=1
                )
                
                if resultado:
                    print(f"✅ Regeneración exitosa para {fecha}")
                    regeneradas += 1
                else:
                    print(f"❌ Error en regeneración para {fecha}")
        
        print(f"\n📊 RESUMEN DE LIMPIEZA:")
        print(f"  • Transacciones eliminadas: {count_eliminadas}")
        print(f"  • Fechas regeneradas: {regeneradas}")
        print(f"  • Total fechas disponibles: {len(fechas_para_regenerar)}")
        
        # 5. Verificar resultado final
        print(f"\n🔍 VERIFICACIÓN FINAL:")
        nuevas_transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 54,
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).all()
        
        for trans in nuevas_transacciones:
            print(f"  ✅ {trans.fecha}: Cuenta {trans.cuenta_id} = ${trans.monto} ({trans.descripcion})")
        
        print(f"\n🎉 LIMPIEZA COMPLETADA - {len(nuevas_transacciones)} SALDO DIA ANTERIOR regenerados correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_y_regenerar_saldo_anterior()
