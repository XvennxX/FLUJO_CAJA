#!/usr/bin/env python3
"""
Script para implementar auto-cálculo multicuenta para SUB TOTAL TESORERÍA
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.cuentas_bancarias import CuentaBancaria
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.services.dependencias_flujo_caja_service import DependenciasFlujo_CajaService
from datetime import date
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Función principal"""
    logger.info("=== IMPLEMENTANDO AUTO-CÁLCULO MULTICUENTA ===")
    
    db = next(get_db())
    fecha_actual = date.today()
    
    try:
        # 1. Obtener todas las cuentas bancarias activas
        logger.info("1. Obteniendo todas las cuentas bancarias...")
        cuentas = db.query(CuentaBancaria).filter(
            CuentaBancaria.activo == True
        ).all()
        
        logger.info(f"   Encontradas {len(cuentas)} cuentas activas")
        for cuenta in cuentas:
            logger.info(f"   - Cuenta {cuenta.id}: {cuenta.numero}")
        
        # 2. Verificar concepto SUB TOTAL TESORERÍA
        logger.info("\n2. Verificando concepto SUB TOTAL TESORERÍA...")
        concepto_subtotal = db.query(ConceptosFlujo_Caja).filter(
            ConceptosFlujo_Caja.id == 50
        ).first()
        
        if concepto_subtotal:
            logger.info(f"   ✓ Concepto encontrado: {concepto_subtotal.nombre}")
            logger.info(f"   ✓ Fórmula: {concepto_subtotal.formula}")
        else:
            logger.error("   ✗ Concepto SUB TOTAL TESORERÍA no encontrado!")
            return
        
        # 3. Verificar estado actual por cuenta
        logger.info(f"\n3. Verificando estado actual para fecha {fecha_actual}...")
        for cuenta in cuentas:
            # Contar transacciones de tesorería (conceptos 5-49)
            count_tesoreria = db.query(TransaccionesFlujo_Caja).filter(
                TransaccionesFlujo_Caja.fecha == fecha_actual,
                TransaccionesFlujo_Caja.concepto_id >= 5,
                TransaccionesFlujo_Caja.concepto_id <= 49,
                TransaccionesFlujo_Caja.cuenta_id == cuenta.id
            ).count()
            
            # Verificar si existe SUB TOTAL TESORERÍA para esta cuenta
            subtotal_existe = db.query(TransaccionesFlujo_Caja).filter(
                TransaccionesFlujo_Caja.fecha == fecha_actual,
                TransaccionesFlujo_Caja.concepto_id == 50,
                TransaccionesFlujo_Caja.cuenta_id == cuenta.id
            ).first()
            
            logger.info(f"   Cuenta {cuenta.numero}: {count_tesoreria} transacciones tesorería, "
                       f"SUB TOTAL: {'SÍ' if subtotal_existe else 'NO'}")
        
        # 4. Crear/actualizar SUB TOTAL TESORERÍA para todas las cuentas
        logger.info(f"\n4. Implementando auto-cálculo para todas las cuentas...")
        
        dependencias_service = DependenciasFlujo_CajaService()
        usuario_id = 1  # Usuario del sistema para auto-cálculos
        
        for cuenta in cuentas:
            logger.info(f"\n   Procesando cuenta {cuenta.numero} (ID: {cuenta.id})...")
            
            # Calcular suma de conceptos 5-49 para esta cuenta
            suma_query = db.query(
                db.func.COALESCE(db.func.sum(TransaccionesFlujo_Caja.monto), 0)
            ).filter(
                TransaccionesFlujo_Caja.fecha == fecha_actual,
                TransaccionesFlujo_Caja.concepto_id >= 5,
                TransaccionesFlujo_Caja.concepto_id <= 49,
                TransaccionesFlujo_Caja.cuenta_id == cuenta.id
            )
            
            suma_tesoreria = suma_query.scalar() or 0
            logger.info(f"      Suma conceptos 5-49: ${suma_tesoreria:,.2f}")
            
            # Verificar si ya existe transacción SUB TOTAL para esta cuenta
            transaccion_existente = db.query(TransaccionesFlujo_Caja).filter(
                TransaccionesFlujo_Caja.fecha == fecha_actual,
                TransaccionesFlujo_Caja.concepto_id == 50,
                TransaccionesFlujo_Caja.cuenta_id == cuenta.id
            ).first()
            
            if transaccion_existente:
                logger.info(f"      Transacción existente: ${transaccion_existente.monto:,.2f}")
                if abs(transaccion_existente.monto - suma_tesoreria) < 0.01:
                    logger.info("      ✓ Valor correcto, no requiere actualización")
                    continue
                else:
                    logger.info("      → Actualizando valor...")
                    transaccion_existente.monto = suma_tesoreria
                    transaccion_existente.auditoria = {
                        "usuario_modificacion": usuario_id,
                        "fecha_modificacion": fecha_actual.isoformat(),
                        "motivo": "Auto-cálculo multicuenta",
                        "valor_anterior": transaccion_existente.monto,
                        "valor_nuevo": suma_tesoreria
                    }
            else:
                if suma_tesoreria == 0:
                    logger.info("      → Creando transacción con valor $0...")
                else:
                    logger.info("      → Creando nueva transacción...")
                
                nueva_transaccion = TransaccionesFlujo_Caja(
                    fecha=fecha_actual,
                    concepto_id=50,
                    cuenta_id=cuenta.id,
                    monto=suma_tesoreria,
                    descripcion="Auto-calculado: SUB-TOTAL TESORERÍA",
                    usuario_id=usuario_id,
                    area="SISTEMA",
                    compania_id=1,
                    auditoria={
                        "usuario_creacion": usuario_id,
                        "fecha_creacion": fecha_actual.isoformat(),
                        "motivo": "Auto-cálculo multicuenta",
                        "sistema": "dependencias_flujo_caja_service",
                        "formula_aplicada": "SUMA(5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49)"
                    }
                )
                db.add(nueva_transaccion)
            
            logger.info(f"      ✓ Procesada cuenta {cuenta.numero}")
        
        # 5. Confirmar cambios
        logger.info(f"\n5. Confirmando cambios...")
        db.commit()
        logger.info("   ✓ Cambios guardados en la base de datos")
        
        # 6. Verificar resultado final
        logger.info(f"\n6. Verificando resultado final...")
        for cuenta in cuentas:
            subtotal = db.query(TransaccionesFlujo_Caja).filter(
                TransaccionesFlujo_Caja.fecha == fecha_actual,
                TransaccionesFlujo_Caja.concepto_id == 50,
                TransaccionesFlujo_Caja.cuenta_id == cuenta.id
            ).first()
            
            if subtotal:
                logger.info(f"   ✓ Cuenta {cuenta.numero}: SUB TOTAL = ${subtotal.monto:,.2f}")
            else:
                logger.warning(f"   ⚠ Cuenta {cuenta.numero}: Sin SUB TOTAL")
        
        logger.info(f"\n=== IMPLEMENTACIÓN COMPLETADA ===")
        
    except Exception as e:
        logger.error(f"Error durante la implementación: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
