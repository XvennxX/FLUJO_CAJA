"""
Sistema de Flujo de Caja - FastAPI Backend (Versión Expandida)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Flujo de Caja",
    description="API para gestión de flujo de caja empresarial",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    tipo: str
    esta_activa: bool
    color: str

class TransaccionResponse(BaseModel):
    id: int
    fecha: date
    descripcion: str
    monto: float
    categoria_id: int
    categoria_nombre: str
    tipo: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    usuario: dict

# Datos demo
DEMO_CATEGORIAS = [
    {"id": 1, "nombre": "Ventas", "descripcion": "Ingresos por ventas", "tipo": "ingreso", "esta_activa": True, "color": "#10B981"},
    {"id": 2, "nombre": "Servicios", "descripcion": "Ingresos por servicios", "tipo": "ingreso", "esta_activa": True, "color": "#059669"},
    {"id": 3, "nombre": "Nómina", "descripcion": "Pagos de nómina", "tipo": "egreso", "esta_activa": True, "color": "#EF4444"},
    {"id": 4, "nombre": "Proveedores", "descripcion": "Pagos a proveedores", "tipo": "egreso", "esta_activa": True, "color": "#DC2626"},
    {"id": 5, "nombre": "Servicios Públicos", "descripcion": "Pago servicios públicos", "tipo": "egreso", "esta_activa": True, "color": "#B91C1C"},
]

DEMO_TRANSACCIONES = [
    {"id": 1, "fecha": "2025-01-15", "descripcion": "Venta productos", "monto": 5000000, "categoria_id": 1, "categoria_nombre": "Ventas", "tipo": "ingreso"},
    {"id": 2, "fecha": "2025-01-15", "descripcion": "Pago nómina enero", "monto": -3200000, "categoria_id": 3, "categoria_nombre": "Nómina", "tipo": "egreso"},
    {"id": 3, "fecha": "2025-01-16", "descripcion": "Servicios consultoría", "monto": 2500000, "categoria_id": 2, "categoria_nombre": "Servicios", "tipo": "ingreso"},
    {"id": 4, "fecha": "2025-01-16", "descripcion": "Compra materia prima", "monto": -1800000, "categoria_id": 4, "categoria_nombre": "Proveedores", "tipo": "egreso"},
]

DEMO_USUARIOS = {
    "tesoreria@empresa.com": {"password": "123456", "rol": "tesoreria", "nombre": "Usuario Tesorería"},
    "pagaduria@empresa.com": {"password": "123456", "rol": "pagaduria", "nombre": "Usuario Pagaduría"},
    "mesa@empresa.com": {"password": "123456", "rol": "mesa_dinero", "nombre": "Usuario Mesa de Dinero"},
}

# Ruta de prueba
@app.get("/")
async def root():
    return {
        "message": "Sistema de Flujo de Caja API", 
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/auth/login",
            "categorias": "/api/categorias",
            "transacciones": "/api/transacciones",
            "dashboard": "/api/dashboard/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "mysql", "timestamp": datetime.now()}

# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@app.post("/api/auth/login", response_model=LoginResponse, tags=["Autenticación"])
async def login(request: LoginRequest):
    """Endpoint para autenticación de usuarios"""
    if request.email not in DEMO_USUARIOS:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    usuario_data = DEMO_USUARIOS[request.email]
    if usuario_data["password"] != request.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return LoginResponse(
        token=f"demo_token_{request.email}",
        usuario={
            "email": request.email,
            "nombre": usuario_data["nombre"],
            "rol": usuario_data["rol"]
        }
    )

@app.get("/api/auth/me", tags=["Autenticación"])
async def get_current_user():
    """Obtener información del usuario actual"""
    return {
        "email": "tesoreria@empresa.com",
        "nombre": "Usuario Tesorería",
        "rol": "tesoreria"
    }

# ========== ENDPOINTS DE CATEGORÍAS ==========
@app.get("/api/categorias", response_model=List[CategoriaResponse], tags=["Categorías"])
async def get_categorias(tipo: Optional[str] = Query(None, description="Filtrar por tipo: 'ingreso' o 'egreso'")):
    """Obtener lista de categorías"""
    categorias = DEMO_CATEGORIAS.copy()
    if tipo:
        categorias = [c for c in categorias if c["tipo"] == tipo]
    return categorias

@app.get("/api/categorias/{categoria_id}", response_model=CategoriaResponse, tags=["Categorías"])
async def get_categoria(categoria_id: int):
    """Obtener una categoría específica"""
    categoria = next((c for c in DEMO_CATEGORIAS if c["id"] == categoria_id), None)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.post("/api/categorias", response_model=CategoriaResponse, tags=["Categorías"])
async def create_categoria(categoria: dict):
    """Crear una nueva categoría"""
    nueva_categoria = {
        "id": len(DEMO_CATEGORIAS) + 1,
        **categoria,
        "esta_activa": True
    }
    DEMO_CATEGORIAS.append(nueva_categoria)
    return nueva_categoria

# ========== ENDPOINTS DE TRANSACCIONES ==========
@app.get("/api/transacciones", response_model=List[TransaccionResponse], tags=["Transacciones"])
async def get_transacciones(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin"),
    categoria_id: Optional[int] = Query(None, description="ID de categoría"),
    tipo: Optional[str] = Query(None, description="Tipo: 'ingreso' o 'egreso'")
):
    """Obtener lista de transacciones con filtros"""
    transacciones = DEMO_TRANSACCIONES.copy()
    
    if fecha_inicio:
        transacciones = [t for t in transacciones if t["fecha"] >= fecha_inicio.isoformat()]
    if fecha_fin:
        transacciones = [t for t in transacciones if t["fecha"] <= fecha_fin.isoformat()]
    if categoria_id:
        transacciones = [t for t in transacciones if t["categoria_id"] == categoria_id]
    if tipo:
        transacciones = [t for t in transacciones if t["tipo"] == tipo]
    
    return transacciones

@app.get("/api/transacciones/{transaccion_id}", response_model=TransaccionResponse, tags=["Transacciones"])
async def get_transaccion(transaccion_id: int):
    """Obtener una transacción específica"""
    transaccion = next((t for t in DEMO_TRANSACCIONES if t["id"] == transaccion_id), None)
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@app.post("/api/transacciones", response_model=TransaccionResponse, tags=["Transacciones"])
async def create_transaccion(transaccion: dict):
    """Crear una nueva transacción"""
    nueva_transaccion = {
        "id": len(DEMO_TRANSACCIONES) + 1,
        **transaccion
    }
    DEMO_TRANSACCIONES.append(nueva_transaccion)
    return nueva_transaccion

@app.delete("/api/transacciones/{transaccion_id}", tags=["Transacciones"])
async def delete_transaccion(transaccion_id: int):
    """Eliminar una transacción"""
    global DEMO_TRANSACCIONES
    DEMO_TRANSACCIONES = [t for t in DEMO_TRANSACCIONES if t["id"] != transaccion_id]
    return {"message": "Transacción eliminada exitosamente"}

# ========== ENDPOINTS DE DASHBOARD ==========
@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Obtener estadísticas para el dashboard"""
    total_ingresos = sum(t["monto"] for t in DEMO_TRANSACCIONES if t["monto"] > 0)
    total_egresos = sum(abs(t["monto"]) for t in DEMO_TRANSACCIONES if t["monto"] < 0)
    flujo_neto = total_ingresos - total_egresos
    
    return {
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "flujo_neto": flujo_neto,
        "num_transacciones": len(DEMO_TRANSACCIONES),
        "saldo_actual": 25000000,  # Demo
        "periodo": "Enero 2025"
    }

@app.get("/api/dashboard/flujo-diario", tags=["Dashboard"])
async def get_flujo_diario():
    """Obtener flujo de caja diario para gráficos"""
    return [
        {"fecha": "2025-01-15", "ingresos": 7500000, "egresos": 3200000, "neto": 4300000},
        {"fecha": "2025-01-16", "ingresos": 2500000, "egresos": 1800000, "neto": 700000},
        {"fecha": "2025-01-17", "ingresos": 3200000, "egresos": 2100000, "neto": 1100000},
        {"fecha": "2025-01-18", "ingresos": 4800000, "egresos": 3500000, "neto": 1300000},
    ]

# ========== ENDPOINTS DE REPORTES ==========
@app.get("/api/reportes/categorias", tags=["Reportes"])
async def get_reporte_categorias():
    """Obtener reporte por categorías"""
    return [
        {"categoria": "Ventas", "total": 7500000, "porcentaje": 75.0, "tipo": "ingreso"},
        {"categoria": "Servicios", "total": 2500000, "porcentaje": 25.0, "tipo": "ingreso"},
        {"categoria": "Nómina", "total": 3200000, "porcentaje": 45.7, "tipo": "egreso"},
        {"categoria": "Proveedores", "total": 1800000, "porcentaje": 25.7, "tipo": "egreso"},
        {"categoria": "Servicios Públicos", "total": 2000000, "porcentaje": 28.6, "tipo": "egreso"},
    ]

@app.get("/api/flujo-mensual/{año}/{mes}", tags=["Flujo Mensual"])
async def get_flujo_mensual(año: int, mes: int):
    """Obtener flujo de caja mensual estilo Excel"""
    return {
        "año": año,
        "mes": mes,
        "saldo_inicial": 20000000,
        "saldo_final": 25000000,
        "dias": [
            {"dia": 1, "fecha": f"{año}-{mes:02d}-01", "ingresos": 0, "egresos": 0, "saldo": 20000000},
            {"dia": 15, "fecha": f"{año}-{mes:02d}-15", "ingresos": 7500000, "egresos": 3200000, "saldo": 24300000},
            {"dia": 16, "fecha": f"{año}-{mes:02d}-16", "ingresos": 2500000, "egresos": 1800000, "saldo": 25000000},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor FastAPI...")
    print("📍 URL del backend: http://localhost:8001")
    print("📋 Documentación API: http://localhost:8001/docs")
    print("🔧 Para detener el servidor presiona Ctrl+C")
    print("=" * 50)
    uvicorn.run(
        app, 
        host="127.0.0.1",  # Usar localhost directamente
        port=8001,
        log_level="info"
    )
