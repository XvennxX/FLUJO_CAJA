from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status

from app.models.ingreso import Ingreso
from app.models.egreso import Egreso
from app.models.concepto import Concepto
from app.models.cuenta import Cuenta
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario
from app.services.audit_service import AuditService

class ReportService:
    """Servicio para generación de reportes del sistema"""
    
    def __init__(self, db: Session, audit_service: AuditService):
        self.db = db
        self.audit_service = audit_service
    
    def reporte_ingresos_egresos(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        id_cuenta: Optional[int] = None,
        id_concepto: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte detallado de ingresos y egresos
        
        Args:
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte
            id_cuenta: Filtro por cuenta específica (opcional)
            id_concepto: Filtro por concepto específico (opcional)
            
        Returns:
            Dict con reporte completo de ingresos y egresos
        """
        try:
            # Filtros base
            filtros_ingresos = [
                Ingreso.fecha >= fecha_inicio,
                Ingreso.fecha <= fecha_fin
            ]
            filtros_egresos = [
                Egreso.fecha >= fecha_inicio,
                Egreso.fecha <= fecha_fin
            ]
            
            if id_cuenta:
                filtros_ingresos.append(Ingreso.id_cuenta == id_cuenta)
                filtros_egresos.append(Egreso.id_cuenta == id_cuenta)
                
            if id_concepto:
                filtros_ingresos.append(Ingreso.id_concepto == id_concepto)
                filtros_egresos.append(Egreso.id_concepto == id_concepto)
            
            # Consultar ingresos detallados
            ingresos = self.db.query(
                Ingreso.id_ingreso,
                Ingreso.valor,
                Ingreso.fecha,
                Concepto.nombre.label('concepto'),
                Cuenta.nombre.label('cuenta')
            ).join(Concepto, Ingreso.id_concepto == Concepto.id_concepto)\
             .join(Cuenta, Ingreso.id_cuenta == Cuenta.id_cuenta)\
             .filter(and_(*filtros_ingresos))\
             .order_by(desc(Ingreso.fecha))\
             .all()
            
            # Consultar egresos detallados
            egresos = self.db.query(
                Egreso.id_egreso,
                Egreso.valor,
                Egreso.fecha,
                Concepto.nombre.label('concepto'),
                Cuenta.nombre.label('cuenta')
            ).join(Concepto, Egreso.id_concepto == Concepto.id_concepto)\
             .join(Cuenta, Egreso.id_cuenta == Cuenta.id_cuenta)\
             .filter(and_(*filtros_egresos))\
             .order_by(desc(Egreso.fecha))\
             .all()
            
            # Calcular totales
            total_ingresos = sum(float(ingreso.valor) for ingreso in ingresos)
            total_egresos = sum(float(egreso.valor) for egreso in egresos)
            balance_neto = total_ingresos - total_egresos
            
            # Agrupar por concepto
            ingresos_por_concepto = {}
            egresos_por_concepto = {}
            
            for ingreso in ingresos:
                concepto = ingreso.concepto
                if concepto not in ingresos_por_concepto:
                    ingresos_por_concepto[concepto] = 0
                ingresos_por_concepto[concepto] += float(ingreso.valor)
            
            for egreso in egresos:
                concepto = egreso.concepto
                if concepto not in egresos_por_concepto:
                    egresos_por_concepto[concepto] = 0
                egresos_por_concepto[concepto] += float(egreso.valor)
            
            return {
                "periodo": {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin
                },
                "filtros": {
                    "id_cuenta": id_cuenta,
                    "id_concepto": id_concepto
                },
                "resumen": {
                    "total_ingresos": total_ingresos,
                    "total_egresos": total_egresos,
                    "balance_neto": balance_neto,
                    "cantidad_ingresos": len(ingresos),
                    "cantidad_egresos": len(egresos)
                },
                "ingresos_por_concepto": [
                    {"concepto": concepto, "total": total}
                    for concepto, total in ingresos_por_concepto.items()
                ],
                "egresos_por_concepto": [
                    {"concepto": concepto, "total": total}
                    for concepto, total in egresos_por_concepto.items()
                ],
                "detalle_ingresos": [
                    {
                        "id": ingreso.id_ingreso,
                        "fecha": ingreso.fecha,
                        "valor": float(ingreso.valor),
                        "concepto": ingreso.concepto,
                        "cuenta": ingreso.cuenta
                    }
                    for ingreso in ingresos
                ],
                "detalle_egresos": [
                    {
                        "id": egreso.id_egreso,
                        "fecha": egreso.fecha,
                        "valor": float(egreso.valor),
                        "concepto": egreso.concepto,
                        "cuenta": egreso.cuenta
                    }
                    for egreso in egresos
                ]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar reporte de ingresos y egresos: {str(e)}"
            )
    
    def reporte_cuentas(self) -> Dict[str, Any]:
        """
        Genera reporte de estado de todas las cuentas
        
        Returns:
            Dict con información detallada de todas las cuentas
        """
        try:
            cuentas = self.db.query(Cuenta).all()
            
            reporte_cuentas = []
            total_saldo = Decimal('0.00')
            cuentas_activas = 0
            
            for cuenta in cuentas:
                # Contar transacciones por cuenta
                total_ingresos_cuenta = self.db.query(func.count(Ingreso.id_ingreso))\
                    .filter(Ingreso.id_cuenta == cuenta.id_cuenta)\
                    .scalar() or 0
                
                total_egresos_cuenta = self.db.query(func.count(Egreso.id_egreso))\
                    .filter(Egreso.id_cuenta == cuenta.id_cuenta)\
                    .scalar() or 0
                
                if cuenta.estado:
                    total_saldo += cuenta.saldo_actual
                    cuentas_activas += 1
                
                reporte_cuentas.append({
                    "id_cuenta": cuenta.id_cuenta,
                    "nombre": cuenta.nombre,
                    "saldo_actual": float(cuenta.saldo_actual),
                    "estado": cuenta.estado,
                    "total_ingresos": total_ingresos_cuenta,
                    "total_egresos": total_egresos_cuenta,
                    "total_transacciones": total_ingresos_cuenta + total_egresos_cuenta
                })
            
            return {
                "fecha_reporte": datetime.now(),
                "resumen": {
                    "total_cuentas": len(cuentas),
                    "cuentas_activas": cuentas_activas,
                    "cuentas_inactivas": len(cuentas) - cuentas_activas,
                    "saldo_total": float(total_saldo)
                },
                "detalle_cuentas": reporte_cuentas
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar reporte de cuentas: {str(e)}"
            )
    
    def reporte_conceptos(self, incluir_inactivos: bool = False) -> Dict[str, Any]:
        """
        Genera reporte de uso de conceptos
        
        Args:
            incluir_inactivos: Incluir conceptos inactivos en el reporte
            
        Returns:
            Dict con información de uso de conceptos
        """
        try:
            filtros = []
            if not incluir_inactivos:
                filtros.append(Concepto.estado == True)
            
            conceptos = self.db.query(Concepto).filter(and_(*filtros)).all()
            
            reporte_conceptos = []
            total_usos = 0
            
            for concepto in conceptos:
                # Contar usos del concepto
                usos_ingresos = self.db.query(func.count(Ingreso.id_ingreso))\
                    .filter(Ingreso.id_concepto == concepto.id_concepto)\
                    .scalar() or 0
                
                usos_egresos = self.db.query(func.count(Egreso.id_egreso))\
                    .filter(Egreso.id_concepto == concepto.id_concepto)\
                    .scalar() or 0
                
                total_usos_concepto = usos_ingresos + usos_egresos
                total_usos += total_usos_concepto
                
                # Calcular montos totales
                monto_ingresos = self.db.query(func.sum(Ingreso.valor))\
                    .filter(Ingreso.id_concepto == concepto.id_concepto)\
                    .scalar() or Decimal('0.00')
                
                monto_egresos = self.db.query(func.sum(Egreso.valor))\
                    .filter(Egreso.id_concepto == concepto.id_concepto)\
                    .scalar() or Decimal('0.00')
                
                reporte_conceptos.append({
                    "id_concepto": concepto.id_concepto,
                    "nombre": concepto.nombre,
                    "tipo": concepto.tipo,
                    "estado": concepto.estado,
                    "usos_ingresos": usos_ingresos,
                    "usos_egresos": usos_egresos,
                    "total_usos": total_usos_concepto,
                    "monto_ingresos": float(monto_ingresos),
                    "monto_egresos": float(monto_egresos),
                    "monto_total": float(monto_ingresos + monto_egresos)
                })
            
            # Ordenar por total de usos
            reporte_conceptos.sort(key=lambda x: x["total_usos"], reverse=True)
            
            return {
                "fecha_reporte": datetime.now(),
                "incluir_inactivos": incluir_inactivos,
                "resumen": {
                    "total_conceptos": len(conceptos),
                    "conceptos_activos": len([c for c in conceptos if c.estado]),
                    "conceptos_inactivos": len([c for c in conceptos if not c.estado]),
                    "total_usos": total_usos
                },
                "detalle_conceptos": reporte_conceptos
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar reporte de conceptos: {str(e)}"
            )
    
    def reporte_auditoria(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        id_usuario: Optional[int] = None,
        accion: Optional[str] = None,
        limite: int = 100
    ) -> Dict[str, Any]:
        """
        Genera reporte de auditoría del sistema
        
        Args:
            fecha_inicio: Fecha de inicio del reporte (opcional)
            fecha_fin: Fecha de fin del reporte (opcional)
            id_usuario: Filtro por usuario específico (opcional)
            accion: Filtro por tipo de acción (opcional)
            limite: Número máximo de registros a retornar
            
        Returns:
            Dict con reporte de auditoría
        """
        try:
            filtros = []
            
            if fecha_inicio:
                filtros.append(Auditoria.fecha_accion >= fecha_inicio)
            if fecha_fin:
                filtros.append(Auditoria.fecha_accion <= fecha_fin)
            if id_usuario:
                filtros.append(Auditoria.id_usuario == id_usuario)
            if accion:
                filtros.append(Auditoria.accion.contains(accion))
            
            # Consultar registros de auditoría
            auditoria_query = self.db.query(
                Auditoria.id_auditoria,
                Auditoria.fecha_accion,
                Auditoria.accion,
                Auditoria.detalles,
                Usuario.nombre.label('usuario_nombre')
            ).join(Usuario, Auditoria.id_usuario == Usuario.id_usuario)\
             .filter(and_(*filtros))\
             .order_by(desc(Auditoria.fecha_accion))\
             .limit(limite)
            
            registros = auditoria_query.all()
            
            # Estadísticas por acción
            estadisticas_acciones = self.db.query(
                Auditoria.accion,
                func.count(Auditoria.id_auditoria).label('cantidad')
            ).filter(and_(*filtros))\
             .group_by(Auditoria.accion)\
             .all()
            
            # Estadísticas por usuario
            estadisticas_usuarios = self.db.query(
                Usuario.nombre,
                func.count(Auditoria.id_auditoria).label('cantidad')
            ).join(Usuario, Auditoria.id_usuario == Usuario.id_usuario)\
             .filter(and_(*filtros))\
             .group_by(Usuario.id_usuario)\
             .all()
            
            return {
                "fecha_reporte": datetime.now(),
                "filtros": {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "id_usuario": id_usuario,
                    "accion": accion,
                    "limite": limite
                },
                "resumen": {
                    "total_registros": len(registros),
                    "registros_mostrados": min(len(registros), limite)
                },
                "estadisticas_acciones": [
                    {"accion": accion, "cantidad": cantidad}
                    for accion, cantidad in estadisticas_acciones
                ],
                "estadisticas_usuarios": [
                    {"usuario": nombre, "cantidad": cantidad}
                    for nombre, cantidad in estadisticas_usuarios
                ],
                "detalle_registros": [
                    {
                        "id": registro.id_auditoria,
                        "fecha": registro.fecha_accion,
                        "usuario": registro.usuario_nombre,
                        "accion": registro.accion,
                        "detalles": registro.detalles
                    }
                    for registro in registros
                ]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar reporte de auditoría: {str(e)}"
            )
    
    def dashboard_resumen(self) -> Dict[str, Any]:
        """
        Genera datos para dashboard principal
        
        Returns:
            Dict con métricas principales del sistema
        """
        try:
            # Fecha actual y períodos
            hoy = date.today()
            inicio_mes = hoy.replace(day=1)
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            
            # Métricas del día
            ingresos_hoy = self.db.query(func.sum(Ingreso.valor))\
                .filter(Ingreso.fecha == hoy)\
                .scalar() or Decimal('0.00')
            
            egresos_hoy = self.db.query(func.sum(Egreso.valor))\
                .filter(Egreso.fecha == hoy)\
                .scalar() or Decimal('0.00')
            
            # Métricas de la semana
            ingresos_semana = self.db.query(func.sum(Ingreso.valor))\
                .filter(Ingreso.fecha >= inicio_semana)\
                .scalar() or Decimal('0.00')
            
            egresos_semana = self.db.query(func.sum(Egreso.valor))\
                .filter(Egreso.fecha >= inicio_semana)\
                .scalar() or Decimal('0.00')
            
            # Métricas del mes
            ingresos_mes = self.db.query(func.sum(Ingreso.valor))\
                .filter(Ingreso.fecha >= inicio_mes)\
                .scalar() or Decimal('0.00')
            
            egresos_mes = self.db.query(func.sum(Egreso.valor))\
                .filter(Egreso.fecha >= inicio_mes)\
                .scalar() or Decimal('0.00')
            
            # Saldo total de cuentas
            saldo_total = self.db.query(func.sum(Cuenta.saldo_actual))\
                .filter(Cuenta.estado == True)\
                .scalar() or Decimal('0.00')
            
            # Transacciones recientes (últimas 5)
            transacciones_recientes = []
            
            # Últimos ingresos
            ultimos_ingresos = self.db.query(
                Ingreso.id_ingreso,
                Ingreso.valor,
                Ingreso.fecha,
                Concepto.nombre.label('concepto'),
                Cuenta.nombre.label('cuenta')
            ).join(Concepto, Ingreso.id_concepto == Concepto.id_concepto)\
             .join(Cuenta, Ingreso.id_cuenta == Cuenta.id_cuenta)\
             .order_by(desc(Ingreso.fecha))\
             .limit(3)\
             .all()
            
            for ingreso in ultimos_ingresos:
                transacciones_recientes.append({
                    "tipo": "ingreso",
                    "id": ingreso.id_ingreso,
                    "fecha": ingreso.fecha,
                    "valor": float(ingreso.valor),
                    "concepto": ingreso.concepto,
                    "cuenta": ingreso.cuenta
                })
            
            # Últimos egresos
            ultimos_egresos = self.db.query(
                Egreso.id_egreso,
                Egreso.valor,
                Egreso.fecha,
                Concepto.nombre.label('concepto'),
                Cuenta.nombre.label('cuenta')
            ).join(Concepto, Egreso.id_concepto == Concepto.id_concepto)\
             .join(Cuenta, Egreso.id_cuenta == Cuenta.id_cuenta)\
             .order_by(desc(Egreso.fecha))\
             .limit(3)\
             .all()
            
            for egreso in ultimos_egresos:
                transacciones_recientes.append({
                    "tipo": "egreso",
                    "id": egreso.id_egreso,
                    "fecha": egreso.fecha,
                    "valor": float(egreso.valor),
                    "concepto": egreso.concepto,
                    "cuenta": egreso.cuenta
                })
            
            # Ordenar por fecha
            transacciones_recientes.sort(key=lambda x: x["fecha"], reverse=True)
            
            return {
                "fecha_consulta": datetime.now(),
                "metricas_diarias": {
                    "ingresos": float(ingresos_hoy),
                    "egresos": float(egresos_hoy),
                    "balance": float(ingresos_hoy - egresos_hoy)
                },
                "metricas_semanales": {
                    "ingresos": float(ingresos_semana),
                    "egresos": float(egresos_semana),
                    "balance": float(ingresos_semana - egresos_semana)
                },
                "metricas_mensuales": {
                    "ingresos": float(ingresos_mes),
                    "egresos": float(egresos_mes),
                    "balance": float(ingresos_mes - egresos_mes)
                },
                "saldo_total": float(saldo_total),
                "transacciones_recientes": transacciones_recientes[:5]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar dashboard: {str(e)}"
            )
