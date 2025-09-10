"""
Servicio para calcular y guardar automáticamente el SALDO INICIAL
basado en el SALDO FINAL del día anterior.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.models.cuentas_bancarias import CuentaBancaria
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


class SaldoInicialService:
    
    @staticmethod
    def calcular_saldo_final_dia_anterior(
        fecha_actual: datetime,
        cuenta_id: Optional[int] = None,
        db: Session = None
    ) -> float:
        """
        Calcula el SALDO FINAL del día anterior (SALDO NETO PAGADURÍA + SUB-TOTAL TESORERÍA)
        """
        try:
            if not db:
                return 0.0
                
            # Fecha del día anterior
            fecha_anterior = fecha_actual - timedelta(days=1)
            fecha_anterior_str = fecha_anterior.strftime('%Y-%m-%d')
            
            logger.info(f"Calculando saldo final para fecha anterior: {fecha_anterior_str}")
            
            # Obtener todas las transacciones del día anterior
            query = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_anterior_str
            )
            
            if cuenta_id:
                query = query.filter(TransaccionFlujoCaja.cuenta_id == cuenta_id)
            
            transacciones_dia_anterior = query.all()
            
            if not transacciones_dia_anterior:
                logger.info(f"No hay transacciones para el día anterior {fecha_anterior_str}")
                return 0.0
            
            # Obtener conceptos para clasificar
            conceptos = db.query(ConceptoFlujoCaja).all()
            
            # Buscar el concepto "SALDO FINAL CUENTAS" específicamente
            saldo_final_cuentas_concepto = next(
                (c for c in conceptos if c.nombre == 'SALDO FINAL CUENTAS'), 
                None
            )
            
            if not saldo_final_cuentas_concepto:
                logger.warning("No se encontró el concepto 'SALDO FINAL CUENTAS'")
                return 0.0
            
            # Buscar las transacciones del día anterior para SALDO FINAL CUENTAS específicamente
            transacciones_saldo_final = [
                t for t in transacciones_dia_anterior 
                if t.concepto_id == saldo_final_cuentas_concepto.id and
                   (not cuenta_id or t.cuenta_id == cuenta_id)
            ]
            
            # Sumar los montos de SALDO FINAL CUENTAS del día anterior
            saldo_final = sum(t.monto for t in transacciones_saldo_final)
            
            logger.info(f"Saldo final calculado desde SALDO FINAL CUENTAS para {fecha_anterior_str}: {saldo_final}")
            logger.debug(f"  - Concepto ID: {saldo_final_cuentas_concepto.id}")
            logger.debug(f"  - Transacciones encontradas: {len(transacciones_saldo_final)}")
            logger.debug(f"  - Cuenta ID filtro: {cuenta_id or 'todas'}")
            
            return saldo_final
            
        except Exception as e:
            logger.error(f"Error calculando saldo final día anterior: {e}")
            return 0.0
    
    @staticmethod
    def crear_o_actualizar_saldo_inicial(
        fecha: datetime,
        cuenta_id: int,
        compania_id: int,
        db: Session
    ) -> Optional[TransaccionFlujoCaja]:
        """
        Crea o actualiza la transacción de SALDO INICIAL basada en el SALDO FINAL del día anterior
        Solo crea/actualiza si es necesario (si no existe o si el valor cambió)
        """
        try:
            # Buscar el concepto SALDO INICIAL
            concepto_saldo_inicial = db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.nombre == 'SALDO INICIAL'
            ).first()
            
            if not concepto_saldo_inicial:
                logger.error("No se encontró el concepto 'SALDO INICIAL'")
                return None
            
            # Calcular el monto basado en el día anterior
            monto_saldo_inicial = SaldoInicialService.calcular_saldo_final_dia_anterior(
                fecha, cuenta_id, db
            )
            
            fecha_str = fecha.strftime('%Y-%m-%d')
            
            # Buscar si ya existe una transacción de SALDO INICIAL para esta fecha y cuenta
            transaccion_existente = db.query(TransaccionFlujoCaja).filter(
                and_(
                    TransaccionFlujoCaja.concepto_id == concepto_saldo_inicial.id,
                    TransaccionFlujoCaja.cuenta_id == cuenta_id,
                    TransaccionFlujoCaja.fecha == fecha_str
                )
            ).first()
            
            if transaccion_existente:
                # Solo actualizar si el monto es diferente
                if transaccion_existente.monto != monto_saldo_inicial:
                    logger.info(f"Actualizando SALDO INICIAL: {transaccion_existente.monto} -> {monto_saldo_inicial}")
                    transaccion_existente.monto = monto_saldo_inicial
                    transaccion_existente.fecha_actualizacion = datetime.utcnow()
                    db.commit()
                    return transaccion_existente
                else:
                    logger.debug(f"SALDO INICIAL ya existe con valor correcto: {monto_saldo_inicial}")
                    return transaccion_existente
                
            else:
                # Solo crear si el monto no es cero
                if monto_saldo_inicial != 0:
                    # Crear nueva transacción
                    nueva_transaccion = TransaccionFlujoCaja(
                        concepto_id=concepto_saldo_inicial.id,
                        cuenta_id=cuenta_id,
                        compania_id=compania_id,
                        fecha=fecha_str,
                        monto=monto_saldo_inicial,
                        fecha_creacion=datetime.utcnow(),
                        fecha_actualizacion=datetime.utcnow()
                    )
                    
                    db.add(nueva_transaccion)
                    db.commit()
                    
                    logger.info(f"Creada nueva transacción SALDO INICIAL: {monto_saldo_inicial}")
                    return nueva_transaccion
                else:
                    logger.debug(f"No se crea SALDO INICIAL porque el monto es 0")
                    return None
            
        except Exception as e:
            logger.error(f"Error creando/actualizando SALDO INICIAL: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def procesar_saldos_iniciales_para_fecha(
        fecha: datetime,
        compania_id: Optional[int] = None,
        db: Session = None
    ) -> List[TransaccionFlujoCaja]:
        """
        Procesa automáticamente los SALDOS INICIALES para todas las cuentas de una fecha específica
        """
        try:
            if not db:
                return []
            
            # Obtener todas las cuentas bancarias
            query_cuentas = db.query(CuentaBancaria)
            
            if compania_id:
                query_cuentas = query_cuentas.filter(CuentaBancaria.compania_id == compania_id)
            
            cuentas = query_cuentas.all()
            
            transacciones_creadas = []
            
            for cuenta in cuentas:
                transaccion = SaldoInicialService.crear_o_actualizar_saldo_inicial(
                    fecha, cuenta.id, cuenta.compania_id, db
                )
                
                if transaccion:
                    transacciones_creadas.append(transaccion)
            
            logger.info(f"Procesados SALDOS INICIALES para {len(transacciones_creadas)} cuentas")
            return transacciones_creadas
            
        except Exception as e:
            logger.error(f"Error procesando saldos iniciales para fecha: {e}")
            return []
