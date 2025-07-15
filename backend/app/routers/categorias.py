"""
Router de categorías - CRUD y gestión de categorías
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.routers.auth import get_current_active_user
from app.models.usuario import Usuario
from app.models.categoria import Categoria

router = APIRouter()


@router.get("/", summary="Listar categorías")
async def listar_categorias(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de todas las categorías"""
    return {"mensaje": "Endpoint de categorías - Por implementar"}


@router.post("/", summary="Crear categoría")
async def crear_categoria(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear una nueva categoría"""
    return {"mensaje": "Crear categoría - Por implementar"}


@router.get("/{categoria_id}", summary="Obtener categoría")
async def obtener_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener información de una categoría específica"""
    return {"mensaje": f"Obtener categoría {categoria_id} - Por implementar"}


@router.put("/{categoria_id}", summary="Actualizar categoría")
async def actualizar_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar una categoría"""
    return {"mensaje": f"Actualizar categoría {categoria_id} - Por implementar"}


@router.delete("/{categoria_id}", summary="Eliminar categoría")
async def eliminar_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar una categoría"""
    return {"mensaje": f"Eliminar categoría {categoria_id} - Por implementar"}
