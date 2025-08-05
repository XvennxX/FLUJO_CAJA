from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_egresos():
    """Listar egresos"""
    return {"message": "Endpoint de egresos - En desarrollo"}

@router.post("/")
async def crear_egreso():
    """Crear nuevo egreso"""
    return {"message": "Crear egreso - En desarrollo"}

@router.get("/{egreso_id}")
async def obtener_egreso(egreso_id: int):
    """Obtener egreso por ID"""
    return {"message": f"Obtener egreso {egreso_id} - En desarrollo"}

@router.put("/{egreso_id}")
async def actualizar_egreso(egreso_id: int):
    """Actualizar egreso"""
    return {"message": f"Actualizar egreso {egreso_id} - En desarrollo"}

@router.delete("/{egreso_id}")
async def eliminar_egreso(egreso_id: int):
    """Eliminar egreso"""
    return {"message": f"Eliminar egreso {egreso_id} - En desarrollo"}
