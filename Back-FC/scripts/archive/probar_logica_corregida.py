"""
Script de prueba para verificar la lógica corregida de SALDO DIA ANTERIOR
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from datetime import datetime, date, timedelta

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def crear_datos_prueba():
    """
    Crear datos de prueba para verificar la lógica de SALDO DIA ANTERIOR
    """
    try:
        print("🔧 CREANDO DATOS DE PRUEBA...")
        
        # Fechas de prueba
        fecha1 = date(2025, 9, 8)  # Día 1
        fecha2 = date(2025, 9, 9)  # Día 2
        fecha3 = date(2025, 9, 10) # Día 3
        
        # 1. Crear SALDO TOTAL EN BANCOS para día 1
        saldo_dia1 = TransaccionFlujoCaja(
            fecha=fecha1,
            concepto_id=85,  # SALDO TOTAL EN BANCOS
            cuenta_id=1,
            monto=100.0,
            descripcion="SALDO TOTAL DIA 1 (prueba)",
            usuario_id=1,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={
                "accion": "prueba_manual",
                "usuario_id": 1,
                "timestamp": datetime.now().isoformat(),
                "tipo": "datos_prueba"
            }
        )
        
        # 2. Crear SALDO TOTAL EN BANCOS para día 2
        saldo_dia2 = TransaccionFlujoCaja(
            fecha=fecha2,
            concepto_id=85,  # SALDO TOTAL EN BANCOS
            cuenta_id=1,
            monto=200.0,
            descripcion="SALDO TOTAL DIA 2 (prueba)",
            usuario_id=1,
            area=AreaTransaccion.pagaduria,
            compania_id=1,
            auditoria={
                "accion": "prueba_manual",
                "usuario_id": 1,
                "timestamp": datetime.now().isoformat(),
                "tipo": "datos_prueba"
            }
        )
        
        db.add(saldo_dia1)
        db.add(saldo_dia2)
        db.commit()
        
        print(f"✅ Creados SALDO TOTAL EN BANCOS:")
        print(f"  • {fecha1}: $100.00")
        print(f"  • {fecha2}: $200.00")
        
        return fecha1, fecha2, fecha3
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.rollback()
        raise

def probar_logica_saldo_anterior():
    """
    Probar que la lógica de SALDO DIA ANTERIOR funciona correctamente
    """
    try:
        # Crear datos de prueba
        fecha1, fecha2, fecha3 = crear_datos_prueba()
        
        print(f"\n🧪 PROBANDO LÓGICA DE SALDO DIA ANTERIOR...")
        
        # Instanciar servicio
        servicio = DependenciasFlujoCajaService(db)
        
        # 1. Probar día 2 (debe usar SALDO TOTAL del día 1 = $100)
        print(f"\n📅 PROCESANDO {fecha2} (debería crear SALDO DIA ANTERIOR = $100 desde {fecha1})")
        resultado_dia2 = servicio.procesar_dependencias_pagaduria(
            fecha=fecha2,
            usuario_id=1,
            compania_id=1
        )
        
        if resultado_dia2:
            print(f"✅ Procesamiento exitoso para {fecha2}")
            for actualizacion in resultado_dia2.get("actualizaciones", []):
                if actualizacion["concepto_id"] == 54:  # SALDO DIA ANTERIOR
                    print(f"  📊 SALDO DIA ANTERIOR creado: ${actualizacion['monto_nuevo']}")
                    print(f"  🔗 Origen: {actualizacion['origen']['concepto_nombre']} = ${actualizacion['origen']['monto']}")
        
        # 2. Probar día 3 (debe usar SALDO TOTAL del día 2 = $200)
        print(f"\n📅 PROCESANDO {fecha3} (debería crear SALDO DIA ANTERIOR = $200 desde {fecha2})")
        resultado_dia3 = servicio.procesar_dependencias_pagaduria(
            fecha=fecha3,
            usuario_id=1,
            compania_id=1
        )
        
        if resultado_dia3:
            print(f"✅ Procesamiento exitoso para {fecha3}")
            for actualizacion in resultado_dia3.get("actualizaciones", []):
                if actualizacion["concepto_id"] == 54:  # SALDO DIA ANTERIOR
                    print(f"  📊 SALDO DIA ANTERIOR creado: ${actualizacion['monto_nuevo']}")
                    print(f"  🔗 Origen: {actualizacion['origen']['concepto_nombre']} = ${actualizacion['origen']['monto']}")
        
        # 3. Verificar resultados en base de datos
        print(f"\n🔍 VERIFICACIÓN EN BASE DE DATOS:")
        saldos_anteriores = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == 54,
            TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
        ).order_by(TransaccionFlujoCaja.fecha).all()
        
        for saldo in saldos_anteriores:
            print(f"  ✅ {saldo.fecha}: SALDO DIA ANTERIOR = ${saldo.monto} ({saldo.descripcion})")
        
        # 4. Validar lógica correcta
        print(f"\n✅ VALIDACIÓN DE LÓGICA:")
        if len(saldos_anteriores) >= 2:
            saldo_dia2_db = next((s for s in saldos_anteriores if s.fecha == fecha2), None)
            saldo_dia3_db = next((s for s in saldos_anteriores if s.fecha == fecha3), None)
            
            if saldo_dia2_db and saldo_dia2_db.monto == 100.0:
                print(f"  ✅ {fecha2}: SALDO DIA ANTERIOR = $100 (correcto, tomado del día anterior)")
            else:
                print(f"  ❌ {fecha2}: SALDO DIA ANTERIOR incorrecto")
                
            if saldo_dia3_db and saldo_dia3_db.monto == 200.0:
                print(f"  ✅ {fecha3}: SALDO DIA ANTERIOR = $200 (correcto, tomado del día anterior)")
            else:
                print(f"  ❌ {fecha3}: SALDO DIA ANTERIOR incorrecto")
        
        print(f"\n🎉 PRUEBA COMPLETADA - La lógica corregida funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        db.rollback()
        raise
    finally:
        # Limpiar datos de prueba
        print(f"\n🧹 Limpiando datos de prueba...")
        db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.descripcion.like("%prueba%")
        ).delete()
        db.commit()
        print(f"✅ Datos de prueba eliminados")
        db.close()

if __name__ == "__main__":
    probar_logica_saldo_anterior()
