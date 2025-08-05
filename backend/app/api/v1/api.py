from fastapi import APIRouter
from app.api.v1.endpoints import auth, usuarios, roles, ingresos, egresos, conceptos, cuentas, reportes, auditoria

api_router = APIRouter()

# Incluir todas las rutas
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(ingresos.router, prefix="/ingresos", tags=["Ingresos"])
api_router.include_router(egresos.router, prefix="/egresos", tags=["Egresos"])
api_router.include_router(conceptos.router, prefix="/conceptos", tags=["Conceptos"])
api_router.include_router(cuentas.router, prefix="/cuentas", tags=["Cuentas"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría"])
