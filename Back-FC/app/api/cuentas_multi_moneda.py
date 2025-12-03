#!/usr/bin/env python3
"""
API para obtener cuentas bancarias expandidas por moneda
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date

from app.core.database import get_db
from app.models.cuentas_bancarias import CuentaBancaria
from app.models.cuenta_moneda import CuentaMoneda, TipoMoneda
from app.models.companias import Compania
from app.models.bancos import Banco
from app.models.trm import TRM

router = APIRouter(prefix="/cuentas-multi-moneda", tags=["cuentas-multi-moneda"])

@router.get("/expandidas")
async def obtener_cuentas_expandidas_por_moneda(
    incluir_trm: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las cuentas bancarias expandidas por moneda.
    Si una cuenta tiene COP y USD, aparecerá dos veces: una para cada moneda.
    """
    
    try:
        print("🔍 OBTENIENDO CUENTAS EXPANDIDAS POR MONEDA")
        
        # Obtener todas las cuentas bancarias con sus relaciones
        cuentas = db.query(CuentaBancaria).all()
        
        # Obtener TRM del día si es necesario
        trm_actual = None
        if incluir_trm:
            trm_actual = db.query(TRM).filter(TRM.fecha == date.today()).first()
            if not trm_actual:
                # Buscar la TRM más reciente si no hay para hoy
                trm_actual = db.query(TRM).order_by(TRM.fecha.desc()).first()
        
        cuentas_expandidas = []
        
        for cuenta in cuentas:
            # Obtener información relacionada
            banco = db.query(Banco).filter(Banco.id == cuenta.banco_id).first()
            compania = db.query(Compania).filter(Compania.id == cuenta.compania_id).first()
            
            # Para cada moneda de la cuenta, crear una entrada
            for cuenta_moneda in cuenta.monedas:
                moneda = cuenta_moneda.moneda.value
                
                # Crear identificador único para la cuenta-moneda
                cuenta_moneda_id = f"{cuenta.id}_{moneda}"
                
                cuenta_expandida = {
                    "id": cuenta.id,  # ID original de la cuenta
                    "cuenta_moneda_id": cuenta_moneda_id,  # ID único cuenta-moneda
                    "numero_cuenta": cuenta.numero_cuenta,
                    "compania_id": cuenta.compania_id,
                    "banco_id": cuenta.banco_id,
                    "tipo_cuenta": cuenta.tipo_cuenta.value if cuenta.tipo_cuenta else "CORRIENTE",
                    "moneda": moneda,
                    "banco": {
                        "id": banco.id,
                        "nombre": banco.nombre
                    } if banco else None,
                    "compania": {
                        "id": compania.id,
                        "nombre": compania.nombre
                    } if compania else None,
                    # Nombre completo para mostrar en UI
                    "nombre_completo": f"{banco.nombre if banco else 'BANCO'} {cuenta.numero_cuenta[-4:]} ({moneda})",
                    "nombre_display": f"{banco.nombre if banco else 'BANCO'} ({moneda})"
                }
                
                # Agregar información de TRM si está disponible y es USD
                if trm_actual and moneda == "USD":
                    cuenta_expandida["trm"] = {
                        "fecha": trm_actual.fecha.isoformat(),
                        "valor": float(trm_actual.valor)
                    }
                
                cuentas_expandidas.append(cuenta_expandida)
        
        print(f"✅ Cuentas expandidas generadas: {len(cuentas_expandidas)}")
        print(f"📊 TRM actual: {trm_actual.valor if trm_actual else 'No disponible'}")
        
        return {
            "cuentas": cuentas_expandidas,
            "total_cuentas_originales": len(cuentas),
            "total_cuentas_expandidas": len(cuentas_expandidas),
            "trm_actual": {
                "fecha": trm_actual.fecha.isoformat(),
                "valor": float(trm_actual.valor)
            } if trm_actual else None
        }
        
    except Exception as e:
        print(f"❌ ERROR AL OBTENER CUENTAS EXPANDIDAS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener cuentas expandidas: {str(e)}")

@router.get("/por-compania/{compania_id}")
async def obtener_cuentas_expandidas_por_compania(
    compania_id: int,
    incluir_trm: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtiene cuentas bancarias expandidas por moneda para una compañía específica
    """
    
    try:
        print(f"🔍 OBTENIENDO CUENTAS EXPANDIDAS PARA COMPAÑÍA {compania_id}")
        
        # Verificar que la compañía existe
        compania = db.query(Compania).filter(Compania.id == compania_id).first()
        if not compania:
            raise HTTPException(status_code=404, detail="Compañía no encontrada")
        
        # Obtener cuentas de la compañía
        cuentas = db.query(CuentaBancaria).filter(CuentaBancaria.compania_id == compania_id).all()
        
        # Obtener TRM del día si es necesario
        trm_actual = None
        if incluir_trm:
            trm_actual = db.query(TRM).filter(TRM.fecha == date.today()).first()
            if not trm_actual:
                trm_actual = db.query(TRM).order_by(TRM.fecha.desc()).first()
        
        cuentas_expandidas = []
        
        for cuenta in cuentas:
            banco = db.query(Banco).filter(Banco.id == cuenta.banco_id).first()
            
            for cuenta_moneda in cuenta.monedas:
                moneda = cuenta_moneda.moneda.value
                cuenta_moneda_id = f"{cuenta.id}_{moneda}"
                
                cuenta_expandida = {
                    "id": cuenta.id,
                    "cuenta_moneda_id": cuenta_moneda_id,
                    "numero_cuenta": cuenta.numero_cuenta,
                    "compania_id": cuenta.compania_id,
                    "banco_id": cuenta.banco_id,
                    "tipo_cuenta": cuenta.tipo_cuenta.value if cuenta.tipo_cuenta else "CORRIENTE",
                    "moneda": moneda,
                    "banco": {
                        "id": banco.id,
                        "nombre": banco.nombre
                    } if banco else None,
                    "compania": {
                        "id": compania.id,
                        "nombre": compania.nombre
                    },
                    "nombre_completo": f"{banco.nombre if banco else 'BANCO'} {cuenta.numero_cuenta[-4:]} ({moneda})",
                    "nombre_display": f"{banco.nombre if banco else 'BANCO'} ({moneda})"
                }
                
                if trm_actual and moneda == "USD":
                    cuenta_expandida["trm"] = {
                        "fecha": trm_actual.fecha.isoformat(),
                        "valor": float(trm_actual.valor)
                    }
                
                cuentas_expandidas.append(cuenta_expandida)
        
        return {
            "compania": {
                "id": compania.id,
                "nombre": compania.nombre
            },
            "cuentas": cuentas_expandidas,
            "total_cuentas_originales": len(cuentas),
            "total_cuentas_expandidas": len(cuentas_expandidas),
            "trm_actual": {
                "fecha": trm_actual.fecha.isoformat(),
                "valor": float(trm_actual.valor)
            } if trm_actual else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener cuentas de la compañía: {str(e)}")