"""
Router de dashboard - Métricas y estadísticas principales
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_active_user
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", summary="Dashboard principal")
async def dashboard_principal(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener datos principales para el dashboard"""
    return {
        "mensaje": "Dashboard principal",
        "usuario": current_user.nombre,
        "rol": current_user.rol.value,
        "datos": "Por implementar métricas clave"
    }


@router.get("/metricas-clave", summary="Métricas clave")
async def metricas_clave(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener métricas clave del sistema"""
    return {"mensaje": "Métricas clave - Por implementar"}


@router.get("/saldo-actual", summary="Saldo actual en caja")
async def saldo_actual(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener el saldo actual en caja"""
    return {"mensaje": "Saldo actual - Por implementar"}


@router.get("/flujo-ultimos-dias", summary="Flujo últimos días")
async def flujo_ultimos_dias(
    dias: int = 7,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener flujo de caja de los últimos N días"""
    return {"mensaje": f"Flujo últimos {dias} días - Por implementar"}


@router.get("/proyeccion-semanal", summary="Proyección semanal")
async def proyeccion_semanal(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener proyección de flujo para la próxima semana"""
    return {"mensaje": "Proyección semanal - Por implementar"}
