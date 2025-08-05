from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_conceptos():
    """Listar conceptos"""
    return {"message": "Endpoint de conceptos - En desarrollo"}

@router.post("/")
async def crear_concepto():
    """Crear nuevo concepto"""
    return {"message": "Crear concepto - En desarrollo"}

@router.put("/{concepto_id}")
async def actualizar_concepto(concepto_id: int):
    """Actualizar concepto"""
    return {"message": f"Actualizar concepto {concepto_id} - En desarrollo"}

@router.delete("/{concepto_id}")
async def eliminar_concepto(concepto_id: int):
    """Eliminar concepto"""
    return {"message": f"Eliminar concepto {concepto_id} - En desarrollo"}
