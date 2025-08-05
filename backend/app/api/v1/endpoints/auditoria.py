from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_auditoria():
    """Listar acciones registradas"""
    return {"message": "Endpoint de auditoría - En desarrollo"}

@router.get("/usuario/{usuario_id}")
async def auditoria_por_usuario(usuario_id: int):
    """Ver acciones por usuario"""
    return {"message": f"Auditoría usuario {usuario_id} - En desarrollo"}
