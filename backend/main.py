"""
Sistema de Flujo de Caja - FastAPI Backend
Aplicación principal que configura y ejecuta el servidor FastAPI
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import auth, usuarios, categorias, transacciones, reportes, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando Sistema de Flujo de Caja...")
    
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de datos inicializada")
    yield
    
    # Shutdown
    print("🔄 Cerrando conexiones...")


# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema de Flujo de Caja API",
    description="""
    API REST para el sistema de flujo de caja que digitaliza y automatiza 
    los cuadros de flujo tradicionalmente manejados en Excel.
    
    ## Características principales:
    * **Autenticación JWT** con roles diferenciados
    * **CRUD completo** para transacciones, categorías y usuarios  
    * **Cálculos automáticos** de saldos y flujos diarios
    * **Importación/Exportación** de archivos Excel
    * **Reportes avanzados** con filtros personalizables
    * **Dashboard ejecutivo** con métricas en tiempo real
    
    ## Roles de usuario:
    * **Tesorería**: Acceso completo al sistema
    * **Pagaduría**: Solo egresos (nómina, proveedores)
    * **Mesa de Dinero**: Solo consulta y reportes
    """,
    version="1.0.0",
    contact={
        "name": "Equipo Desarrollo",
        "email": "desarrollo@flujocaja.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["🔐 Autenticación"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["👥 Usuarios"])
app.include_router(categorias.router, prefix="/api/categorias", tags=["📂 Categorías"])
app.include_router(transacciones.router, prefix="/api/transacciones", tags=["💰 Transacciones"])
app.include_router(reportes.router, prefix="/api/reportes", tags=["📊 Reportes"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["📈 Dashboard"])


@app.get("/", tags=["🏠 Inicio"])
async def root():
    """Endpoint raíz que retorna información básica del sistema"""
    return {
        "mensaje": "🏦 Sistema de Flujo de Caja API",
        "version": "1.0.0",
        "estado": "✅ Operativo",
        "documentacion": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["🔍 Salud"])
async def health_check():
    """Endpoint de verificación de salud del sistema"""
    return {
        "estado": "saludable",
        "timestamp": "2025-01-14",
        "version": "1.0.0",
        "base_datos": "conectada",
        "servicios": {
            "api": "activo",
            "auth": "activo", 
            "reportes": "activo"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
