from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_cuentas():
    """Listar cuentas"""
    return {"message": "Endpoint de cuentas - En desarrollo"}

@router.post("/")
async def crear_cuenta():
    """Crear nueva cuenta"""
    return {"message": "Crear cuenta - En desarrollo"}

@router.get("/{cuenta_id}/movimientos")
async def obtener_movimientos_cuenta(cuenta_id: int):
    """Obtener movimientos de una cuenta"""
    return {"message": f"Movimientos cuenta {cuenta_id} - En desarrollo"}

@router.put("/{cuenta_id}")
async def actualizar_cuenta(cuenta_id: int):
    """Actualizar cuenta"""
    return {"message": f"Actualizar cuenta {cuenta_id} - En desarrollo"}

@router.patch("/{cuenta_id}/saldo")
async def ajustar_saldo_cuenta(cuenta_id: int):
    """Ajustar saldo de cuenta"""
    return {"message": f"Ajustar saldo cuenta {cuenta_id} - En desarrollo"}
