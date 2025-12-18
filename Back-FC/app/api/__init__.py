from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .roles import router as roles_router
from .companies import router as companies_router
from .cuentas_bancarias import router as cuentas_bancarias_router
from .cuentas_multi_moneda import router as cuentas_multi_moneda_router
from .trm import router as trm_router
from .conceptos_flujo_caja import router as conceptos_flujo_caja_router
from .transacciones_flujo_caja import router as transacciones_flujo_caja_router
from .saldo_inicial import router as saldo_inicial_router
from .diferencia_saldos import router as diferencia_saldos_router
from .gmf_config import router as gmf_config_router
from .dias_habiles import router as dias_habiles_router
from .informes_consolidados import router as informes_consolidados_router
from .auditoria import router as auditoria_router
from .conciliacion_contable import router as conciliacion_contable_router
from .gmf import router as gmf_router
from .cuatro_por_mil import router as cuatro_por_mil_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router, prefix="/rbac", tags=["Roles y Permisos"])
api_router.include_router(companies_router)
api_router.include_router(cuentas_bancarias_router)
api_router.include_router(cuentas_multi_moneda_router)
api_router.include_router(trm_router, prefix="/trm", tags=["TRM"])
api_router.include_router(conceptos_flujo_caja_router)
api_router.include_router(transacciones_flujo_caja_router)
api_router.include_router(saldo_inicial_router, prefix="/saldo-inicial", tags=["Saldo Inicial"])
api_router.include_router(diferencia_saldos_router, prefix="/diferencia-saldos", tags=["Diferencia Saldos"])
api_router.include_router(gmf_config_router, prefix="/gmf-config", tags=["GMF Config"])
api_router.include_router(dias_habiles_router, prefix="/dias-habiles", tags=["Días Hábiles"])
api_router.include_router(informes_consolidados_router)
api_router.include_router(auditoria_router)
api_router.include_router(conciliacion_contable_router)
api_router.include_router(gmf_router, prefix="/gmf", tags=["GMF"])
api_router.include_router(cuatro_por_mil_router, prefix="/cuatro-por-mil", tags=["Cuatro Por Mil"])