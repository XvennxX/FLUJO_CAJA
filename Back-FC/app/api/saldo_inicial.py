"""
API para manejar SALDOS INICIALES automáticos
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.saldo_inicial_service import SaldoInicialService
from app.schemas.flujo_caja import TransaccionFlujoCajaResponse
from pydantic import BaseModel

router = APIRouter()


class SaldoInicialRequest(BaseModel):
    fecha: str  # YYYY-MM-DD
    cuenta_id: Optional[int] = None
    compania_id: Optional[int] = None


class SaldoInicialResponse(BaseModel):
    success: bool
    message: str
    transacciones_creadas: int
    transacciones: List[TransaccionFlujoCajaResponse]


@router.post("/calcular-saldo-inicial", response_model=SaldoInicialResponse)
async def calcular_saldo_inicial(
    request: SaldoInicialRequest,
    db: Session = Depends(get_db)
):
    """
    Calcula y guarda automáticamente el SALDO INICIAL para una fecha específica
    basado en el SALDO FINAL del día anterior
    """
    try:
        # Convertir fecha string a datetime
        fecha_obj = datetime.strptime(request.fecha, '%Y-%m-%d')
        
        if request.cuenta_id:
            # Procesar una cuenta específica
            from app.models.cuentas_bancarias import CuentaBancaria
            cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == request.cuenta_id).first()
            
            if not cuenta:
                raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
            
            transaccion = SaldoInicialService.crear_o_actualizar_saldo_inicial(
                fecha_obj, cuenta.id, cuenta.compania_id, db
            )
            
            transacciones = [transaccion] if transaccion else []
            
        else:
            # Procesar todas las cuentas
            transacciones = SaldoInicialService.procesar_saldos_iniciales_para_fecha(
                fecha_obj, request.compania_id, db
            )
        
        # Convertir a formato de respuesta
        transacciones_response = []
        for t in transacciones:
            if t:
                transacciones_response.append(TransaccionFlujoCajaResponse(
                    id=t.id,
                    concepto_id=t.concepto_id,
                    cuenta_id=t.cuenta_id,
                    compania_id=t.compania_id,
                    fecha=t.fecha,
                    monto=t.monto,
                    fecha_creacion=t.fecha_creacion,
                    fecha_actualizacion=t.fecha_actualizacion
                ))
        
        return SaldoInicialResponse(
            success=True,
            message=f"SALDOS INICIALES procesados correctamente para {request.fecha}",
            transacciones_creadas=len(transacciones_response),
            transacciones=transacciones_response
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando SALDOS INICIALES: {str(e)}")


@router.get("/saldo-final-dia-anterior")
async def obtener_saldo_final_dia_anterior(
    fecha: str = Query(..., description="Fecha actual en formato YYYY-MM-DD"),
    cuenta_id: Optional[int] = Query(None, description="ID de cuenta específica"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el SALDO FINAL del día anterior para una fecha específica
    (para preview antes de crear el SALDO INICIAL)
    """
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        
        saldo_final = SaldoInicialService.calcular_saldo_final_dia_anterior(
            fecha_obj, cuenta_id, db
        )
        
        return {
            "success": True,
            "fecha_anterior": (fecha_obj - timedelta(days=1)).strftime('%Y-%m-%d'),
            "fecha_actual": fecha,
            "saldo_final_dia_anterior": saldo_final,
            "cuenta_id": cuenta_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando saldo: {str(e)}")


@router.get("/verificar-necesidad/{fecha}")
async def verificar_necesidad_saldos_iniciales(
    fecha: str,
    compania_id: Optional[int] = Query(None, description="ID de compañía específica"),
    db: Session = Depends(get_db)
):
    """
    Verifica si es necesario procesar SALDOS INICIALES para una fecha
    (útil para evitar procesamientos innecesarios)
    """
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        
        # Buscar concepto SALDO INICIAL
        from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
        concepto_saldo_inicial = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO INICIAL'
        ).first()
        
        if not concepto_saldo_inicial:
            return {
                "necesario": True,
                "razon": "No se encontró el concepto SALDO INICIAL",
                "fecha": fecha
            }
        
        # Obtener cuentas
        from app.models.cuentas_bancarias import CuentaBancaria
        query_cuentas = db.query(CuentaBancaria)
        if compania_id:
            query_cuentas = query_cuentas.filter(CuentaBancaria.compania_id == compania_id)
        
        cuentas = query_cuentas.all()
        
        if not cuentas:
            return {
                "necesario": False,
                "razon": "No hay cuentas bancarias para procesar",
                "fecha": fecha
            }
        
        # Verificar si ya existen transacciones de SALDO INICIAL para esta fecha
        from app.models.transacciones_flujo_caja import TransaccionFlujoCaja
        from sqlalchemy import and_
        
        transacciones_existentes = db.query(TransaccionFlujoCaja).filter(
            and_(
                TransaccionFlujoCaja.concepto_id == concepto_saldo_inicial.id,
                TransaccionFlujoCaja.fecha == fecha
            )
        ).all()
        
        cuentas_con_saldo = len(transacciones_existentes)
        total_cuentas = len(cuentas)
        
        necesario = cuentas_con_saldo < total_cuentas
        
        return {
            "necesario": necesario,
            "razon": f"Ya procesado {cuentas_con_saldo}/{total_cuentas} cuentas" if not necesario else f"Faltan {total_cuentas - cuentas_con_saldo} cuentas por procesar",
            "fecha": fecha,
            "cuentas_procesadas": cuentas_con_saldo,
            "total_cuentas": total_cuentas,
            "compania_id": compania_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando necesidad: {str(e)}")


@router.post("/auto-procesar-saldos-iniciales")
async def auto_procesar_saldos_iniciales(
    fecha: str = Query(..., description="Fecha para procesar en formato YYYY-MM-DD"),
    compania_id: Optional[int] = Query(None, description="ID de compañía específica"),
    db: Session = Depends(get_db)
):
    """
    Procesa automáticamente todos los SALDOS INICIALES para una fecha
    (útil para ejecutar diariamente de forma automática)
    """
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        
        transacciones = SaldoInicialService.procesar_saldos_iniciales_para_fecha(
            fecha_obj, compania_id, db
        )
        
        return {
            "success": True,
            "message": f"Procesamiento automático completado para {fecha}",
            "fecha": fecha,
            "transacciones_procesadas": len(transacciones),
            "compania_id": compania_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento automático: {str(e)}")
