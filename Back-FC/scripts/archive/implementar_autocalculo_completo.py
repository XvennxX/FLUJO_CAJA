#!/usr/bin/env python3
"""
Script para implementar auto-cálculo completo para TODOS los conceptos calculados
en TODAS las cuentas bancarias del sistema.

Conceptos a implementar:
- ID 4: SALDO NETO INICIAL PAGADURÍA = SUMA(1,2,3)
- ID 50: SUB-TOTAL TESORERÍA = SUMA(5-49) [ya existe]
- ID 51: SALDO FINAL CUENTAS = SUMA(4,50)
"""

import logging
import sys
import os
from datetime import date

# Agregar el directorio raíz al path para las importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.cuentas_bancarias import CuentaBancaria
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from sqlalchemy import func

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal"""
    print("="*60)
    print("IMPLEMENTACIÓN AUTO-CÁLCULO COMPLETO MULTICUENTA")
    print("="*60)
    
    try:
        # 1. Obtener conexión a la base de datos
        db = next(get_db())
        fecha_actual = date.today()
        usuario_id = 1  # Usuario sistema
        
        logger.info(f"Fecha de procesamiento: {fecha_actual}")
        logger.info(f"Usuario: {usuario_id}")
        
        # 2. Obtener todos los conceptos que requieren auto-cálculo
        conceptos_calculados = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.formula_dependencia.isnot(None),
            ConceptoFlujoCaja.formula_dependencia != ''
        ).order_by(ConceptoFlujoCaja.id).all()
        
        logger.info(f"\n=== CONCEPTOS A PROCESAR ===")
        for concepto in conceptos_calculados:
            logger.info(f"ID {concepto.id}: {concepto.nombre} → {concepto.formula_dependencia}")
        
        # 3. Obtener todas las cuentas bancarias
        cuentas = db.query(CuentaBancaria).order_by(CuentaBancaria.id).all()
        logger.info(f"\n=== CUENTAS BANCARIAS ===")
        logger.info(f"Total cuentas a procesar: {len(cuentas)}")
        
        # 4. Instanciar el servicio de dependencias
        servicio_dependencias = DependenciasFlujoCajaService(db)
        
        # 5. Procesar cada concepto para cada cuenta
        transacciones_creadas = 0
        transacciones_actualizadas = 0
        
        # Procesar en el orden correcto de dependencias:
        # 1ro: SALDO NETO INICIAL PAGADURÍA (ID 4) - depende de conceptos 1,2,3
        # 2do: SUB-TOTAL TESORERÍA (ID 50) - depende de conceptos 5-49
        # 3ro: SALDO FINAL CUENTAS (ID 51) - depende de conceptos 4,50
        
        orden_procesamiento = [4, 50, 51]
        
        for concepto_id in orden_procesamiento:
            concepto = next((c for c in conceptos_calculados if c.id == concepto_id), None)
            if not concepto:
                continue
                
            logger.info(f"\n{'='*50}")
            logger.info(f"PROCESANDO: {concepto.nombre} (ID {concepto.id})")
            logger.info(f"Formula: {concepto.formula_dependencia}")
            logger.info(f"{'='*50}")
            
            for i, cuenta in enumerate(cuentas, 1):
                logger.info(f"\n[{i:2d}/{len(cuentas)}] Procesando cuenta {cuenta.numero_cuenta or 'N/A'} (ID: {cuenta.id})")
                
                # Calcular el valor según la fórmula
                valor_calculado = calcular_valor_formula(db, concepto.formula_dependencia, 
                                                       cuenta.id, fecha_actual)
                logger.info(f"    Valor calculado: ${valor_calculado:,.2f}")
                
                # Verificar si ya existe transacción para este concepto y cuenta
                transaccion_existente = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_actual,
                    TransaccionFlujoCaja.concepto_id == concepto.id,
                    TransaccionFlujoCaja.cuenta_id == cuenta.id
                ).first()
                
                if transaccion_existente:
                    # Actualizar si el valor es diferente
                    if abs(transaccion_existente.monto - valor_calculado) >= 0.01:
                        logger.info(f"    → Actualizando: ${transaccion_existente.monto:,.2f} → ${valor_calculado:,.2f}")
                        transaccion_existente.monto = valor_calculado
                        transaccion_existente.auditoria = {
                            "usuario_modificacion": usuario_id,
                            "fecha_modificacion": fecha_actual.isoformat(),
                            "motivo": "Auto-cálculo multicuenta completo",
                            "valor_anterior": transaccion_existente.monto,
                            "valor_nuevo": valor_calculado,
                            "formula_aplicada": concepto.formula_dependencia
                        }
                        transacciones_actualizadas += 1
                    else:
                        logger.info(f"    ✓ Ya existe con valor correcto")
                else:
                    # Crear nueva transacción
                    logger.info(f"    → Creando nueva transacción: ${valor_calculado:,.2f}")
                    
                    # Determinar el área según el concepto
                    area = "pagaduria" if concepto.id == 4 else "tesoreria"
                    
                    nueva_transaccion = TransaccionFlujoCaja(
                        fecha=fecha_actual,
                        concepto_id=concepto.id,
                        cuenta_id=cuenta.id,
                        monto=valor_calculado,
                        descripcion=f"Auto-calculado: {concepto.nombre}",
                        usuario_id=usuario_id,
                        area=area,
                        compania_id=1,
                        auditoria={
                            "usuario_creacion": usuario_id,
                            "fecha_creacion": fecha_actual.isoformat(),
                            "motivo": "Auto-cálculo multicuenta completo",
                            "sistema": "dependencias_flujo_caja_service",
                            "formula_aplicada": concepto.formula_dependencia
                        }
                    )
                    db.add(nueva_transaccion)
                    transacciones_creadas += 1
                
                logger.info(f"    ✓ Procesada cuenta {cuenta.numero_cuenta or 'N/A'}")
        
        # 6. Confirmar cambios
        logger.info(f"\n{'='*50}")
        logger.info(f"CONFIRMANDO CAMBIOS...")
        logger.info(f"{'='*50}")
        db.commit()
        
        # 7. Resumen final
        logger.info(f"\n🎉 IMPLEMENTACIÓN COMPLETADA EXITOSAMENTE")
        logger.info(f"  - Transacciones creadas: {transacciones_creadas}")
        logger.info(f"  - Transacciones actualizadas: {transacciones_actualizadas}")
        logger.info(f"  - Total cuentas procesadas: {len(cuentas)}")
        logger.info(f"  - Conceptos implementados: {len(orden_procesamiento)}")
        
        # 8. Validación final
        logger.info(f"\n=== VALIDACIÓN FINAL ===")
        for concepto_id in orden_procesamiento:
            count = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.concepto_id == concepto_id,
                TransaccionFlujoCaja.fecha == fecha_actual
            ).count()
            concepto = next((c for c in conceptos_calculados if c.id == concepto_id), None)
            logger.info(f"  - {concepto.nombre if concepto else f'Concepto {concepto_id}'}: {count} transacciones")
        
    except Exception as e:
        logger.error(f"Error durante la implementación: {e}")
        if 'db' in locals():
            db.rollback()
        raise
    finally:
        if 'db' in locals():
            db.close()

def calcular_valor_formula(db, formula, cuenta_id, fecha):
    """
    Calcula el valor de una fórmula para una cuenta específica
    """
    if not formula or not formula.startswith('SUMA('):
        return 0
    
    # Extraer los conceptos de la fórmula SUMA(...)
    conceptos_str = formula[5:-1]  # Quitar "SUMA(" y ")"
    
    if ',' in conceptos_str:
        # Lista de conceptos separados por comas: SUMA(1,2,3)
        conceptos = [int(x.strip()) for x in conceptos_str.split(',')]
    elif '-' in conceptos_str:
        # Rango de conceptos: SUMA(5-49) -> convertir a lista
        inicio, fin = map(int, conceptos_str.split('-'))
        conceptos = list(range(inicio, fin + 1))
    else:
        # Un solo concepto
        conceptos = [int(conceptos_str)]
    
    # Calcular la suma de los conceptos
    suma_query = db.query(func.coalesce(func.sum(TransaccionFlujoCaja.monto), 0)).filter(
        TransaccionFlujoCaja.fecha == fecha,
        TransaccionFlujoCaja.concepto_id.in_(conceptos),
        TransaccionFlujoCaja.cuenta_id == cuenta_id
    )
    
    return suma_query.scalar() or 0

if __name__ == "__main__":
    main()
