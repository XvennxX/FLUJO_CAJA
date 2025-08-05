from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.rol import Rol
from app.schemas.rol import RolResponse

router = APIRouter()

@router.get("/", response_model=List[RolResponse])
async def listar_roles(
    db: Session = Depends(get_db)
):
    """Listar todos los roles disponibles"""
    roles = db.query(Rol).all()
    return roles
