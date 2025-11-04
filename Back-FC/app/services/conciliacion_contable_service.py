"""
Servicio para manejar la lógica de conciliaciones contables
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal

from ..models.conciliacion_contable import ConciliacionContable
from ..models.companias import Compania
from ..models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from ..schemas.conciliacion_contable import (
    ConciliacionContableCreate,
    ConciliacionContableUpdate,
    EmpresaConciliacionResponse,
    ConciliacionFechaResponse,
    CompaniaResponse
)

class ConciliacionContableService:
    """
    Servicio para manejar conciliaciones contables
    """
    
    @staticmethod
    def calcular_totales_por_area(db: Session, empresa_id: int, fecha: date) -> Dict[str, Decimal]:
        """
        Calcula los totales de Pagaduría y Tesorería para una empresa en una fecha específica
        Los valores se obtienen de los conceptos de subtotal específicos:
        - SUB-TOTAL TESORERÍA (concepto_id = 50)
        - SUBTOTAL MOVIMIENTO PAGADURIA (concepto_id = 82)
        """
        # Total Pagaduría - buscar concepto SUBTOTAL MOVIMIENTO PAGADURIA (ID 82)
        transaccion_pagaduria = db.query(TransaccionFlujoCaja).filter(
            and_(
                TransaccionFlujoCaja.compania_id == empresa_id,
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == 82  # SUBTOTAL MOVIMIENTO PAGADURIA
            )
        ).first()
        
        total_pagaduria = transaccion_pagaduria.monto if transaccion_pagaduria else Decimal('0.00')
        
        # Total Tesorería - buscar concepto SUB-TOTAL TESORERÍA (ID 50)
        transaccion_tesoreria = db.query(TransaccionFlujoCaja).filter(
            and_(
                TransaccionFlujoCaja.compania_id == empresa_id,
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == 50  # SUB-TOTAL TESORERÍA
            )
        ).first()
        
        total_tesoreria = transaccion_tesoreria.monto if transaccion_tesoreria else Decimal('0.00')
        
        return {
            "pagaduria": total_pagaduria,
            "tesoreria": total_tesoreria,
            "total": total_pagaduria + total_tesoreria
        }
    
    @staticmethod
    def obtener_conciliacion_por_fecha(db: Session, fecha: date) -> ConciliacionFechaResponse:
        """
        Obtiene todas las empresas con sus datos de conciliación para una fecha específica
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📊 Iniciando obtención de conciliación para fecha: {fecha}")
        
        # Obtener las primeras 3 empresas (Capitalizadora, Seguros Bolívar, Comerciales)
        empresas = db.query(Compania).limit(3).all()
        logger.info(f"🏢 Empresas encontradas: {len(empresas)}")
        
        empresas_conciliacion = []
        
        for empresa in empresas:
            logger.info(f"  📋 Procesando empresa: {empresa.nombre} (ID: {empresa.id})")
            
            # Buscar conciliación existente
            conciliacion = db.query(ConciliacionContable).filter(
                and_(
                    ConciliacionContable.empresa_id == empresa.id,
                    ConciliacionContable.fecha == fecha
                )
            ).first()
            
            # Calcular totales automáticamente desde transacciones
            totales = ConciliacionContableService.calcular_totales_por_area(
                db, empresa.id, fecha
            )
            
            # Si existe conciliación, usar esos datos
            if conciliacion:
                # Actualizar totales calculados
                conciliacion.total_pagaduria = totales["pagaduria"]
                conciliacion.total_tesoreria = totales["tesoreria"]
                
                # Calcular diferencia: tratar total_centralizadora como 0 si es None
                # Diferencia = Total Calculado - (Total Centralizadora o 0)
                centralizadora = conciliacion.total_centralizadora or Decimal('0.00')
                diferencia = conciliacion.total_calculado - centralizadora
                
                db.commit()
                
                empresa_data = EmpresaConciliacionResponse(
                    id=conciliacion.id,
                    compania_id=empresa.id,
                    compania=CompaniaResponse(id=empresa.id, nombre=empresa.nombre),
                    total_pagaduria=conciliacion.total_pagaduria,
                    total_tesoreria=conciliacion.total_tesoreria,
                    total_calculado=conciliacion.total_calculado,
                    total_centralizadora=conciliacion.total_centralizadora,
                    diferencia=diferencia,
                    estado=conciliacion.estado,
                    observaciones=conciliacion.observaciones
                )
            else:
                # Crear nueva entrada con totales calculados
                nueva_conciliacion = ConciliacionContable(
                    fecha=fecha,
                    empresa_id=empresa.id,
                    total_pagaduria=totales["pagaduria"],
                    total_tesoreria=totales["tesoreria"],
                    total_centralizadora=Decimal('0.00'),  # Inicializar en 0.00 en lugar de None
                    estado="Pendiente"
                )
                
                db.add(nueva_conciliacion)
                db.commit()
                db.refresh(nueva_conciliacion)
                
                total_calculado = totales["pagaduria"] + totales["tesoreria"]
                diferencia_calculada = total_calculado - (nueva_conciliacion.total_centralizadora or Decimal('0.00'))
                
                empresa_data = EmpresaConciliacionResponse(
                    id=nueva_conciliacion.id,
                    compania_id=empresa.id,
                    compania=CompaniaResponse(id=empresa.id, nombre=empresa.nombre),
                    total_pagaduria=totales["pagaduria"],
                    total_tesoreria=totales["tesoreria"],
                    total_calculado=total_calculado,
                    total_centralizadora=nueva_conciliacion.total_centralizadora,
                    diferencia=diferencia_calculada,
                    estado="pendiente",
                    observaciones=None
                )
            
            empresas_conciliacion.append(empresa_data)
        
        return ConciliacionFechaResponse(
            fecha=fecha,
            empresas=empresas_conciliacion
        )
    
    @staticmethod
    def actualizar_total_centralizadora(
        db: Session, 
        empresa_id: int, 
        fecha: date, 
        total_centralizadora: Decimal,
        observaciones: Optional[str] = None
    ) -> ConciliacionContable:
        """
        Actualiza el total centralizadora de una conciliación
        """
        conciliacion = db.query(ConciliacionContable).filter(
            and_(
                ConciliacionContable.empresa_id == empresa_id,
                ConciliacionContable.fecha == fecha
            )
        ).first()
        
        if not conciliacion:
            # Recalcular totales
            totales = ConciliacionContableService.calcular_totales_por_area(
                db, empresa_id, fecha
            )
            
            # Crear nueva conciliación
            conciliacion = ConciliacionContable(
                fecha=fecha,
                empresa_id=empresa_id,
                total_pagaduria=totales["pagaduria"],
                total_tesoreria=totales["tesoreria"],
                total_centralizadora=total_centralizadora,
                estado="Evaluado",  # Automático: pasa a Evaluado al ingresar centralizadora
                observaciones=observaciones
            )
            db.add(conciliacion)
        else:
            # Actualizar existente
            conciliacion.total_centralizadora = total_centralizadora
            
            # Solo cambiar a Evaluado si está en Pendiente
            # No retroceder si ya está Confirmado o Cerrado
            if conciliacion.estado == "Pendiente":
                conciliacion.estado = "Evaluado"
            
            if observaciones:
                conciliacion.observaciones = observaciones
        
        # Calcular diferencia
        conciliacion.diferencia = conciliacion.diferencia_calculada
        
        db.commit()
        db.refresh(conciliacion)
        
        return conciliacion
    
    @staticmethod
    def evaluar_conciliacion(
        db: Session, 
        empresa_id: int, 
        fecha: date
    ) -> ConciliacionContable:
        """
        Evalúa una conciliación (cambia estado a Evaluado)
        """
        conciliacion = db.query(ConciliacionContable).filter(
            and_(
                ConciliacionContable.empresa_id == empresa_id,
                ConciliacionContable.fecha == fecha
            )
        ).first()
        
        if not conciliacion:
            raise ValueError("No existe conciliación para evaluar")
        
        # Permitir cambio desde cualquier estado
        conciliacion.estado = "Evaluado"
        db.commit()
        db.refresh(conciliacion)
        
        return conciliacion
    
    @staticmethod
    def confirmar_conciliacion(
        db: Session, 
        empresa_id: int, 
        fecha: date
    ) -> ConciliacionContable:
        """
        Confirma una conciliación (cambia estado a Confirmado)
        """
        conciliacion = db.query(ConciliacionContable).filter(
            and_(
                ConciliacionContable.empresa_id == empresa_id,
                ConciliacionContable.fecha == fecha
            )
        ).first()
        
        if not conciliacion:
            raise ValueError("No existe conciliación para confirmar")
        
        # Permitir cambio desde cualquier estado
        conciliacion.estado = "Confirmado"
        db.commit()
        db.refresh(conciliacion)
        
        return conciliacion
    
    @staticmethod
    def cerrar_conciliacion(
        db: Session, 
        empresa_id: int, 
        fecha: date
    ) -> ConciliacionContable:
        """
        Cierra una conciliación (cambia estado a Cerrado)
        """
        conciliacion = db.query(ConciliacionContable).filter(
            and_(
                ConciliacionContable.empresa_id == empresa_id,
                ConciliacionContable.fecha == fecha
            )
        ).first()
        
        if not conciliacion:
            raise ValueError("No existe conciliación para cerrar")
        
        # Permitir cambio desde cualquier estado
        conciliacion.estado = "Cerrado"
        db.commit()
        db.refresh(conciliacion)
        
        return conciliacion
    
    @staticmethod
    def evaluar_todas_conciliaciones(db: Session, fecha: date) -> List[ConciliacionContable]:
        """
        Evalúa todas las conciliaciones de una fecha (cambia estado a Evaluado)
        """
        conciliaciones = db.query(ConciliacionContable).filter(
            ConciliacionContable.fecha == fecha
        ).all()
        
        for conciliacion in conciliaciones:
            if conciliacion.total_centralizadora is not None:
                conciliacion.estado = "Evaluado"
        
        db.commit()
        
        return conciliaciones