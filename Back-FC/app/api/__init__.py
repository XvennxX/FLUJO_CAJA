from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .companies import router as companies_router
from .cuentas_bancarias import router as cuentas_bancarias_router
from .trm import router as trm_router
from .conceptos_flujo_caja import router as conceptos_flujo_caja_router
from .transacciones_flujo_caja import router as transacciones_flujo_caja_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(companies_router)
api_router.include_router(cuentas_bancarias_router)
api_router.include_router(trm_router, prefix="/trm", tags=["TRM"])
api_router.include_router(conceptos_flujo_caja_router)
api_router.include_router(transacciones_flujo_caja_router)