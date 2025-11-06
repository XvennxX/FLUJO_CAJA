from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from ..core.database import get_db
from ..models.cuentas_bancarias import CuentaBancaria, TipoCuenta
from ..models.cuenta_moneda import CuentaMoneda, TipoMoneda
from ..models.bancos import Banco
from ..models.companias import Compania
from ..services.auditoria_service import AuditoriaService
from ..api.auth import get_current_user
from ..services.auth_service import get_current_user_optional
from ..models.usuarios import Usuario
from pydantic import BaseModel

logger = logging.getLogger(__name__)
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
def create_bank_account(
    company_id: int, 
    cuenta_data: CuentaBancariaCreateForCompany, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
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
    
    # 📝 AUDITORÍA: Registrar creación de cuenta bancaria
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="CREATE",
            modulo="CUENTAS",
            entidad="CuentaBancaria",
            entidad_id=str(db_cuenta.id),
            descripcion=f"Creó cuenta bancaria: {banco.nombre} - {db_cuenta.numero_cuenta} para {compania.nombre}",
            valores_nuevos={
                "numero_cuenta": db_cuenta.numero_cuenta,
                "banco": banco.nombre,
                "compania": compania.nombre,
                "tipo_cuenta": db_cuenta.tipo_cuenta.value if hasattr(db_cuenta.tipo_cuenta, 'value') else str(db_cuenta.tipo_cuenta)
            }
        )
        logger.info(f"✅ Auditoría registrada: CREATE cuenta bancaria {db_cuenta.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de creación de cuenta bancaria: {e}")
    
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
def update_bank_account(
    account_id: int, 
    cuenta_data: CuentaBancariaUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar una cuenta bancaria"""
    db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
    if not db_cuenta:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    
    # Obtener información anterior para auditoría
    banco_anterior = db.query(Banco).filter(Banco.id == db_cuenta.banco_id).first()
    compania_anterior = db.query(Compania).filter(Compania.id == db_cuenta.compania_id).first()
    
    valores_anteriores = {
        "numero_cuenta": db_cuenta.numero_cuenta,
        "banco": banco_anterior.nombre if banco_anterior else "N/A",
        "tipo_cuenta": db_cuenta.tipo_cuenta.value if hasattr(db_cuenta.tipo_cuenta, 'value') else str(db_cuenta.tipo_cuenta)
    }
    
    # Actualizar solo los campos proporcionados
    update_data = cuenta_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cuenta, field, value)
    
    db.commit()
    db.refresh(db_cuenta)
    
    # Obtener información relacionada actualizada
    banco = db.query(Banco).filter(Banco.id == db_cuenta.banco_id).first()
    compania = db.query(Compania).filter(Compania.id == db_cuenta.compania_id).first()
    
    # 📝 AUDITORÍA: Registrar actualización de cuenta bancaria
    try:
        valores_nuevos = {
            "numero_cuenta": db_cuenta.numero_cuenta,
            "banco": banco.nombre if banco else "N/A",
            "tipo_cuenta": db_cuenta.tipo_cuenta.value if hasattr(db_cuenta.tipo_cuenta, 'value') else str(db_cuenta.tipo_cuenta)
        }
        
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="UPDATE",
            modulo="CUENTAS",
            entidad="CuentaBancaria",
            entidad_id=str(db_cuenta.id),
            descripcion=f"Actualizó cuenta bancaria: {banco.nombre if banco else 'N/A'} - {db_cuenta.numero_cuenta}",
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos
        )
        logger.info(f"✅ Auditoría registrada: UPDATE cuenta bancaria {db_cuenta.id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de actualización de cuenta bancaria: {e}")
    
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
def delete_bank_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una cuenta bancaria"""
    db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
    if not db_cuenta:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    
    # Obtener datos para auditoría antes de eliminar
    banco = db.query(Banco).filter(Banco.id == db_cuenta.banco_id).first()
    compania = db.query(Compania).filter(Compania.id == db_cuenta.compania_id).first()
    numero_cuenta_eliminado = db_cuenta.numero_cuenta
    banco_nombre = banco.nombre if banco else "N/A"
    compania_nombre = compania.nombre if compania else "N/A"
    
    db.delete(db_cuenta)
    db.commit()
    
    # 📝 AUDITORÍA: Registrar eliminación de cuenta bancaria
    try:
        AuditoriaService.registrar_accion(
            db=db,
            usuario=current_user,
            accion="DELETE",
            modulo="CUENTAS",
            entidad="CuentaBancaria",
            entidad_id=str(account_id),
            descripcion=f"Eliminó cuenta bancaria: {banco_nombre} - {numero_cuenta_eliminado} de {compania_nombre}",
            valores_anteriores={
                "numero_cuenta": numero_cuenta_eliminado,
                "banco": banco_nombre,
                "compania": compania_nombre
            }
        )
        logger.info(f"✅ Auditoría registrada: DELETE cuenta bancaria {account_id}")
    except Exception as e:
        logger.warning(f"Error en auditoría de eliminación de cuenta bancaria: {e}")
    
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
async def create_bank_account_test(
    company_id: int, 
    cuenta_data: CuentaBancariaCreateForCompany,
    request: Request,
    db: Session = Depends(get_db)
):
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

        # 📝 AUDITORÍA: Registrar creación de cuenta bancaria
        try:
            # Intentar obtener usuario autenticado, sino usar usuario por defecto
            current_user = await get_current_user_optional(request, db)
            
            if not current_user:
                # Si no hay usuario autenticado, usar usuario por defecto
                current_user = db.query(Usuario).filter(Usuario.email == "admin@sifco.com").first()
                if not current_user:
                    # Si no existe el admin, crear un usuario temporal para auditoría
                    current_user = type('Usuario', (), {
                        'id': 1,
                        'nombre': 'Sistema Test',
                        'email': 'sistema@test.com'
                    })()
            
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="CREATE",
                modulo="CUENTAS",
                entidad="CuentaBancaria",
                entidad_id=str(db_cuenta.id),
                descripcion=f"Creó cuenta bancaria: {banco.nombre} - {db_cuenta.numero_cuenta} para {compania.nombre}",
                valores_nuevos={
                    "numero_cuenta": db_cuenta.numero_cuenta,
                    "banco": banco.nombre,
                    "compania": compania.nombre
                }
            )
            logger.info(f"✅ Auditoría registrada: CREATE cuenta bancaria {db_cuenta.id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de creación de cuenta bancaria: {e}")

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
async def delete_bank_account_test(
    account_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Endpoint de prueba para eliminar una cuenta bancaria"""
    try:
        db_cuenta = db.query(CuentaBancaria).filter(CuentaBancaria.id == account_id).first()
        if not db_cuenta:
            raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
        
        # Guardar para auditoría
        numero_cuenta_eliminado = db_cuenta.numero_cuenta
        banco = db.query(Banco).filter(Banco.id == db_cuenta.banco_id).first()
        compania = db.query(Compania).filter(Compania.id == db_cuenta.compania_id).first()

        db.delete(db_cuenta)
        db.commit()

        # 📝 AUDITORÍA: Registrar eliminación de cuenta bancaria
        try:
            # Intentar obtener usuario autenticado, sino usar usuario por defecto
            current_user = await get_current_user_optional(request, db)
            
            if not current_user:
                # Si no hay usuario autenticado, usar usuario por defecto
                current_user = db.query(Usuario).filter(Usuario.email == "admin@sifco.com").first()
                if not current_user:
                    # Si no existe el admin, crear un usuario temporal para auditoría
                    current_user = type('Usuario', (), {
                        'id': 1,
                        'nombre': 'Sistema Test',
                        'email': 'sistema@test.com'
                    })()
            
            AuditoriaService.registrar_accion(
                db=db,
                usuario=current_user,
                accion="DELETE",
                modulo="CUENTAS",
                entidad="CuentaBancaria",
                entidad_id=str(account_id),
                descripcion=f"Eliminó cuenta bancaria: {banco.nombre if banco else 'N/A'} - {numero_cuenta_eliminado}",
                valores_anteriores={
                    "numero_cuenta": numero_cuenta_eliminado,
                    "banco": banco.nombre if banco else 'N/A',
                    "compania": compania.nombre if compania else 'N/A'
                }
            )
            logger.info(f"✅ Auditoría registrada: DELETE cuenta bancaria {account_id}")
        except Exception as e:
            logger.warning(f"Error en auditoría de eliminación de cuenta bancaria: {e}")

        return {"message": "Cuenta bancaria eliminada exitosamente"}
    except Exception as e:
        print(f"Error al eliminar cuenta bancaria: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
