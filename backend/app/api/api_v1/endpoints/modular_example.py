"""
API Endpoints principales actualizados para usar la capa CRUD
Este archivo muestra cómo integrar la nueva capa CRUD en los endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database import get_db
from app.crud import usuario, rol, cuenta, concepto, ingreso, egreso, auditoria
from app.schemas import usuario as usuario_schemas
from app.schemas import transaction as transaction_schemas
from app.schemas import auditoria as auditoria_schemas

router = APIRouter()

# ========== USUARIOS ==========
@router.get("/usuarios", response_model=List[usuario_schemas.UsuarioResponse])
def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios"""
    usuarios = usuario.get_multi(db, skip=skip, limit=limit)
    return usuarios

@router.post("/usuarios", response_model=usuario_schemas.UsuarioResponse)
def create_usuario(
    usuario_in: usuario_schemas.UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario"""
    # Verificar si el usuario ya existe
    db_usuario = usuario.get_by_email(db, email=usuario_in.email)
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    return usuario.create(db=db, obj_in=usuario_in)

@router.get("/usuarios/{usuario_id}", response_model=usuario_schemas.UsuarioResponse)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """Obtener usuario por ID"""
    db_usuario = usuario.get_by_id(db, id=usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_usuario

# ========== INGRESOS ==========
@router.get("/ingresos", response_model=List[transaction_schemas.IngresoResponse])
def get_ingresos(
    skip: int = 0,
    limit: int = 100,
    account_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de ingresos con filtros opcionales"""
    if start_date and end_date:
        return ingreso.get_by_date_range(
            db, start_date=start_date, end_date=end_date, account_id=account_id
        )
    elif account_id:
        return ingreso.get_by_account(db, account_id=account_id)
    else:
        return ingreso.get_multi(db, skip=skip, limit=limit)

@router.post("/ingresos", response_model=transaction_schemas.IngresoResponse)
def create_ingreso(
    ingreso_in: transaction_schemas.IngresoCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo ingreso"""
    return ingreso.create(db=db, obj_in=ingreso_in)

@router.get("/ingresos/estadisticas")
def get_ingresos_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de ingresos"""
    return ingreso.get_income_stats(db)

# ========== EGRESOS ==========
@router.get("/egresos", response_model=List[transaction_schemas.EgresoResponse])
def get_egresos(
    skip: int = 0,
    limit: int = 100,
    account_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de egresos con filtros opcionales"""
    if start_date and end_date:
        return egreso.get_by_date_range(
            db, start_date=start_date, end_date=end_date, account_id=account_id
        )
    elif account_id:
        return egreso.get_by_account(db, account_id=account_id)
    else:
        return egreso.get_multi(db, skip=skip, limit=limit)

@router.post("/egresos", response_model=transaction_schemas.EgresoResponse)
def create_egreso(
    egreso_in: transaction_schemas.EgresoCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo egreso"""
    return egreso.create(db=db, obj_in=egreso_in)

@router.get("/egresos/estadisticas")
def get_egresos_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de egresos"""
    return egreso.get_expense_stats(db)

# ========== AUDITORÍA ==========
@router.get("/auditoria", response_model=List[auditoria_schemas.AuditoriaResponse])
def get_auditoria(
    skip: int = 0,
    limit: int = 50,
    user_id: int = None,
    action: str = None,
    db: Session = Depends(get_db)
):
    """Obtener registros de auditoría"""
    if user_id:
        return auditoria.get_by_user(db, user_id=user_id)
    elif action:
        return auditoria.get_by_action(db, action=action)
    else:
        return auditoria.get_recent_activity(db, limit=limit)

@router.get("/auditoria/estadisticas")
def get_auditoria_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de auditoría"""
    return auditoria.get_audit_stats(db)

# ========== CUENTAS ==========
@router.get("/cuentas")
def get_cuentas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de cuentas"""
    return cuenta.get_multi(db, skip=skip, limit=limit)

@router.get("/cuentas/{cuenta_id}")
def get_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db)
):
    """Obtener cuenta por ID"""
    db_cuenta = cuenta.get_by_id(db, id=cuenta_id)
    if not db_cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )
    return db_cuenta

# ========== CONCEPTOS ==========
@router.get("/conceptos")
def get_conceptos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de conceptos"""
    return concepto.get_multi(db, skip=skip, limit=limit)

@router.get("/conceptos/tipo/{tipo}")
def get_conceptos_by_tipo(
    tipo: str,
    db: Session = Depends(get_db)
):
    """Obtener conceptos por tipo"""
    return concepto.get_by_tipo(db, tipo=tipo)
