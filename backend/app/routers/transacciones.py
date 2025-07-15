"""
Router de transacciones - CRUD y gestión de transacciones
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.routers.auth import get_current_active_user
from app.models.usuario import Usuario

router = APIRouter()


@router.get("/", summary="Listar transacciones")
async def listar_transacciones(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de transacciones con filtros"""
    return {"mensaje": "Endpoint de transacciones - Por implementar"}


@router.post("/", summary="Crear transacción")
async def crear_transaccion(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear una nueva transacción"""
    return {"mensaje": "Crear transacción - Por implementar"}


@router.get("/flujo-diario/{fecha}", summary="Flujo de caja del día")
async def flujo_diario(
    fecha: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener el flujo de caja de un día específico"""
    return {"mensaje": f"Flujo del día {fecha} - Por implementar"}


@router.get("/flujo-mensual/{mes}/{anio}", summary="Flujo de caja del mes")
async def flujo_mensual(
    mes: int,
    anio: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener el flujo de caja de un mes completo (tipo Excel)"""
    return {"mensaje": f"Flujo del mes {mes}/{anio} - Por implementar"}


@router.get("/{transaccion_id}", summary="Obtener transacción")
async def obtener_transaccion(
    transaccion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener información de una transacción específica"""
    return {"mensaje": f"Obtener transacción {transaccion_id} - Por implementar"}


@router.put("/{transaccion_id}", summary="Actualizar transacción")
async def actualizar_transaccion(
    transaccion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar una transacción"""
    return {"mensaje": f"Actualizar transacción {transaccion_id} - Por implementar"}


@router.delete("/{transaccion_id}", summary="Eliminar transacción")
async def eliminar_transaccion(
    transaccion_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar una transacción"""
    return {"mensaje": f"Eliminar transacción {transaccion_id} - Por implementar"}
