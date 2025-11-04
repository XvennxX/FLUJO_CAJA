from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from .core.config import get_settings
from .core.database import engine, Base, SessionLocal
from .api import api_router
# from .api.auditoria import router as auditoria_router  # Ya incluido en api_router
# from .middleware.auditoria_middleware import AuditoriaMiddleware  # Comentado temporalmente

settings = get_settings()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API REST para el Sistema de Flujo de Caja de Bolívar",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de la API
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """Eventos que se ejecutan al iniciar el servidor"""
    logger.info("🚀 Iniciando servidor FastAPI...")
    
    # Verificar TRMs faltantes al iniciar (en background)
    import asyncio
    asyncio.create_task(verificar_trms_startup())

async def verificar_trms_startup():
    """Verificar TRMs faltantes en background al iniciar"""
    try:
        import subprocess
        import sys
        import os
        
        logger.info("🔍 Verificando TRMs faltantes en background...")
        
        # Ruta al script de actualización
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'scripts', 'trm', 'update_missing_trm.py'
        )
        
        if os.path.exists(script_path):
            # Ejecutar el script en background
            result = subprocess.run([
                sys.executable, script_path, "7"
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                logger.info("✅ Verificación de TRMs completada")
            else:
                logger.warning(f"⚠️ Error en verificación de TRMs: {result.stderr}")
        else:
            logger.warning("⚠️ Script de TRM no encontrado")
            
    except Exception as e:
        logger.error(f"❌ Error en verificación de TRMs: {e}")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Sistema de Flujo de Caja - API",
        "version": settings.version,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }

# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )