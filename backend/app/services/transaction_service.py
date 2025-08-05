from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ingreso import Ingreso
from app.models.egreso import Egreso
from app.models.concepto import Concepto, TipoConcepto
from app.models.cuenta import Cuenta
from app.services.audit_service import AuditService

class TransactionService:
    """Servicio para gestión de transacciones (ingresos y egresos)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def crear_ingreso(
        self,
        fecha: date,
        valor: Decimal,
        observaciones: str,
        id_concepto: int,
        id_cuenta: int,
        created_by: int
    ) -> Dict[str, Any]:
        """
        Crea un nuevo ingreso
        
        Args:
            fecha: Fecha del ingreso
            valor: Valor del ingreso
            observaciones: Observaciones del ingreso
            id_concepto: ID del concepto de ingreso
            id_cuenta: ID de la cuenta
            created_by: ID del usuario que crea el ingreso
            
        Returns:
            Dict con información del ingreso creado
        """
        try:
            # Validaciones
            if valor <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El valor debe ser mayor a cero"
                )
            
            # Verificar que el concepto existe y es de tipo INGRESO
            concepto = self.db.query(Concepto).filter(
                Concepto.id_concepto == id_concepto,
                Concepto.tipo == TipoConcepto.INGRESO
            ).first()
            
            if not concepto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Concepto de ingreso no válido"
                )
            
            # Verificar que la cuenta existe y está activa
            cuenta = self.db.query(Cuenta).filter(
                Cuenta.id_cuenta == id_cuenta,
                Cuenta.estado == True
            ).first()
            
            if not cuenta:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cuenta no válida o inactiva"
                )
            
            # Crear el ingreso
            nuevo_ingreso = Ingreso(
                fecha=fecha,
                valor=valor,
                observaciones=observaciones,
                id_concepto=id_concepto,
                id_cuenta=id_cuenta
            )
            
            self.db.add(nuevo_ingreso)
            self.db.flush()
            
            # Actualizar saldo de la cuenta
            cuenta.saldo_actual += valor
            
            # Registrar en auditoría
            self.audit_service.registrar_accion(
                id_usuario=created_by,
                accion=f"Creó ingreso por ${valor} - {concepto.nombre}",
                tabla_afectada="ingreso",
                id_registro_afectado=nuevo_ingreso.id_ingreso
            )
            
            self.db.commit()
            
            return {
                "id_ingreso": nuevo_ingreso.id_ingreso,
                "fecha": nuevo_ingreso.fecha,
                "valor": float(nuevo_ingreso.valor),
                "observaciones": nuevo_ingreso.observaciones,
                "concepto": concepto.nombre,
                "cuenta": cuenta.nombre,
                "nuevo_saldo_cuenta": float(cuenta.saldo_actual)
            }
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear ingreso: {str(e)}"
            )
    
    def crear_egreso(
        self,
        fecha: date,
        valor: Decimal,
        observaciones: str,
        id_concepto: int,
        id_cuenta: int,
        created_by: int
    ) -> Dict[str, Any]:
        """
        Crea un nuevo egreso
        
        Args:
            fecha: Fecha del egreso
            valor: Valor del egreso
            observaciones: Observaciones del egreso
            id_concepto: ID del concepto de egreso
            id_cuenta: ID de la cuenta
            created_by: ID del usuario que crea el egreso
            
        Returns:
            Dict con información del egreso creado
        """
        try:
            # Validaciones
            if valor <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El valor debe ser mayor a cero"
                )
            
            # Verificar que el concepto existe y es de tipo EGRESO
            concepto = self.db.query(Concepto).filter(
                Concepto.id_concepto == id_concepto,
                Concepto.tipo == TipoConcepto.EGRESO
            ).first()
            
            if not concepto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Concepto de egreso no válido"
                )
            
            # Verificar que la cuenta existe y está activa
            cuenta = self.db.query(Cuenta).filter(
                Cuenta.id_cuenta == id_cuenta,
                Cuenta.estado == True
            ).first()
            
            if not cuenta:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cuenta no válida o inactiva"
                )
            
            # Verificar saldo suficiente
            if cuenta.saldo_actual < valor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Saldo insuficiente en la cuenta"
                )
            
            # Crear el egreso
            nuevo_egreso = Egreso(
                fecha=fecha,
                valor=valor,
                observaciones=observaciones,
                id_concepto=id_concepto,
                id_cuenta=id_cuenta
            )
            
            self.db.add(nuevo_egreso)
            self.db.flush()
            
            # Actualizar saldo de la cuenta
            cuenta.saldo_actual -= valor
            
            # Registrar en auditoría
            self.audit_service.registrar_accion(
                id_usuario=created_by,
                accion=f"Creó egreso por ${valor} - {concepto.nombre}",
                tabla_afectada="egreso",
                id_registro_afectado=nuevo_egreso.id_egreso
            )
            
            self.db.commit()
            
            return {
                "id_egreso": nuevo_egreso.id_egreso,
                "fecha": nuevo_egreso.fecha,
                "valor": float(nuevo_egreso.valor),
                "observaciones": nuevo_egreso.observaciones,
                "concepto": concepto.nombre,
                "cuenta": cuenta.nombre,
                "nuevo_saldo_cuenta": float(cuenta.saldo_actual)
            }
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear egreso: {str(e)}"
            )
    
    def listar_ingresos(
        self,
        skip: int = 0,
        limit: int = 100,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        id_cuenta: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista los ingresos con filtros opcionales
        
        Args:
            skip: Registros a saltar
            limit: Máximo registros a devolver
            fecha_inicio: Filtro por fecha de inicio
            fecha_fin: Filtro por fecha de fin
            id_cuenta: Filtro por cuenta
            
        Returns:
            Lista de ingresos
        """
        try:
            query = self.db.query(Ingreso)
            
            if fecha_inicio:
                query = query.filter(Ingreso.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.filter(Ingreso.fecha <= fecha_fin)
            if id_cuenta:
                query = query.filter(Ingreso.id_cuenta == id_cuenta)
            
            ingresos = query.offset(skip).limit(limit).all()
            
            return [
                {
                    "id_ingreso": ingreso.id_ingreso,
                    "fecha": ingreso.fecha,
                    "valor": float(ingreso.valor),
                    "observaciones": ingreso.observaciones,
                    "concepto": ingreso.concepto.nombre if ingreso.concepto else None,
                    "cuenta": ingreso.cuenta.nombre if ingreso.cuenta else None
                }
                for ingreso in ingresos
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al listar ingresos: {str(e)}"
            )
    
    def listar_egresos(
        self,
        skip: int = 0,
        limit: int = 100,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        id_cuenta: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista los egresos con filtros opcionales
        
        Args:
            skip: Registros a saltar
            limit: Máximo registros a devolver
            fecha_inicio: Filtro por fecha de inicio
            fecha_fin: Filtro por fecha de fin
            id_cuenta: Filtro por cuenta
            
        Returns:
            Lista de egresos
        """
        try:
            query = self.db.query(Egreso)
            
            if fecha_inicio:
                query = query.filter(Egreso.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.filter(Egreso.fecha <= fecha_fin)
            if id_cuenta:
                query = query.filter(Egreso.id_cuenta == id_cuenta)
            
            egresos = query.offset(skip).limit(limit).all()
            
            return [
                {
                    "id_egreso": egreso.id_egreso,
                    "fecha": egreso.fecha,
                    "valor": float(egreso.valor),
                    "observaciones": egreso.observaciones,
                    "concepto": egreso.concepto.nombre if egreso.concepto else None,
                    "cuenta": egreso.cuenta.nombre if egreso.cuenta else None
                }
                for egreso in egresos
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al listar egresos: {str(e)}"
            )
    
    def obtener_ingreso_por_id(self, ingreso_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un ingreso por su ID
        
        Args:
            ingreso_id: ID del ingreso
            
        Returns:
            Dict con información del ingreso o None si no existe
        """
        try:
            ingreso = self.db.query(Ingreso).filter(
                Ingreso.id_ingreso == ingreso_id
            ).first()
            
            if not ingreso:
                return None
            
            return {
                "id_ingreso": ingreso.id_ingreso,
                "fecha": ingreso.fecha,
                "valor": float(ingreso.valor),
                "observaciones": ingreso.observaciones,
                "concepto": ingreso.concepto.nombre if ingreso.concepto else None,
                "cuenta": ingreso.cuenta.nombre if ingreso.cuenta else None
            }
            
        except Exception:
            return None
    
    def obtener_egreso_por_id(self, egreso_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un egreso por su ID
        
        Args:
            egreso_id: ID del egreso
            
        Returns:
            Dict con información del egreso o None si no existe
        """
        try:
            egreso = self.db.query(Egreso).filter(
                Egreso.id_egreso == egreso_id
            ).first()
            
            if not egreso:
                return None
            
            return {
                "id_egreso": egreso.id_egreso,
                "fecha": egreso.fecha,
                "valor": float(egreso.valor),
                "observaciones": egreso.observaciones,
                "concepto": egreso.concepto.nombre if egreso.concepto else None,
                "cuenta": egreso.cuenta.nombre if egreso.cuenta else None
            }
            
        except Exception:
            return None
