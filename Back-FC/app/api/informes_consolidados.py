#!/usr/bin/env python3
"""
API para informes consolidados mensuales
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from calendar import monthrange

from app.core.database import get_db
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.companias import Compania
from app.models.cuentas_bancarias import CuentaBancaria
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja

router = APIRouter(prefix="/informes-consolidados", tags=["informes-consolidados"])

@router.get("/mensual")
async def obtener_informe_consolidado_mensual(
    año: int = Query(..., description="Año del informe"),
    mes: int = Query(..., description="Mes del informe (1-12)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene informe consolidado mensual con datos agregados por compañía y cuenta
    
    Retorna la misma estructura que los dashboards pero con totales mensuales:
    - Tesorería: Conceptos ID 1-51
    - Pagaduría: Conceptos ID 52+
    - Consolidado por compañía y cuenta bancaria
    """
    
    try:
        # Validar fecha
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
        
        # Calcular rango de fechas del mes
        _, ultimo_dia = monthrange(año, mes)
        fecha_inicio = date(año, mes, 1)
        fecha_fin = date(año, mes, ultimo_dia)
        
        print(f"🔍 OBTENIENDO INFORME CONSOLIDADO: {fecha_inicio} - {fecha_fin}")
        
        # Obtener todas las transacciones del mes
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha >= fecha_inicio,
            TransaccionFlujoCaja.fecha <= fecha_fin
        ).all()
        
        print(f"📊 TRANSACCIONES ENCONTRADAS: {len(transacciones)}")
        
        # Obtener compañías y cuentas
        companias = db.query(Compania).all()
        cuentas = db.query(CuentaBancaria).all()
        conceptos = db.query(ConceptoFlujoCaja).all()
        
        # Crear mapeos para eficiencia
        compania_map = {c.id: c for c in companias}
        cuenta_map = {c.id: c for c in cuentas}
        concepto_map = {c.id: c for c in conceptos}
        
        # Estructura de datos consolidados
        datos_consolidados = {
            "tesoreria": {},  # conceptos 1-51
            "pagaduria": {}   # conceptos 52+
        }
        
        # Procesar cada transacción
        for transaccion in transacciones:
            compania_id = transaccion.compania_id or 0  # Usar 0 si es NULL
            cuenta_id = transaccion.cuenta_id or 0      # Usar 0 si es NULL
            concepto_id = transaccion.concepto_id
            monto = float(transaccion.monto)
            
            print(f"📊 Procesando: concepto_id={concepto_id}, compania_id={compania_id}, cuenta_id={cuenta_id}, monto={monto}")
            
            # Determinar área (Tesorería vs Pagaduría)
            area = "tesoreria" if concepto_id <= 51 else "pagaduria"
            
            # Inicializar estructura si no existe
            if concepto_id not in datos_consolidados[area]:
                datos_consolidados[area][concepto_id] = {}
            
            if compania_id not in datos_consolidados[area][concepto_id]:
                datos_consolidados[area][concepto_id][compania_id] = {}
            
            if cuenta_id not in datos_consolidados[area][concepto_id][compania_id]:
                datos_consolidados[area][concepto_id][compania_id][cuenta_id] = 0
            
            # Sumar monto
            datos_consolidados[area][concepto_id][compania_id][cuenta_id] += monto
        
        # Formatear respuesta con información completa
        respuesta = {
            "periodo": {
                "año": año,
                "mes": mes,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "nombre_mes": fecha_inicio.strftime("%B %Y")
            },
            "metadata": {
                "total_transacciones": len(transacciones),
                "companias": [{"id": c.id, "nombre": c.nombre} for c in companias],
                "cuentas": [{"id": c.id, "numero_cuenta": c.numero_cuenta, "banco": c.banco.nombre if c.banco else None} for c in cuentas],
                "conceptos_tesoreria": [{"id": c.id, "nombre": c.nombre} for c in conceptos if c.id <= 51],
                "conceptos_pagaduria": [{"id": c.id, "nombre": c.nombre} for c in conceptos if c.id > 51]
            },
            "datos": datos_consolidados
        }
        
        print(f"✅ INFORME CONSOLIDADO GENERADO EXITOSAMENTE")
        return respuesta
        
    except Exception as e:
        print(f"❌ ERROR EN INFORME CONSOLIDADO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar informe consolidado: {str(e)}")

@router.get("/resumen-mensual")
async def obtener_resumen_mensual(
    año: int = Query(..., description="Año del resumen"),
    mes: int = Query(..., description="Mes del resumen (1-12)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene resumen de métricas del mes para mostrar en cards superiores
    """
    
    try:
        # Calcular rango de fechas del mes
        _, ultimo_dia = monthrange(año, mes)
        fecha_inicio = date(año, mes, 1)
        fecha_fin = date(año, mes, ultimo_dia)
        
        # Obtener transacciones del mes
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha >= fecha_inicio,
            TransaccionFlujoCaja.fecha <= fecha_fin
        ).all()
        
        # Calcular métricas
        total_ingresos = sum(float(t.monto) for t in transacciones if float(t.monto) > 0)
        total_gastos = abs(sum(float(t.monto) for t in transacciones if float(t.monto) < 0))
        balance_neto = total_ingresos - total_gastos
        total_transacciones = len(transacciones)
        
        # Calcular tasa de ahorro
        tasa_ahorro = (balance_neto / total_ingresos * 100) if total_ingresos > 0 else 0
        
        return {
            "periodo": {
                "año": año,
                "mes": mes,
                "nombre_mes": fecha_inicio.strftime("%B %Y")
            },
            "metricas": {
                "total_ingresos": total_ingresos,
                "total_gastos": total_gastos,
                "balance_neto": balance_neto,
                "tasa_ahorro": round(tasa_ahorro, 1),
                "total_transacciones": total_transacciones
            }
        }
        
    except Exception as e:
        print(f"❌ ERROR EN RESUMEN MENSUAL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar resumen mensual: {str(e)}")

@router.get("/mensual-multi-moneda")
async def obtener_informe_consolidado_multi_moneda(
    año: int = Query(..., description="Año del informe"),
    mes: int = Query(..., description="Mes del informe (1-12)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene informe consolidado mensual con cuentas expandidas por moneda.
    Las cuentas que tienen múltiples monedas aparecen como columnas separadas.
    
    Los valores en USD se convierten a COP usando la TRM del día.
    """
    
    try:
        from app.models.trm import TRM
        from app.models.cuenta_moneda import CuentaMoneda
        from app.models.bancos import Banco
        
        # Validar fecha
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
        
        # Calcular rango de fechas del mes
        _, ultimo_dia = monthrange(año, mes)
        fecha_inicio = date(año, mes, 1)
        fecha_fin = date(año, mes, ultimo_dia)
        
        print(f"🔍 OBTENIENDO INFORME MULTI-MONEDA: {fecha_inicio} - {fecha_fin}")
        
        # Obtener TRM promedio del mes para conversiones
        trm_promedio = db.query(TRM).filter(
            TRM.fecha >= fecha_inicio,
            TRM.fecha <= fecha_fin
        ).all()
        
        if trm_promedio:
            valor_trm = sum(float(t.valor) for t in trm_promedio) / len(trm_promedio)
        else:
            # Si no hay TRM del mes, buscar la más reciente
            trm_reciente = db.query(TRM).order_by(TRM.fecha.desc()).first()
            valor_trm = float(trm_reciente.valor) if trm_reciente else 4000  # Valor por defecto
        
        print(f"💱 TRM PROMEDIO DEL MES: {valor_trm}")
        
        # Obtener todas las transacciones del mes
        transacciones = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha >= fecha_inicio,
            TransaccionFlujoCaja.fecha <= fecha_fin
        ).all()
        
        print(f"📊 TRANSACCIONES ENCONTRADAS: {len(transacciones)}")
        
        # Obtener cuentas con sus monedas
        cuentas = db.query(CuentaBancaria).all()
        companias = db.query(Compania).all()
        conceptos = db.query(ConceptoFlujoCaja).all()
        bancos = db.query(Banco).all()
        
        # Crear mapeos
        compania_map = {c.id: c for c in companias}
        concepto_map = {c.id: c for c in conceptos}
        banco_map = {b.id: b for b in bancos}
        
        # Crear cuentas expandidas por moneda
        cuentas_expandidas = []
        for cuenta in cuentas:
            banco = banco_map.get(cuenta.banco_id)
            compania = compania_map.get(cuenta.compania_id)
            
            if cuenta.monedas:  # Cuenta tiene monedas configuradas
                for cuenta_moneda in cuenta.monedas:
                    moneda = cuenta_moneda.moneda.value
                    cuenta_expandida = {
                        "id": cuenta.id,
                        "cuenta_moneda_id": f"{cuenta.id}_{moneda}",
                        "numero_cuenta": cuenta.numero_cuenta,
                        "compania_id": cuenta.compania_id,
                        "banco_id": cuenta.banco_id,
                        "moneda": moneda,
                        "nombre_display": f"{banco.nombre if banco else 'BANCO'} ({moneda})",
                        "banco_nombre": banco.nombre if banco else "BANCO",
                        "compania_nombre": compania.nombre if compania else "COMPANIA"
                    }
                    cuentas_expandidas.append(cuenta_expandida)
            else:  # Cuenta sin monedas configuradas, asumir COP
                cuenta_expandida = {
                    "id": cuenta.id,
                    "cuenta_moneda_id": f"{cuenta.id}_COP",
                    "numero_cuenta": cuenta.numero_cuenta,
                    "compania_id": cuenta.compania_id,
                    "banco_id": cuenta.banco_id,
                    "moneda": "COP",
                    "nombre_display": f"{banco.nombre if banco else 'BANCO'} (COP)",
                    "banco_nombre": banco.nombre if banco else "BANCO",
                    "compania_nombre": compania.nombre if compania else "COMPANIA"
                }
                cuentas_expandidas.append(cuenta_expandida)
        
        print(f"🏦 CUENTAS EXPANDIDAS: {len(cuentas_expandidas)}")
        
        # Estructura de datos consolidados por cuenta-moneda
        datos_consolidados = {
            "tesoreria": {},  # conceptos 1-51
            "pagaduria": {}   # conceptos 52+
        }
        
        # Procesar cada transacción
        for transaccion in transacciones:
            compania_id = transaccion.compania_id or 0
            cuenta_id = transaccion.cuenta_id or 0
            concepto_id = transaccion.concepto_id
            monto = float(transaccion.monto)
            
            # Determinar área
            area = "tesoreria" if concepto_id <= 51 else "pagaduria"
            
            # Encontrar todas las cuentas-moneda que corresponden a esta transacción
            cuentas_coincidentes = [
                c for c in cuentas_expandidas 
                if c["id"] == cuenta_id and c["compania_id"] == compania_id
            ]
            
            if not cuentas_coincidentes:
                # Si no encuentra cuenta específica, crear una por defecto
                cuenta_moneda_id = f"{cuenta_id}_COP"
                cuentas_coincidentes = [{
                    "cuenta_moneda_id": cuenta_moneda_id,
                    "moneda": "COP"
                }]
            
            # Procesar cada cuenta-moneda coincidente
            for cuenta_expandida in cuentas_coincidentes:
                cuenta_moneda_id = cuenta_expandida["cuenta_moneda_id"]
                moneda = cuenta_expandida["moneda"]
                
                # Inicializar estructura
                if concepto_id not in datos_consolidados[area]:
                    datos_consolidados[area][concepto_id] = {}
                
                if compania_id not in datos_consolidados[area][concepto_id]:
                    datos_consolidados[area][concepto_id][compania_id] = {}
                
                if cuenta_moneda_id not in datos_consolidados[area][concepto_id][compania_id]:
                    datos_consolidados[area][concepto_id][compania_id][cuenta_moneda_id] = {
                        "monto_original": 0,
                        "monto_cop": 0,
                        "moneda": moneda
                    }
                
                # Sumar montos
                datos_consolidados[area][concepto_id][compania_id][cuenta_moneda_id]["monto_original"] += monto
                
                # Convertir a COP si es necesario
                if moneda == "USD":
                    monto_cop = monto * valor_trm
                else:
                    monto_cop = monto
                
                datos_consolidados[area][concepto_id][compania_id][cuenta_moneda_id]["monto_cop"] += monto_cop
        
        # Formatear respuesta
        respuesta = {
            "periodo": {
                "año": año,
                "mes": mes,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat(),
                "nombre_mes": fecha_inicio.strftime("%B %Y")
            },
            "conversion": {
                "trm_promedio": valor_trm,
                "fecha_trm": fecha_fin.isoformat()
            },
            "metadata": {
                "total_transacciones": len(transacciones),
                "cuentas_expandidas": len(cuentas_expandidas),
                "companias": [{"id": c.id, "nombre": c.nombre} for c in companias],
                "conceptos_tesoreria": [{"id": c.id, "nombre": c.nombre} for c in conceptos if c.id <= 51],
                "conceptos_pagaduria": [{"id": c.id, "nombre": c.nombre} for c in conceptos if c.id > 51]
            },
            "cuentas_expandidas": cuentas_expandidas,
            "datos": datos_consolidados
        }
        
        print(f"✅ INFORME MULTI-MONEDA GENERADO EXITOSAMENTE")
        return respuesta
        
    except Exception as e:
        print(f"❌ ERROR EN INFORME MULTI-MONEDA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar informe multi-moneda: {str(e)}")