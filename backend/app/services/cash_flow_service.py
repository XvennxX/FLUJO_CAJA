from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, status

from app.models.ingreso import Ingreso
from app.models.egreso import Egreso
from app.models.concepto import Concepto
from app.models.cuenta import Cuenta

class CashFlowService:
    """Servicio para cálculos y análisis de flujo de caja"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_flujo_diario(
        self,
        fecha: date,
        id_cuenta: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcula el flujo de caja de un día específico
        
        Args:
            fecha: Fecha para calcular el flujo
            id_cuenta: ID de cuenta específica (opcional)
            
        Returns:
            Dict con información del flujo diario
        """
        try:
            # Filtros base para ingresos
            filtros_ingresos = [Ingreso.fecha == fecha]
            filtros_egresos = [Egreso.fecha == fecha]
            
            if id_cuenta:
                filtros_ingresos.append(Ingreso.id_cuenta == id_cuenta)
                filtros_egresos.append(Egreso.id_cuenta == id_cuenta)
            
            # Calcular total de ingresos
            total_ingresos = self.db.query(func.sum(Ingreso.valor))\
                .filter(and_(*filtros_ingresos))\
                .scalar() or Decimal('0.00')
            
            # Calcular total de egresos
            total_egresos = self.db.query(func.sum(Egreso.valor))\
                .filter(and_(*filtros_egresos))\
                .scalar() or Decimal('0.00')
            
            # Flujo neto
            flujo_neto = total_ingresos - total_egresos
            
            # Detalles por concepto
            ingresos_por_concepto = self.db.query(
                Concepto.nombre,
                func.sum(Ingreso.valor).label('total')
            ).join(Ingreso)\
             .filter(and_(*filtros_ingresos))\
             .group_by(Concepto.id_concepto)\
             .all()
            
            egresos_por_concepto = self.db.query(
                Concepto.nombre,
                func.sum(Egreso.valor).label('total')
            ).join(Egreso)\
             .filter(and_(*filtros_egresos))\
             .group_by(Concepto.id_concepto)\
             .all()
            
            return {
                "fecha": fecha,
                "id_cuenta": id_cuenta,
                "resumen": {
                    "total_ingresos": float(total_ingresos),
                    "total_egresos": float(total_egresos),
                    "flujo_neto": float(flujo_neto)
                },
                "ingresos_por_concepto": [
                    {"concepto": nombre, "total": float(total)}
                    for nombre, total in ingresos_por_concepto
                ],
                "egresos_por_concepto": [
                    {"concepto": nombre, "total": float(total)}
                    for nombre, total in egresos_por_concepto
                ]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular flujo diario: {str(e)}"
            )
    
    def calcular_flujo_periodo(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        id_cuenta: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcula el flujo de caja en un período determinado
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            id_cuenta: ID de cuenta específica (opcional)
            
        Returns:
            Dict con información del flujo del período
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
            
            # Totales del período
            total_ingresos = self.db.query(func.sum(Ingreso.valor))\
                .filter(and_(*filtros_ingresos))\
                .scalar() or Decimal('0.00')
            
            total_egresos = self.db.query(func.sum(Egreso.valor))\
                .filter(and_(*filtros_egresos))\
                .scalar() or Decimal('0.00')
            
            flujo_neto = total_ingresos - total_egresos
            
            # Flujo diario en el período
            flujo_diario = []
            fecha_actual = fecha_inicio
            
            while fecha_actual <= fecha_fin:
                flujo_dia = self.calcular_flujo_diario(fecha_actual, id_cuenta)
                flujo_diario.append({
                    "fecha": fecha_actual,
                    "ingresos": flujo_dia["resumen"]["total_ingresos"],
                    "egresos": flujo_dia["resumen"]["total_egresos"],
                    "flujo_neto": flujo_dia["resumen"]["flujo_neto"]
                })
                fecha_actual += timedelta(days=1)
            
            return {
                "periodo": {
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin
                },
                "id_cuenta": id_cuenta,
                "resumen": {
                    "total_ingresos": float(total_ingresos),
                    "total_egresos": float(total_egresos),
                    "flujo_neto": float(flujo_neto),
                    "dias": len(flujo_diario)
                },
                "flujo_diario": flujo_diario
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular flujo del período: {str(e)}"
            )
    
    def obtener_saldos_cuentas(self) -> List[Dict[str, Any]]:
        """
        Obtiene los saldos actuales de todas las cuentas
        
        Returns:
            Lista con información de saldos por cuenta
        """
        try:
            cuentas = self.db.query(Cuenta).filter(
                Cuenta.estado == True
            ).all()
            
            saldos = []
            total_general = Decimal('0.00')
            
            for cuenta in cuentas:
                saldos.append({
                    "id_cuenta": cuenta.id_cuenta,
                    "nombre": cuenta.nombre,
                    "saldo": float(cuenta.saldo_actual)
                })
                total_general += cuenta.saldo_actual
            
            return {
                "cuentas": saldos,
                "total_general": float(total_general),
                "fecha_consulta": datetime.now()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener saldos: {str(e)}"
            )
    
    def proyectar_flujo_futuro(
        self,
        dias_proyeccion: int = 30,
        id_cuenta: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Proyecta el flujo de caja futuro basado en promedios históricos
        
        Args:
            dias_proyeccion: Número de días a proyectar
            id_cuenta: ID de cuenta específica (opcional)
            
        Returns:
            Lista con proyecciones diarias
        """
        try:
            # Calcular promedios de los últimos 30 días
            fecha_fin = date.today()
            fecha_inicio = fecha_fin - timedelta(days=30)
            
            flujo_historico = self.calcular_flujo_periodo(
                fecha_inicio, fecha_fin, id_cuenta
            )
            
            promedio_ingresos_diario = flujo_historico["resumen"]["total_ingresos"] / 30
            promedio_egresos_diario = flujo_historico["resumen"]["total_egresos"] / 30
            
            # Generar proyecciones
            proyecciones = []
            saldo_proyectado = 0
            
            # Obtener saldo actual si es para una cuenta específica
            if id_cuenta:
                cuenta = self.db.query(Cuenta).filter(
                    Cuenta.id_cuenta == id_cuenta
                ).first()
                if cuenta:
                    saldo_proyectado = float(cuenta.saldo_actual)
            else:
                saldos_info = self.obtener_saldos_cuentas()
                saldo_proyectado = saldos_info["total_general"]
            
            for i in range(1, dias_proyeccion + 1):
                fecha_proyeccion = fecha_fin + timedelta(days=i)
                flujo_neto_dia = promedio_ingresos_diario - promedio_egresos_diario
                saldo_proyectado += flujo_neto_dia
                
                proyecciones.append({
                    "fecha": fecha_proyeccion,
                    "ingresos_proyectados": promedio_ingresos_diario,
                    "egresos_proyectados": promedio_egresos_diario,
                    "flujo_neto_proyectado": flujo_neto_dia,
                    "saldo_proyectado": saldo_proyectado
                })
            
            return {
                "base_calculo": {
                    "periodo_historico": f"{fecha_inicio} - {fecha_fin}",
                    "promedio_ingresos_diario": promedio_ingresos_diario,
                    "promedio_egresos_diario": promedio_egresos_diario
                },
                "proyecciones": proyecciones
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al proyectar flujo: {str(e)}"
            )
    
    def analizar_tendencias(
        self,
        dias_analisis: int = 90,
        id_cuenta: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analiza las tendencias del flujo de caja
        
        Args:
            dias_analisis: Número de días hacia atrás para analizar
            id_cuenta: ID de cuenta específica (opcional)
            
        Returns:
            Dict con análisis de tendencias
        """
        try:
            fecha_fin = date.today()
            fecha_inicio = fecha_fin - timedelta(days=dias_analisis)
            
            # Obtener flujo por semanas
            tendencias_semanales = []
            fecha_semana = fecha_inicio
            
            while fecha_semana <= fecha_fin:
                fin_semana = min(fecha_semana + timedelta(days=6), fecha_fin)
                
                flujo_semana = self.calcular_flujo_periodo(
                    fecha_semana, fin_semana, id_cuenta
                )
                
                tendencias_semanales.append({
                    "semana": f"{fecha_semana} - {fin_semana}",
                    "ingresos": flujo_semana["resumen"]["total_ingresos"],
                    "egresos": flujo_semana["resumen"]["total_egresos"],
                    "flujo_neto": flujo_semana["resumen"]["flujo_neto"]
                })
                
                fecha_semana = fin_semana + timedelta(days=1)
            
            # Calcular tendencias
            if len(tendencias_semanales) >= 2:
                primera_semana = tendencias_semanales[0]
                ultima_semana = tendencias_semanales[-1]
                
                tendencia_ingresos = "creciente" if ultima_semana["ingresos"] > primera_semana["ingresos"] else "decreciente"
                tendencia_egresos = "creciente" if ultima_semana["egresos"] > primera_semana["egresos"] else "decreciente"
                
                return {
                    "periodo_analisis": f"{fecha_inicio} - {fecha_fin}",
                    "tendencias_semanales": tendencias_semanales,
                    "analisis": {
                        "tendencia_ingresos": tendencia_ingresos,
                        "tendencia_egresos": tendencia_egresos,
                        "promedio_semanal_ingresos": sum(s["ingresos"] for s in tendencias_semanales) / len(tendencias_semanales),
                        "promedio_semanal_egresos": sum(s["egresos"] for s in tendencias_semanales) / len(tendencias_semanales)
                    }
                }
            
            return {
                "periodo_analisis": f"{fecha_inicio} - {fecha_fin}",
                "mensaje": "Datos insuficientes para análisis de tendencias"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al analizar tendencias: {str(e)}"
            )
