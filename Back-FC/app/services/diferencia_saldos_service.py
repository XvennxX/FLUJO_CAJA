"""
Servicio para manejo automático de DIFERENCIA SALDOS en Pagaduría
"""

from datetime import date
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

from ..core.database import get_db
from ..models.transacciones_flujo_caja import TransaccionFlujoCaja
from ..models.conceptos_flujo_caja import ConceptoFlujoCaja
from ..models.cuentas_bancarias import CuentaBancaria

import logging

logger = logging.getLogger(__name__)

class DiferenciaSaldosService:
    
    @staticmethod
    def obtener_concepto_por_nombre(db: Session, nombre: str) -> Optional[ConceptoFlujoCaja]:
        """Obtener concepto por nombre exacto"""
        return db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == nombre
        ).first()
    
    @staticmethod
    def obtener_monto_concepto(db: Session, concepto_id: int, cuenta_id: int, fecha: date) -> float:
        """Obtener el monto de un concepto para una cuenta específica en una fecha"""
        transaccion = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == concepto_id,
            TransaccionFlujoCaja.cuenta_id == cuenta_id,
            TransaccionFlujoCaja.fecha == fecha
        ).first()
        
        return float(transaccion.monto) if transaccion else 0.0
    
    @staticmethod
    def calcular_diferencia_saldos(db: Session, cuenta_id: int, fecha: date) -> float:
        """
        Calcular DIFERENCIA SALDOS = SALDOS EN BANCOS + SALDO DIA ANTERIOR
        """
        try:
            # Buscar los conceptos necesarios
            concepto_saldos_bancos = DiferenciaSaldosService.obtener_concepto_por_nombre(
                db, "SALDOS EN BANCOS"
            )
            concepto_saldo_anterior = DiferenciaSaldosService.obtener_concepto_por_nombre(
                db, "SALDO DIA ANTERIOR"
            )
            
            if not concepto_saldos_bancos:
                logger.warning("No se encontró el concepto 'SALDOS EN BANCOS'")
                return 0.0
                
            if not concepto_saldo_anterior:
                logger.warning("No se encontró el concepto 'SALDO DIA ANTERIOR'")
                return 0.0
            
            # Obtener montos
            monto_saldos_bancos = DiferenciaSaldosService.obtener_monto_concepto(
                db, concepto_saldos_bancos.id, cuenta_id, fecha
            )
            
            monto_saldo_anterior = DiferenciaSaldosService.obtener_monto_concepto(
                db, concepto_saldo_anterior.id, cuenta_id, fecha
            )
            
            # Calcular diferencia
            diferencia = monto_saldos_bancos + monto_saldo_anterior
            
            logger.info(
                f"Diferencia Saldos calculada para cuenta {cuenta_id} fecha {fecha}: "
                f"SALDOS_BANCOS({monto_saldos_bancos}) + SALDO_ANTERIOR({monto_saldo_anterior}) = {diferencia}"
            )
            
            return diferencia
            
        except Exception as e:
            logger.error(f"Error calculando diferencia saldos: {e}")
            return 0.0
    
    @staticmethod
    def crear_o_actualizar_diferencia_saldos(
        db: Session, 
        cuenta_id: int, 
        fecha: date, 
        usuario_id: int,
        compania_id: int
    ) -> Optional[TransaccionFlujoCaja]:
        """
        Crear o actualizar la transacción de DIFERENCIA SALDOS automáticamente
        """
        try:
            # Buscar el concepto DIFERENCIA SALDOS
            concepto_diferencia = DiferenciaSaldosService.obtener_concepto_por_nombre(
                db, "DIFERENCIA SALDOS"
            )
            
            if not concepto_diferencia:
                logger.error("No se encontró el concepto 'DIFERENCIA SALDOS'")
                return None
            
            # Calcular el nuevo valor
            nuevo_monto = DiferenciaSaldosService.calcular_diferencia_saldos(db, cuenta_id, fecha)
            
            # Buscar transacción existente
            transaccion_existente = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.concepto_id == concepto_diferencia.id,
                TransaccionFlujoCaja.cuenta_id == cuenta_id,
                TransaccionFlujoCaja.fecha == fecha
            ).first()
            
            if transaccion_existente:
                # Actualizar transacción existente
                transaccion_existente.monto = nuevo_monto
                transaccion_existente.descripcion = f"Calculado automáticamente: SALDOS_BANCOS + SALDO_ANTERIOR"
                logger.info(f"Actualizada DIFERENCIA SALDOS para cuenta {cuenta_id}: {nuevo_monto}")
            else:
                # Crear nueva transacción
                transaccion_existente = TransaccionFlujoCaja(
                    fecha=fecha,
                    concepto_id=concepto_diferencia.id,
                    cuenta_id=cuenta_id,
                    monto=nuevo_monto,
                    descripcion="Calculado automáticamente: SALDOS_BANCOS + SALDO_ANTERIOR",
                    usuario_id=usuario_id,
                    area="PAGADURIA",
                    compania_id=compania_id
                )
                db.add(transaccion_existente)
                logger.info(f"Creada DIFERENCIA SALDOS para cuenta {cuenta_id}: {nuevo_monto}")
            
            db.commit()
            return transaccion_existente
            
        except Exception as e:
            logger.error(f"Error creando/actualizando diferencia saldos: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def procesar_diferencias_saldos_para_fecha(
        db: Session, 
        fecha: date, 
        usuario_id: int
    ) -> Dict[str, any]:
        """
        Procesar todas las diferencias de saldos para una fecha específica
        """
        try:
            cuentas = db.query(CuentaBancaria).all()
            resultados = {
                "procesadas": 0,
                "errores": 0,
                "cuentas": []
            }
            
            for cuenta in cuentas:
                try:
                    transaccion = DiferenciaSaldosService.crear_o_actualizar_diferencia_saldos(
                        db, cuenta.id, fecha, usuario_id, cuenta.compania_id
                    )
                    
                    if transaccion:
                        resultados["procesadas"] += 1
                        resultados["cuentas"].append({
                            "cuenta_id": cuenta.id,
                            "numero_cuenta": cuenta.numero_cuenta,
                            "monto": float(transaccion.monto),
                            "status": "procesada"
                        })
                    else:
                        resultados["errores"] += 1
                        resultados["cuentas"].append({
                            "cuenta_id": cuenta.id,
                            "numero_cuenta": cuenta.numero_cuenta,
                            "status": "error"
                        })
                        
                except Exception as e:
                    logger.error(f"Error procesando cuenta {cuenta.id}: {e}")
                    resultados["errores"] += 1
                    resultados["cuentas"].append({
                        "cuenta_id": cuenta.id,
                        "numero_cuenta": cuenta.numero_cuenta,
                        "status": "error",
                        "error": str(e)
                    })
            
            logger.info(f"Procesamiento completado: {resultados['procesadas']} exitosas, {resultados['errores']} errores")
            return resultados
            
        except Exception as e:
            logger.error(f"Error en procesamiento masivo: {e}")
            return {"error": str(e)}
