from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models.cuentas_bancarias import CuentaBancaria, TipoCuenta
from ..models.cuenta_moneda import CuentaMoneda, TipoMoneda
from ..models.bancos import Banco
from ..models.companias import Compania
from pydantic import BaseModel

router = APIRouter(prefix="/bank-accounts", tags=["bank-accounts"])

# Schemas
class CuentaBancariaCreate(BaseModel):
    numero_cuenta: str
    compania_id: int
    banco_id: int
    tipo_cuenta: TipoCuenta = TipoCuenta.CORRIENTE
    monedas: List[TipoMoneda] = [TipoMoneda.COP]

class CuentaBancariaCreateForCompany(BaseModel):
    numero_cuenta: str
    banco_id: int
    tipo_cuenta: TipoCuenta = TipoCuenta.CORRIENTE
    monedas: List[TipoMoneda] = [TipoMoneda.COP]

class CuentaBancariaUpdate(BaseModel):
    numero_cuenta: str = None
    banco_id: int = None
    tipo_cuenta: TipoCuenta = None
    monedas: List[TipoMoneda] = None

class CuentaBancariaResponse(BaseModel):
    id: int
    numero_cuenta: str
    compania_id: int
    banco_id: int
    tipo_cuenta: TipoCuenta
    monedas: List[TipoMoneda]
    banco_nombre: str = None
    compania_nombre: str = None

    class Config:
        from_attributes = True

class BancoResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

# Endpoints de prueba temporales
@router.get("/test/banks")
def get_banks_test(db: Session = Depends(get_db)):
    """Endpoint de prueba para obtener todos los bancos"""
    try:
        bancos = db.query(Banco).all()
        return [{"id": banco.id, "nombre": banco.nombre} for banco in bancos]
    except Exception as e:
        print(f"Error al obtener bancos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/test/companies/{company_id}")
def get_company_bank_accounts_test(company_id: int, db: Session = Depends(get_db)):
    """Endpoint de prueba para obtener cuentas bancarias de una compañía"""
    try:
        cuentas = db.query(CuentaBancaria).filter(CuentaBancaria.compania_id == company_id).all()
        result = []
        for cuenta in cuentas:
            result.append({
                "id": cuenta.id,
                "numero_cuenta": cuenta.numero_cuenta,
                "compania_id": cuenta.compania_id,
                "banco_id": cuenta.banco_id,
                "monedas": [m.moneda.value for m in cuenta.monedas],
                "tipo_cuenta": cuenta.tipo_cuenta.value if cuenta.tipo_cuenta else "CORRIENTE"
            })
        return result
    except Exception as e:
        print(f"Error al obtener cuentas bancarias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
@router.get("/companies/{company_id}", response_model=List[CuentaBancariaResponse])
def get_company_bank_accounts(company_id: int, db: Session = Depends(get_db)):
    """Obtener todas las cuentas bancarias de una compañía"""
    cuentas = db.query(CuentaBancaria).filter(CuentaBancaria.compania_id == company_id).all()
    
    result = []
    for cuenta in cuentas:
        banco = db.query(Banco).filter(Banco.id == cuenta.banco_id).first()
        compania = db.query(Compania).filter(Compania.id == cuenta.compania_id).first()
        
        cuenta_data = CuentaBancariaResponse(
            id=cuenta.id,
            numero_cuenta=cuenta.numero_cuenta,
            compania_id=cuenta.compania_id,
            banco_id=cuenta.banco_id,
            moneda=cuenta.moneda,
            banco_nombre=banco.nombre if banco else None,
            compania_nombre=compania.nombre if compania else None
        )
        result.append(cuenta_data)
    
    return result

@router.post("/companies/{company_id}", response_model=CuentaBancariaResponse)
def create_bank_account(company_id: int, cuenta_data: CuentaBancariaCreateForCompany, db: Session = Depends(get_db)):
    """Crear una nueva cuenta bancaria para una compañía"""
    # Verificar que la compañía existe
    compania = db.query(Compania).filter(Compania.id == company_id).first()
    if not compania:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    
    # Verificar que el banco existe
    banco = db.query(Banco).filter(Banco.id == cuenta_data.banco_id).first()
    if not banco:
        raise HTTPException(status_code=404, detail="Banco no encontrado")
    
    # Verificar que no existe otra cuenta con el mismo número para la misma compañía
    existing_cuenta = db.query(CuentaBancaria).filter(
        CuentaBancaria.numero_cuenta == cuenta_data.numero_cuenta,
        CuentaBancaria.compania_id == company_id
    ).first()
    if existing_cuenta:
        raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese número para esta compañía")
    
    # Crear la cuenta
    db_cuenta = CuentaBancaria(
        numero_cuenta=cuenta_data.numero_cuenta,
        compania_id=company_id,
        banco_id=cuenta_data.banco_id,
        tipo_cuenta=cuenta_data.tipo_cuenta
    )
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    
    # Crear las relaciones de monedas
    for moneda in cuenta_data.monedas:
        cuenta_moneda = CuentaMoneda(
            id_cuenta=db_cuenta.id,
            moneda=moneda
        )
        db.add(cuenta_moneda)
    
    db.commit()
    db.refresh(db_cuenta)
    
    return CuentaBancariaResponse(
        id=db_cuenta.id,
        numero_cuenta=db_cuenta.numero_cuenta,
        compania_id=db_cuenta.compania_id,
        banco_id=db_cuenta.banco_id,
        tipo_cuenta=db_cuenta.tipo_cuenta,
        monedas=[m.moneda for m in db_cuenta.monedas],
        banco_nombre=banco.nombre,
        compania_nombre=compania.nombre
    )

@router.put("/{account_id}", response_model=CuentaBancariaResponse)
def update_bank_account(account_id: int, cuenta_data: CuentaBancariaUpdate, db: Session = Depends(get_db)):
    """Actualizar una cuenta bancaria"""
    db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
    if not db_cuenta:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    
    # Actualizar solo los campos proporcionados
    update_data = cuenta_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cuenta, field, value)
    
    db.commit()
    db.refresh(db_cuenta)
    
    # Obtener información relacionada
    banco = db.query(Banco).filter(Banco.id == db_cuenta.banco_id).first()
    compania = db.query(Compania).filter(Compania.id == db_cuenta.compania_id).first()
    
    return CuentaBancariaResponse(
        id=db_cuenta.id,
        numero_cuenta=db_cuenta.numero_cuenta,
        compania_id=db_cuenta.compania_id,
        banco_id=db_cuenta.banco_id,
        moneda=db_cuenta.moneda,
        banco_nombre=banco.nombre if banco else None,
        compania_nombre=compania.nombre if compania else None
    )

@router.delete("/{account_id}")
def delete_bank_account(account_id: int, db: Session = Depends(get_db)):
    """Eliminar una cuenta bancaria"""
    db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
    if not db_cuenta:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    
    db.delete(db_cuenta)
    db.commit()
    return {"message": "Cuenta bancaria eliminada exitosamente"}

# Endpoint para obtener todos los bancos disponibles
@router.get("/banks", response_model=List[BancoResponse])
def get_all_banks(db: Session = Depends(get_db)):
    """Obtener todos los bancos disponibles"""
    bancos = db.query(Banco).all()
    return bancos

# ENDPOINTS DE TEST - COMENTADOS PARA PRODUCCIÓN
# @router.get("/test/banks", response_model=List[BancoResponse])
# def test_get_all_banks(db: Session = Depends(get_db)):
#     """TEST: Obtener todos los bancos disponibles (sin autenticación)"""
#     # Código comentado para producción
#     pass

# @router.get("/test/banks-simple")
# def test_banks_simple(db: Session = Depends(get_db)):
#     """TEST: Endpoint simple para probar conexión"""
#     # Código comentado para producción
#     pass

@router.post("/test/companies/{company_id}")
def create_bank_account_test(company_id: int, cuenta_data: CuentaBancariaCreateForCompany, db: Session = Depends(get_db)):
    """Endpoint de prueba para crear una cuenta bancaria"""
    try:
        # Verificar que la compañía existe
        compania = db.query(Compania).filter(Compania.id == company_id).first()
        if not compania:
            raise HTTPException(status_code=404, detail="Compañía no encontrada")
        
        # Verificar que el banco existe
        banco = db.query(Banco).filter(Banco.id == cuenta_data.banco_id).first()
        if not banco:
            raise HTTPException(status_code=404, detail="Banco no encontrado")
        
        # Crear la cuenta
        db_cuenta = CuentaBancaria(
            numero_cuenta=cuenta_data.numero_cuenta,
            compania_id=company_id,
            banco_id=cuenta_data.banco_id,
            tipo_cuenta=cuenta_data.tipo_cuenta
        )
        db.add(db_cuenta)
        db.commit()
        db.refresh(db_cuenta)
        
        # Crear las relaciones de monedas
        for moneda in cuenta_data.monedas:
            cuenta_moneda = CuentaMoneda(
                id_cuenta=db_cuenta.id,
                moneda=moneda
            )
            db.add(cuenta_moneda)
        
        db.commit()
        db.refresh(db_cuenta)
        
        return {
            "id": db_cuenta.id,
            "numero_cuenta": db_cuenta.numero_cuenta,
            "compania_id": db_cuenta.compania_id,
            "banco_id": db_cuenta.banco_id,
            "monedas": [m.moneda.value for m in db_cuenta.monedas],
            "tipo_cuenta": db_cuenta.tipo_cuenta.value if db_cuenta.tipo_cuenta else "CORRIENTE",
            "banco_nombre": banco.nombre,
            "compania_nombre": compania.nombre
        }
    except Exception as e:
        print(f"Error al crear cuenta bancaria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/all")
def get_all_bank_accounts(db: Session = Depends(get_db)):
    """Obtener todas las cuentas bancarias de todas las compañías"""
    try:
        # Consultar todas las cuentas bancarias con sus relaciones
        cuentas = db.query(CuentaBancaria).all()
        
        resultado = []
        for cuenta in cuentas:
            # Obtener banco
            banco = db.query(Banco).filter(Banco.id == cuenta.banco_id).first()
            # Obtener compañía
            compania = db.query(Compania).filter(Compania.id == cuenta.compania_id).first()
            
            resultado.append({
                "id": cuenta.id,
                "numero_cuenta": cuenta.numero_cuenta,
                "compania_id": cuenta.compania_id,
                "banco_id": cuenta.banco_id,
                "monedas": [m.moneda.value for m in cuenta.monedas],
                "tipo_cuenta": cuenta.tipo_cuenta.value if cuenta.tipo_cuenta else "CORRIENTE",
                "banco": {
                    "id": banco.id,
                    "nombre": banco.nombre
                } if banco else None,
                "compania": {
                    "id": compania.id,
                    "nombre": compania.nombre
                } if compania else None
            })
        
        return resultado
    except Exception as e:
        print(f"Error al obtener todas las cuentas bancarias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/test/{account_id}")
def delete_bank_account_test(account_id: int, db: Session = Depends(get_db)):
    """Endpoint de prueba para eliminar una cuenta bancaria"""
    try:
        db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
        if not db_cuenta:
            raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
        
        db.delete(db_cuenta)
        db.commit()
        return {"message": "Cuenta bancaria eliminada exitosamente"}
    except Exception as e:
        print(f"Error al eliminar cuenta bancaria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
