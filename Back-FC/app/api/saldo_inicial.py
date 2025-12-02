"""
API para manejar SALDOS INICIALES automáticos
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.saldo_inicial_service import SaldoInicialService
from app.services.importador_saldos_service import ImportadorSaldosService
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


class CargueInicialRequest(BaseModel):
    fecha: str
    modificaciones: List[dict]


@router.post("/guardar-cargue-inicial")
async def guardar_cargue_inicial(
    request: CargueInicialRequest,
    db: Session = Depends(get_db)
):
    """
    Guarda el cargue inicial de saldos para una fecha específica
    """
    try:
        from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
        from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
        from datetime import datetime
        
        fecha_obj = datetime.strptime(request.fecha, '%Y-%m-%d').date()
        transacciones_creadas = 0
        
        # Buscar conceptos necesarios
        saldo_inicial_concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO INICIAL',
            ConceptoFlujoCaja.area == 'tesoreria'
        ).first()
        
        saldo_dia_anterior_concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO DIA ANTERIOR',
            ConceptoFlujoCaja.area == 'pagaduria'
        ).first()
        
        if not saldo_inicial_concepto or not saldo_dia_anterior_concepto:
            raise HTTPException(status_code=404, detail="Conceptos SALDO INICIAL o SALDO DIA ANTERIOR no encontrados")
        
        for modificacion in request.modificaciones:
            cuenta_id = modificacion.get('cuenta_id')
            saldo_inicial = modificacion.get('saldo_inicial')
            saldo_dia_anterior = modificacion.get('saldo_dia_anterior')
            
            # Obtener compania_id de la cuenta
            from app.models.cuenta_moneda import CuentaMoneda
            from app.models.cuentas_bancarias import CuentaBancaria
            
            cuenta_moneda = db.query(CuentaMoneda).filter(CuentaMoneda.id == cuenta_id).first()
            if not cuenta_moneda:
                continue
                
            cuenta_bancaria = db.query(CuentaBancaria).filter(CuentaBancaria.id == cuenta_moneda.id_cuenta).first()
            if not cuenta_bancaria:
                continue
            
            # Guardar SALDO INICIAL TESORERÍA si está definido
            if saldo_inicial is not None and saldo_inicial != 0:
                # Buscar transacción existente
                transaccion_existente = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_obj,
                    TransaccionFlujoCaja.concepto_id == saldo_inicial_concepto.id,
                    TransaccionFlujoCaja.cuenta_id == cuenta_id,
                    TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
                ).first()
                
                if transaccion_existente:
                    # Actualizar existente
                    transaccion_existente.monto = saldo_inicial
                    transaccion_existente.descripcion = "Cargue inicial manual - Actualizado"
                else:
                    # Crear nueva
                    nueva_transaccion = TransaccionFlujoCaja(
                        concepto_id=saldo_inicial_concepto.id,
                        cuenta_id=cuenta_id,
                        compania_id=cuenta_bancaria.compania_id,
                        fecha=fecha_obj,
                        monto=saldo_inicial,
                        descripcion="Cargue inicial manual",
                        usuario_id=1,  # TODO: usar usuario actual
                        area=AreaTransaccion.tesoreria
                    )
                    db.add(nueva_transaccion)
                    transacciones_creadas += 1
            
            # Guardar SALDO DÍA ANTERIOR PAGADURÍA si está definido
            if saldo_dia_anterior is not None and saldo_dia_anterior != 0:
                # Buscar transacción existente
                transaccion_existente = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_obj,
                    TransaccionFlujoCaja.concepto_id == saldo_dia_anterior_concepto.id,
                    TransaccionFlujoCaja.cuenta_id == cuenta_id,
                    TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
                ).first()
                
                if transaccion_existente:
                    # Actualizar existente
                    transaccion_existente.monto = saldo_dia_anterior
                    transaccion_existente.descripcion = "Cargue inicial manual - Actualizado"
                else:
                    # Crear nueva
                    nueva_transaccion = TransaccionFlujoCaja(
                        concepto_id=saldo_dia_anterior_concepto.id,
                        cuenta_id=cuenta_id,
                        compania_id=cuenta_bancaria.compania_id,
                        fecha=fecha_obj,
                        monto=saldo_dia_anterior,
                        descripcion="Cargue inicial manual",
                        usuario_id=1,  # TODO: usar usuario actual
                        area=AreaTransaccion.pagaduria
                    )
                    db.add(nueva_transaccion)
                    transacciones_creadas += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cargue inicial guardado correctamente para {request.fecha}",
            "transacciones_creadas": transacciones_creadas,
            "fecha": request.fecha
        }
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error guardando cargue inicial: {str(e)}")


@router.get("/obtener-saldos")
async def obtener_saldos_fecha(
    fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los saldos existentes para una fecha específica
    """
    try:
        from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
        from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
        from datetime import datetime
        
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Buscar conceptos
        saldo_inicial_concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO INICIAL',
            ConceptoFlujoCaja.area == 'tesoreria'
        ).first()
        
        saldo_dia_anterior_concepto = db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == 'SALDO DIA ANTERIOR',
            ConceptoFlujoCaja.area == 'pagaduria'
        ).first()
        
        saldos = []
        
        if saldo_inicial_concepto:
            transacciones_tesoreria = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_obj,
                TransaccionFlujoCaja.concepto_id == saldo_inicial_concepto.id,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria
            ).all()
            
            for t in transacciones_tesoreria:
                saldos.append({
                    "cuenta_id": t.cuenta_id,
                    "saldo_inicial": float(t.monto),
                    "saldo_dia_anterior": 0
                })
        
        if saldo_dia_anterior_concepto:
            transacciones_pagaduria = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_obj,
                TransaccionFlujoCaja.concepto_id == saldo_dia_anterior_concepto.id,
                TransaccionFlujoCaja.area == AreaTransaccion.pagaduria
            ).all()
            
            for t in transacciones_pagaduria:
                # Buscar si ya existe en saldos
                existente = next((s for s in saldos if s["cuenta_id"] == t.cuenta_id), None)
                if existente:
                    existente["saldo_dia_anterior"] = float(t.monto)
                else:
                    saldos.append({
                        "cuenta_id": t.cuenta_id,
                        "saldo_inicial": 0,
                        "saldo_dia_anterior": float(t.monto)
                    })
        
        return saldos
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo saldos: {str(e)}")


@router.post("/importar-saldos")
async def importar_saldos_iniciales(
    tipo_carga: str = Form(..., description="Tipo de carga: 'mes' o 'dia'"),
    mes: str = Form(..., description="Mes en formato YYYY-MM"),
    dia: Optional[str] = Form(None, description="Día específico YYYY-MM-DD si tipo_carga=dia"),
    sobrescribir: bool = Form(False, description="Si true, sobrescribe transacciones existentes"),
    archivo_excel: UploadFile = File(..., description="Excel con SALDO INICIAL"),
    db: Session = Depends(get_db)
):
    """
    Importa saldos iniciales desde UN archivo Excel con campo 'SALDO INICIAL'.
    Los valores se usan tanto para Tesorería como para Pagaduría.
    - tipo_carga: 'mes' procesa todos los días anteriores del mes; 'dia' solo el día indicado.
    - mes: formato YYYY-MM.
    - dia: requerido solo cuando tipo_carga='dia'.
    - sobrescribir: si existe una transacción previa la reemplaza.
    Devuelve resumen de cuentas procesadas, días sin TRM y errores.
    """
    from app.services.importador_saldos_service import ImportadorSaldosService
    try:
        # Validar tipo_carga
        if tipo_carga not in ('mes', 'dia'):
            raise HTTPException(status_code=400, detail="tipo_carga debe ser 'mes' o 'dia'")
        
        contenido = await archivo_excel.read()
        
        resultado = ImportadorSaldosService.importar(
            db=db,
            tipo_carga=tipo_carga,
            mes=mes,
            dia=dia,
            sobrescribir=sobrescribir,
            archivo_excel=contenido,
            usuario_id=1  # TODO: reemplazar por usuario autenticado
        )
        return {"success": True, **resultado}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importando saldos: {str(e)}")
