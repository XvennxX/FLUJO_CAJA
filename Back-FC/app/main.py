from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from .core.config import get_settings
from .core.database import engine, Base, SessionLocal
from .api import api_router
from fastapi import UploadFile, File, Form
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
    allow_origins=settings.cors_allowed_origins,
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
    # Ejecutar verificación de TRM de forma síncrona para asegurar recuperación inmediata
    await verificar_trms_startup()
    
    # Iniciar scheduler de TRM en background
    asyncio.create_task(iniciar_scheduler_trm())

async def verificar_trms_startup():
    """Verificar TRMs faltantes en background al iniciar"""
    try:
        logger.info("=" * 70)
        logger.info("🔍 VERIFICANDO TRMs FALTANTES AL INICIAR SERVIDOR")
        logger.info("=" * 70)
        
        from app.services.trm_service import trm_service
        
        # Verificar últimos 30 días
        logger.info("� Revisando últimos 30 días para TRMs faltantes...")
        resultado = trm_service.verificar_trms_faltantes(days_back=30)
        
        if resultado["success"]:
            logger.info("")
            logger.info("📊 RESUMEN DE RECUPERACIÓN DE TRMs:")
            logger.info(f"   - Fechas faltantes encontradas: {resultado['missing_count']}")
            logger.info(f"   - TRMs actualizadas exitosamente: {resultado['updated_count']}")
            logger.info(f"   - Actualizaciones fallidas: {resultado['failed_count']}")
            
            if resultado["updated_count"] > 0:
                logger.info(f"   🎉 Se recuperaron {resultado['updated_count']} TRMs faltantes")
            
            if resultado["errors"] and len(resultado["errors"]) > 0:
                logger.warning("")
                logger.warning("⚠️ Algunos TRMs no se pudieron obtener:")
                for error in resultado["errors"][:3]:
                    logger.warning(f"   - {error}")
        else:
            logger.error(f"❌ Error en verificación: {resultado.get('error', 'Error desconocido')}")
        
        logger.info("=" * 70)
        logger.info("✅ VERIFICACIÓN DE TRMs COMPLETADA")
        logger.info("=" * 70)
            
    except Exception as e:
        logger.error(f"❌ Error en verificación de TRMs: {e}")

async def iniciar_scheduler_trm():
    """Iniciar scheduler de TRM en background para ejecución diaria a las 7:00 PM"""
    try:
        import asyncio
        import schedule
        import time
        from datetime import date
        
        logger.info("=" * 70)
        logger.info("⏰ INICIANDO SCHEDULER TRM - Ejecución diaria a las 7:00 PM")
        logger.info("=" * 70)
        
        def job_trm_diaria():
            """Job que se ejecuta diariamente a las 7:00 PM"""
            try:
                logger.info("🌙 Ejecutando actualización TRM diaria - 7:00 PM")
                
                from app.services.trm_service import trm_service
                
                hoy = date.today()
                exito = trm_service.obtener_trm_fecha(hoy)
                
                if exito:
                    logger.info(f"✅ TRM actualizada exitosamente para {hoy}")
                    # Verificar fechas faltantes después de actualizar
                    resultado = trm_service.verificar_trms_faltantes(days_back=7)
                    if resultado["updated_count"] > 0:
                        logger.info(f"✅ Se recuperaron {resultado['updated_count']} TRMs adicionales")
                else:
                    logger.warning(f"⚠️ No se pudo obtener TRM para {hoy}")
                    
            except Exception as e:
                logger.error(f"❌ Error en job diario de TRM: {e}")
        
        # Programar ejecución diaria a las 7:00 PM
        schedule.every().day.at("19:00").do(job_trm_diaria)
        
        logger.info("✅ Scheduler TRM configurado correctamente")
        logger.info("   - Próxima ejecución: Hoy a las 7:00 PM (19:00)")
        logger.info("=" * 70)
        
        # Loop del scheduler en background
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Verificar cada minuto
            
    except Exception as e:
        logger.error(f"❌ Error iniciando scheduler de TRM: {e}")

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