from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models.bancos import Banco
from pydantic import BaseModel

router = APIRouter(prefix="/banks", tags=["banks"])

class BancoResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[BancoResponse])
def get_all_banks(db: Session = Depends(get_db)):
    """Obtener todos los bancos disponibles"""
    try:
        bancos = db.query(Banco).all()
        return bancos
    except Exception as e:
        print(f"Error en get_all_banks: {e}")
        raise

# Endpoint temporal sin autenticación para desarrollo
@router.get("/test", response_model=List[BancoResponse])
def test_get_all_banks(db: Session = Depends(get_db)):
    """TEST: Obtener todos los bancos disponibles (sin autenticación)"""
    try:
        bancos = db.query(Banco).all()
        return bancos
    except Exception as e:
        print(f"Error en test_get_all_banks: {e}")
        raise

# Endpoint de prueba simple
@router.get("/ping")
def ping():
    """Endpoint de prueba simple"""
    return {"message": "Banks API is working"}
