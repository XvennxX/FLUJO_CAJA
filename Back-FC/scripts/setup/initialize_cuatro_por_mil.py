"""
Script para inicializar la configuración de Cuatro por Mil
Crea la tabla en la base de datos y genera configuraciones por defecto para las cuentas existentes.

Ejecutar desde la carpeta Back-FC:
    python scripts/setup/initialize_cuatro_por_mil.py
"""
import sys
import os
from datetime import date

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import engine, SessionLocal, Base
from app.models.cuatro_por_mil_config import CuatroPorMilConfig
from app.models import CuentaBancaria
import json

# IDs de conceptos permitidos para Cuatro por Mil
CONCEPTOS_CUATRO_POR_MIL = [68, 69, 76, 78]  # EMBARGOS, OTROS PAGOS, PAGO SOI, OTROS IMPTOS


def crear_tabla():
    """Crear la tabla cuatro_por_mil_config si no existe"""
    print("=" * 60)
    print("📦 CREANDO TABLA cuatro_por_mil_config")
    print("=" * 60)
    
    try:
        # Crear solo la tabla de CuatroPorMilConfig
        CuatroPorMilConfig.__table__.create(engine, checkfirst=True)
        print("✅ Tabla cuatro_por_mil_config creada/verificada exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        return False


def crear_configs_default():
    """Crear configuraciones por defecto para todas las cuentas bancarias"""
    print("\n" + "=" * 60)
    print("⚙️ CREANDO CONFIGURACIONES POR DEFECTO")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Obtener todas las cuentas bancarias
        cuentas = db.query(CuentaBancaria).all()
        print(f"📋 Encontradas {len(cuentas)} cuentas bancarias")
        
        creadas = 0
        existentes = 0
        
        for cuenta in cuentas:
            # Verificar si ya existe configuración para esta cuenta
            config_existente = db.query(CuatroPorMilConfig).filter(
                CuatroPorMilConfig.cuenta_bancaria_id == cuenta.id,
                CuatroPorMilConfig.activo == True
            ).first()
            
            if config_existente:
                existentes += 1
                continue
            
            # Crear configuración por defecto con todos los conceptos
            nueva_config = CuatroPorMilConfig(
                cuenta_bancaria_id=cuenta.id,
                conceptos_seleccionados=json.dumps(CONCEPTOS_CUATRO_POR_MIL),
                activo=True,
                fecha_vigencia_desde=date(2025, 1, 1)  # Vigente desde inicio de 2025
            )
            db.add(nueva_config)
            creadas += 1
        
        db.commit()
        
        print(f"\n📊 RESUMEN:")
        print(f"   - Configuraciones creadas: {creadas}")
        print(f"   - Configuraciones existentes: {existentes}")
        print(f"   - Total cuentas procesadas: {len(cuentas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando configuraciones: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def mostrar_configuraciones():
    """Mostrar todas las configuraciones de Cuatro por Mil"""
    print("\n" + "=" * 60)
    print("📋 CONFIGURACIONES DE CUATRO POR MIL")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        configs = db.query(CuatroPorMilConfig).filter(
            CuatroPorMilConfig.activo == True
        ).all()
        
        if not configs:
            print("⚠️ No hay configuraciones de Cuatro por Mil")
            return
        
        print(f"\n{'ID':>4} | {'Cuenta':>8} | {'Vigencia Desde':>14} | {'Conceptos'}")
        print("-" * 60)
        
        for config in configs:
            conceptos = json.loads(config.conceptos_seleccionados) if config.conceptos_seleccionados else []
            print(f"{config.id:>4} | {config.cuenta_bancaria_id:>8} | {str(config.fecha_vigencia_desde):>14} | {conceptos}")
        
        print(f"\n✅ Total: {len(configs)} configuraciones activas")
        
    except Exception as e:
        print(f"❌ Error consultando configuraciones: {e}")
    finally:
        db.close()


def main():
    print("\n" + "=" * 70)
    print("🔧 INICIALIZADOR DE CUATRO POR MIL - PAGADURÍA")
    print("=" * 70)
    print(f"\nConceptos base: {CONCEPTOS_CUATRO_POR_MIL}")
    print("  - 68: EMBARGOS")
    print("  - 69: OTROS PAGOS")
    print("  - 76: PAGO SOI")
    print("  - 78: OTROS IMPTOS")
    print("\nFórmula: CUATRO_POR_MIL = SUM(conceptos) × 4/1000")
    
    # Paso 1: Crear tabla
    if not crear_tabla():
        print("\n❌ Error en la creación de tabla. Abortando...")
        return
    
    # Paso 2: Crear configuraciones por defecto
    if not crear_configs_default():
        print("\n❌ Error creando configuraciones. Abortando...")
        return
    
    # Paso 3: Mostrar resumen
    mostrar_configuraciones()
    
    print("\n" + "=" * 70)
    print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n📝 Próximos pasos:")
    print("   1. Reiniciar el servidor backend")
    print("   2. Verificar endpoints en /api/v1/cuatro-por-mil/")
    print("   3. Probar en el frontend (Dashboard Pagaduría)")


if __name__ == "__main__":
    main()
