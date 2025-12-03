from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
import json
from typing import Callable
import asyncio

from ..core.database import get_db
from ..services.auditoria_service import AuditoriaService
from ..services.auth_service import get_current_user_from_token

class AuditoriaMiddleware:
    """
    Middleware para capturar automáticamente acciones de auditoría
    basadas en las requests HTTP al API
    """
    
    def __init__(self, app):
        self.app = app
        
        # Endpoints que requieren auditoría automática
        self.endpoints_auditoria = {
            # Flujo de Caja
            "/api/v1/transacciones-flujo-caja/guardar": {
                "modulo": "FLUJO_CAJA",
                "accion": "CREATE",
                "entidad": "Transacción"
            },
            "/api/v1/transacciones-flujo-caja/actualizar": {
                "modulo": "FLUJO_CAJA", 
                "accion": "UPDATE",
                "entidad": "Transacción"
            },
            "/api/v1/transacciones-flujo-caja/eliminar": {
                "modulo": "FLUJO_CAJA",
                "accion": "DELETE", 
                "entidad": "Transacción"
            },
            
            # Empresas
            "/api/v1/companies": {
                "modulo": "EMPRESAS",
                "accion_por_metodo": {
                    "POST": {"accion": "CREATE", "entidad": "Empresa"},
                    "PUT": {"accion": "UPDATE", "entidad": "Empresa"},
                    "DELETE": {"accion": "DELETE", "entidad": "Empresa"}
                }
            },
            
            # Cuentas Bancarias
            "/api/v1/bank-accounts": {
                "modulo": "CUENTAS",
                "accion_por_metodo": {
                    "POST": {"accion": "CREATE", "entidad": "Cuenta Bancaria"},
                    "PUT": {"accion": "UPDATE", "entidad": "Cuenta Bancaria"},
                    "DELETE": {"accion": "DELETE", "entidad": "Cuenta Bancaria"}
                }
            },
            
            # Usuarios
            "/api/v1/users": {
                "modulo": "USUARIOS",
                "accion_por_metodo": {
                    "POST": {"accion": "CREATE", "entidad": "Usuario"},
                    "PUT": {"accion": "UPDATE", "entidad": "Usuario"},
                    "DELETE": {"accion": "DELETE", "entidad": "Usuario"}
                }
            },
            
            # Reportes
            "/api/v1/reportes/exportar": {
                "modulo": "REPORTES",
                "accion": "EXPORT",
                "entidad": "Reporte"
            },
            
            # Conceptos
            "/api/v1/conceptos": {
                "modulo": "CONCEPTOS",
                "accion_por_metodo": {
                    "POST": {"accion": "CREATE", "entidad": "Concepto"},
                    "PUT": {"accion": "UPDATE", "entidad": "Concepto"},
                    "DELETE": {"accion": "DELETE", "entidad": "Concepto"}
                }
            }
        }
        
        # Endpoints que NO requieren auditoría (consultas, login, etc.)
        self.endpoints_excluir = [
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/me",
            "/api/v1/health",
            "/docs",
            "/openapi.json",
            "/api/v1/auditoria/"  # Evitar recursión infinita
        ]

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Marcar tiempo de inicio
        inicio = time.time()
        
        # Verificar si requiere auditoría
        requiere_auditoria = self._requiere_auditoria(request)
        usuario = None
        
        if requiere_auditoria:
            # Obtener usuario actual si está autenticado
            try:
                usuario = await self._obtener_usuario_actual(request)
            except:
                pass  # Si no puede obtener el usuario, continuar sin auditoría
        
        try:
            # Ejecutar la request
            response = await call_next(request)
            
            # Si requiere auditoría y tenemos usuario, registrar
            if requiere_auditoria and usuario and response.status_code < 400:
                await self._registrar_auditoria_exitosa(
                    request, response, usuario, time.time() - inicio
                )
            
            return response
            
        except Exception as e:
            # En caso de error, también registrar en auditoría
            if requiere_auditoria and usuario:
                await self._registrar_auditoria_error(
                    request, usuario, str(e), time.time() - inicio
                )
            
            # Re-lanzar la excepción
            raise e

    def _requiere_auditoria(self, request: Request) -> bool:
        """Determina si una request requiere auditoría"""
        
        path = request.url.path
        
        # Verificar exclusiones
        for exclusion in self.endpoints_excluir:
            if path.startswith(exclusion):
                return False
        
        # Verificar inclusiones explícitas
        for endpoint in self.endpoints_auditoria.keys():
            if path.startswith(endpoint) or path == endpoint:
                return True
        
        # Por defecto, auditar operaciones de modificación
        return request.method in ["POST", "PUT", "DELETE", "PATCH"]

    async def _obtener_usuario_actual(self, request: Request):
        """Obtiene el usuario actual desde el token de la request"""
        try:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization.split(" ")[1]
            
            # Usar sesión de DB
            db = next(get_db())
            try:
                usuario = get_current_user_from_token(token, db)
                return usuario
            finally:
                db.close()
                
        except Exception:
            return None

    async def _registrar_auditoria_exitosa(
        self, 
        request: Request, 
        response: Response, 
        usuario, 
        duracion: float
    ):
        """Registra una acción exitosa en auditoría"""
        
        try:
            path = request.url.path
            metodo = request.method
            
            # Obtener configuración de auditoría para este endpoint
            config = self._obtener_config_auditoria(path, metodo)
            if not config:
                return
            
            # Leer body de la request si existe
            body_data = await self._obtener_body_request(request)
            
            # Generar descripción
            descripcion = self._generar_descripcion(config, metodo, path, body_data)
            
            # Registrar en base de datos
            db = next(get_db())
            try:
                AuditoriaService.registrar_accion(
                    db=db,
                    usuario=usuario,
                    accion=config["accion"],
                    modulo=config["modulo"],
                    entidad=config["entidad"],
                    descripcion=descripcion,
                    request=request,
                    duracion_ms=int(duracion * 1000),
                    resultado="EXITOSO",
                    valores_nuevos=body_data if body_data else None
                )
            finally:
                db.close()
                
        except Exception as e:
            # Si falla la auditoría, no fallar la operación principal
            print(f"Error en auditoría: {e}")

    async def _registrar_auditoria_error(
        self, 
        request: Request, 
        usuario, 
        error_msg: str, 
        duracion: float
    ):
        """Registra un error en auditoría"""
        
        try:
            path = request.url.path
            metodo = request.method
            
            config = self._obtener_config_auditoria(path, metodo)
            if not config:
                return
            
            descripcion = f"Error en {config['entidad'].lower()}: {error_msg[:200]}"
            
            db = next(get_db())
            try:
                AuditoriaService.registrar_accion(
                    db=db,
                    usuario=usuario,
                    accion=config["accion"],
                    modulo=config["modulo"], 
                    entidad=config["entidad"],
                    descripcion=descripcion,
                    request=request,
                    duracion_ms=int(duracion * 1000),
                    resultado="ERROR",
                    mensaje_error=error_msg
                )
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error en auditoría de error: {e}")

    def _obtener_config_auditoria(self, path: str, metodo: str) -> dict:
        """Obtiene la configuración de auditoría para un endpoint"""
        
        for endpoint, config in self.endpoints_auditoria.items():
            if path.startswith(endpoint):
                # Si tiene configuración por método HTTP
                if "accion_por_metodo" in config:
                    metodo_config = config["accion_por_metodo"].get(metodo)
                    if metodo_config:
                        return {
                            "modulo": config["modulo"],
                            "accion": metodo_config["accion"],
                            "entidad": metodo_config["entidad"]
                        }
                else:
                    # Configuración directa
                    return config
        
        return None

    async def _obtener_body_request(self, request: Request) -> dict:
        """Obtiene el body de la request de forma segura"""
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                # Esta es una forma simplificada, en producción se necesitaría
                # manejar esto de forma más robusta
                return None  # Por simplicidad, no capturamos el body por ahora
            return None
        except:
            return None

    def _generar_descripcion(
        self, 
        config: dict, 
        metodo: str, 
        path: str, 
        body_data: dict = None
    ) -> str:
        """Genera una descripción legible de la acción"""
        
        accion_texto = {
            "CREATE": "creó",
            "UPDATE": "modificó", 
            "DELETE": "eliminó",
            "READ": "consultó",
            "EXPORT": "exportó",
            "IMPORT": "importó"
        }
        
        accion = accion_texto.get(config["accion"], config["accion"].lower())
        entidad = config["entidad"].lower()
        
        descripcion = f"Usuario {accion} {entidad}"
        
        # Añadir más contexto basado en el path
        if "flujo-caja" in path:
            descripcion += " en flujo de caja"
        elif "companies" in path:
            descripcion += " de empresa"
        elif "accounts" in path:
            descripcion += " bancaria"
        
        return descripcion