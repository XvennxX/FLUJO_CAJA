"""
API endpoints para manejo de DIFERENCIA SALDOS
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, Any

from ..core.database import get_db
from ..services.diferencia_saldos_service import DiferenciaSaldosService
from ..services.auth_service import get_current_user
from ..models.usuarios import Usuario

router = APIRouter(prefix="/diferencia-saldos", tags=["diferencia-saldos"])

@router.post("/calcular-diferencia-saldos")
async def calcular_diferencia_saldos(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Calcular y guardar DIFERENCIA SALDOS automáticamente para todas las cuentas en una fecha
    """
    try:
        resultado = DiferenciaSaldosService.procesar_diferencias_saldos_para_fecha(
            db=db,
            fecha=fecha,
            usuario_id=current_user.id
        )
        
        if "error" in resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando diferencias saldos: {resultado['error']}"
            )
        
        return {
            "message": "Diferencias saldos procesadas exitosamente",
            "fecha": fecha.isoformat(),
            "resultado": resultado
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando diferencias saldos: {str(e)}"
        )

@router.get("/verificar-necesidad/{fecha}")
async def verificar_necesidad_calculo(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verificar si es necesario calcular diferencias saldos para una fecha
    """
    try:
        # Buscar el concepto DIFERENCIA SALDOS
        concepto_diferencia = DiferenciaSaldosService.obtener_concepto_por_nombre(
            db, "DIFERENCIA SALDOS"
        )
        
        if not concepto_diferencia:
            return {
                "necesita_calculo": False,
                "razon": "Concepto DIFERENCIA SALDOS no encontrado"
            }
        
        # Contar transacciones existentes para esta fecha
        from ..models.transacciones_flujo_caja import TransaccionFlujoCaja
        transacciones_existentes = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == concepto_diferencia.id,
            TransaccionFlujoCaja.fecha == fecha
        ).count()
        
        # Contar total de cuentas
        from ..models.cuentas_bancarias import CuentaBancaria
        total_cuentas = db.query(CuentaBancaria).count()
        
        necesita_calculo = transacciones_existentes < total_cuentas
        
        return {
            "necesita_calculo": necesita_calculo,
            "transacciones_existentes": transacciones_existentes,
            "total_cuentas": total_cuentas,
            "fecha": fecha.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando necesidad de cálculo: {str(e)}"
        )
