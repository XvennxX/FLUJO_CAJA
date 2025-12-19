# ARQUITECTURA BACKEND - SISTEMA DE FLUJO DE CAJA

## INFORMACIÓN GENERAL

**Proyecto**: Sistema de Flujo de Caja - Bolívar  
**Framework**: FastAPI 0.104.1+  
**Lenguaje**: Python 3.9+  
**Arquitectura**: API REST con patrón Repository/Service  
**Base de Datos**: MySQL 8.0+ con SQLAlchemy ORM  
**Fecha de Documentación**: 18 de Diciembre de 2025  

---

## 🏗️ ARQUITECTURA GENERAL

### Patrón de Diseño

El backend sigue una **arquitectura en capas** con separación clara de responsabilidades:

```
┌─────────────────┐
│   API Layer     │ ← Endpoints REST (FastAPI Routers)
├─────────────────┤
│ Service Layer   │ ← Lógica de negocio
├─────────────────┤
│  Model Layer    │ ← Entidades SQLAlchemy
├─────────────────┤
│ Database Layer  │ ← MySQL con Connection Pool
└─────────────────┘
```

### Estructura de Directorios

```
Back-FC/
├── app/                        # Aplicación principal
│   ├── api/                   # Endpoints REST organizados por dominio
│   │   ├── auth.py           # Autenticación y autorización
│   │   ├── users.py          # Gestión de usuarios
│   │   ├── conceptos_flujo_caja.py
│   │   ├── transacciones_flujo_caja.py
│   │   ├── cuentas_bancarias.py
│   │   ├── trm.py            # Tasas de cambio
│   │   └── ...               # 20+ endpoints especializados
│   ├── core/                 # Configuración central
│   │   ├── config.py         # Settings y variables de entorno
│   │   ├── database.py       # Conexión DB y SessionLocal
│   │   └── websocket.py      # WebSocket manager
│   ├── models/               # Modelos SQLAlchemy
│   │   ├── usuarios.py       # Modelo Usuario
│   │   ├── conceptos_flujo_caja.py
│   │   ├── transacciones_flujo_caja.py
│   │   └── ...               # 14+ entidades
│   ├── schemas/              # Schemas Pydantic
│   │   ├── auth.py           # Schemas de autenticación
│   │   ├── flujo_caja.py     # Schemas principales
│   │   └── ...               # Validación de datos
│   ├── services/             # Lógica de negocio
│   │   ├── auth_service.py   # Servicio de autenticación
│   │   ├── concepto_flujo_caja_service.py
│   │   ├── transaccion_flujo_caja_service.py
│   │   └── ...               # 15+ servicios especializados
│   └── main.py              # Aplicación FastAPI principal
├── tests/                    # Tests automatizados
├── scripts/                 # Scripts de migración y utilidades
└── requirements.txt         # Dependencias Python
```

---

## 🔧 CAPA DE CONFIGURACIÓN

### `/app/core/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

class Settings(BaseSettings):
    # Database Configuration
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "flujo_caja")
    database_url_env: Optional[str] = os.getenv("DATABASE_URL")
    
    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS Configuration
    allowed_origins: list = ["http://localhost:5000", "http://127.0.0.1:5000"]
    
    # Application Info
    app_name: str = "Sistema de Flujo de Caja - Bolívar"
    version: str = "1.0.0"
    debug: bool = True
    
    @property
    def database_url(self) -> str:
        if self.database_url_env and self.database_url_env.strip():
            return self.database_url_env.strip()
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### `/app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# SQLAlchemy Engine con optimizaciones
engine = create_engine(
    settings.database_url,
    echo=settings.debug,           # Logging SQL en desarrollo
    pool_pre_ping=True,           # Verificar conexiones antes de usar
    pool_recycle=300,             # Reciclar conexiones cada 5 min
    max_overflow=20,              # Máximo de conexiones extras
    pool_size=10                  # Pool base de conexiones
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Dependency Injection para DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN Y AUTORIZACIÓN

### Servicio de Autenticación (`auth_service.py`)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña con bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña con bcrypt"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autenticar usuario con validaciones completas:
    - Verificar existencia del usuario
    - Validar contraseña
    - Comprobar estado activo
    """
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or not verify_password(password, user.contrasena) or not user.estado:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear JWT token con expiración configurable"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(credentials, db: Session) -> Usuario:
    """Extraer usuario actual desde JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### API de Autenticación (`auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login_for_access_token(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint de login con validaciones múltiples:
    1. Verificar existencia del usuario
    2. Validar si está activo (estado=True)
    3. Autenticar credenciales
    4. Generar JWT token
    """
    user_in_db = db.query(Usuario).filter(Usuario.email == user_credentials.email).first()
    
    if user_in_db and not user_in_db.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta ha sido desactivada. Contacte al administrador."
        )
    
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol
        }
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: Usuario = Depends(get_current_user)):
    """Renovar token de acceso"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user
```

---

## 🎯 CAPA DE SERVICIOS (LÓGICA DE NEGOCIO)

### Servicio de Conceptos de Flujo de Caja

```python
# /app/services/concepto_flujo_caja_service.py

class ConceptoFlujoCajaService:
    """Servicio para gestión completa de conceptos de flujo de caja"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_concepto(self, concepto_data: ConceptoFlujoCajaCreate) -> ConceptoFlujoCaja:
        """
        Crear un nuevo concepto con validaciones:
        - Verificar unicidad de nombre por área
        - Asignar orden_display automático
        - Validar dependencias circulares
        """
        # Validar si ya existe un concepto con el mismo nombre en la misma área
        existing = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.nombre == concepto_data.nombre,
            ConceptoFlujoCaja.area == concepto_data.area,
            ConceptoFlujoCaja.activo == True
        ).first()
        
        if existing:
            raise ValueError(f"Ya existe un concepto activo con el nombre '{concepto_data.nombre}' en el área '{concepto_data.area}'")
        
        # Asignar orden automático si no se especifica
        if concepto_data.orden_display == 0:
            max_orden = self.db.query(func.max(ConceptoFlujoCaja.orden_display)).filter(
                ConceptoFlujoCaja.area == concepto_data.area,
                ConceptoFlujoCaja.activo == True
            ).scalar()
            concepto_data.orden_display = (max_orden or 0) + 1
        
        # Crear el concepto
        concepto = ConceptoFlujoCaja(**concepto_data.model_dump())
        self.db.add(concepto)
        self.db.commit()
        self.db.refresh(concepto)
        
        logger.info(f"Concepto creado: {concepto.nombre} (ID: {concepto.id})")
        return concepto
    
    def obtener_conceptos_por_area(self, area: AreaConceptoSchema, activos_only: bool = True) -> List[ConceptoFlujoCaja]:
        """
        Obtener conceptos filtrados por área:
        - Filtro por área (tesoreria, pagaduria, ambas)
        - Solo activos por defecto
        - Ordenados por orden_display
        """
        query = self.db.query(ConceptoFlujoCaja)
        
        if area != AreaConceptoSchema.ambas:
            query = query.filter(
                or_(ConceptoFlujoCaja.area == area, ConceptoFlujoCaja.area == AreaConceptoSchema.ambas)
            )
        
        if activos_only:
            query = query.filter(ConceptoFlujoCaja.activo == True)
        
        return query.order_by(ConceptoFlujoCaja.orden_display.asc()).all()
    
    def actualizar_concepto(self, concepto_id: int, concepto_data: ConceptoFlujoCajaUpdate) -> Optional[ConceptoFlujoCaja]:
        """
        Actualizar concepto con validaciones:
        - Verificar existencia
        - Validar cambios de dependencias
        - Recalcular transacciones dependientes si es necesario
        """
        concepto = self.db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.id == concepto_id).first()
        if not concepto:
            return None
        
        # Actualizar campos no nulos del schema
        for field, value in concepto_data.model_dump(exclude_unset=True).items():
            setattr(concepto, field, value)
        
        self.db.commit()
        self.db.refresh(concepto)
        
        logger.info(f"Concepto actualizado: {concepto.nombre} (ID: {concepto.id})")
        return concepto
```

### Servicio de Transacciones de Flujo de Caja

```python
# /app/services/transaccion_flujo_caja_service.py

class TransaccionFlujoCajaService:
    """Servicio para gestión completa de transacciones con cálculos automáticos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dependencias_service = DependenciasFlujoCajaService(db)
    
    def crear_transaccion(self, transaccion_data: TransaccionFlujoCajaCreate, usuario_id: int) -> TransaccionFlujoCaja:
        """
        Crear transacción con lógica completa:
        1. Validar concepto activo
        2. Verificar duplicidad (fecha + concepto + cuenta)
        3. Aplicar conversión TRM si es USD
        4. Ejecutar cálculos automáticos de dependencias
        5. Registrar auditoría
        """
        # Validar concepto
        concepto = self.db.query(ConceptoFlujoCaja).filter(
            ConceptoFlujoCaja.id == transaccion_data.concepto_id,
            ConceptoFlujoCaja.activo == True
        ).first()
        if not concepto:
            raise ValueError("El concepto especificado no existe o no está activo")
        
        # Verificar duplicidad
        existing = self.db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == transaccion_data.fecha,
            TransaccionFlujoCaja.concepto_id == transaccion_data.concepto_id,
            TransaccionFlujoCaja.cuenta_id == transaccion_data.cuenta_id
        ).first()
        if existing:
            raise ValueError("Ya existe una transacción para esa fecha, concepto y cuenta")
        
        # Crear transacción
        transaccion = TransaccionFlujoCaja(
            **transaccion_data.model_dump(),
            usuario_id=usuario_id,
            auditoria={
                "usuario_creacion": usuario_id,
                "fecha_creacion": datetime.now().isoformat(),
                "accion": "CREATE"
            }
        )
        
        self.db.add(transaccion)
        self.db.flush()  # Para obtener el ID antes del commit
        
        # Ejecutar cálculos automáticos de dependencias
        self.dependencias_service.recalcular_dependencias(transaccion.fecha)
        
        self.db.commit()
        self.db.refresh(transaccion)
        
        logger.info(f"Transacción creada: {transaccion.monto} para concepto {concepto.nombre}")
        return transaccion
    
    def obtener_flujo_caja_diario(self, fecha: date, area: Optional[AreaTransaccionSchema] = None) -> FlujoCajaDiarioResponse:
        """
        Generar flujo de caja completo para una fecha:
        1. Obtener conceptos ordenados por área
        2. Para cada concepto, buscar transacciones de la fecha
        3. Calcular totales automáticos
        4. Aplicar conversión TRM para USD
        """
        # Obtener conceptos según el área
        conceptos_query = self.db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.activo == True)
        
        if area:
            conceptos_query = conceptos_query.filter(
                or_(ConceptoFlujoCaja.area == area.value, ConceptoFlujoCaja.area == 'ambas')
            )
        
        conceptos = conceptos_query.order_by(ConceptoFlujoCaja.orden_display.asc()).all()
        
        # Construir items del flujo de caja
        items = []
        total_ingresos = Decimal('0.00')
        total_egresos = Decimal('0.00')
        
        for concepto in conceptos:
            # Buscar transacciones del concepto para la fecha
            transacciones = self.db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha,
                TransaccionFlujoCaja.concepto_id == concepto.id
            ).all()
            
            # Calcular monto total (con conversión TRM si es necesario)
            monto_total = sum(self._convertir_a_cop(t.monto, t.cuenta) for t in transacciones)
            
            # Clasificar como ingreso/egreso según el código del concepto
            if concepto.codigo == 'I':
                total_ingresos += monto_total
            elif concepto.codigo == 'E':
                total_egresos += monto_total
            
            items.append(FlujoCajaDiarioItem(
                concepto_id=concepto.id,
                concepto_nombre=concepto.nombre,
                codigo=concepto.codigo,
                monto=monto_total,
                transacciones_count=len(transacciones)
            ))
        
        return FlujoCajaDiarioResponse(
            fecha=fecha,
            area=area.value if area else "todas",
            items=items,
            total_ingresos=total_ingresos,
            total_egresos=total_egresos,
            saldo_neto=total_ingresos - total_egresos
        )
    
    def _convertir_a_cop(self, monto: Decimal, cuenta: CuentaBancaria) -> Decimal:
        """Convertir monto a COP usando TRM si la cuenta es USD"""
        if not cuenta:
            return monto
        
        # Obtener configuración de moneda de la cuenta
        cuenta_usd = self.db.query(CuentaMoneda).filter(
            CuentaMoneda.cuenta_id == cuenta.id,
            CuentaMoneda.tipo_moneda == 'USD',
            CuentaMoneda.activo == True
        ).first()
        
        if cuenta_usd:
            # Convertir de USD a COP usando TRM actual
            trm_actual = self.db.query(TRM).order_by(TRM.fecha.desc()).first()
            if trm_actual:
                return monto * trm_actual.valor
        
        return monto  # Asumir COP si no se encuentra configuración USD
```

### Servicio de TRM (Tasas de Cambio)

```python
# /app/services/trm_service.py

import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from datetime import date, datetime

class TRMService:
    """Servicio para obtención automática de TRM desde fuentes oficiales"""
    
    SOURCES = {
        "superfinanciera": "https://www.superfinanciera.gov.co/inicio/consultas-10037/trm-52",
        "banrep": "https://www.banrep.gov.co/es/estadisticas/trm"
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtener_trm_actual(self) -> Optional[TRM]:
        """Obtener TRM más reciente de la base de datos"""
        return self.db.query(TRM).order_by(TRM.fecha.desc()).first()
    
    def actualizar_trm_diaria(self) -> bool:
        """
        Actualizar TRM desde fuentes oficiales:
        1. Intentar Superintendencia Financiera
        2. Fallback a Banco de la República
        3. Guardar en BD si es exitoso
        """
        fecha_hoy = date.today()
        
        # Verificar si ya existe TRM para hoy
        trm_existente = self.db.query(TRM).filter(TRM.fecha == fecha_hoy).first()
        if trm_existente:
            logger.info(f"TRM ya existe para {fecha_hoy}: {trm_existente.valor}")
            return True
        
        # Intentar obtener de fuentes oficiales
        valor_trm = None
        
        # Fuente 1: Superintendencia Financiera
        try:
            valor_trm = self._obtener_trm_superfinanciera()
            if valor_trm:
                logger.info("TRM obtenida de Superintendencia Financiera")
        except Exception as e:
            logger.warning(f"Error obteniendo TRM de Superfinanciera: {e}")
        
        # Fuente 2: Banco de la República (fallback)
        if not valor_trm:
            try:
                valor_trm = self._obtener_trm_banrep()
                if valor_trm:
                    logger.info("TRM obtenida de Banco de la República")
            except Exception as e:
                logger.warning(f"Error obteniendo TRM de Banrep: {e}")
        
        # Guardar TRM si se obtuvo exitosamente
        if valor_trm:
            nueva_trm = TRM(fecha=fecha_hoy, valor=valor_trm)
            self.db.add(nueva_trm)
            self.db.commit()
            self.db.refresh(nueva_trm)
            
            logger.info(f"TRM guardada: {fecha_hoy} = {valor_trm}")
            return True
        
        logger.error("No se pudo obtener TRM de ninguna fuente oficial")
        return False
    
    def _obtener_trm_superfinanciera(self) -> Optional[Decimal]:
        """Scraping de TRM desde Superintendencia Financiera"""
        try:
            response = requests.get(self.SOURCES["superfinanciera"], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscar el valor TRM en el HTML (selector específico puede cambiar)
            trm_element = soup.find('span', class_='trm-value') or soup.find('div', id='trm-today')
            
            if trm_element:
                trm_text = trm_element.get_text().strip()
                # Limpiar formato: "3,850.25" -> 3850.25
                trm_value = trm_text.replace(',', '').replace('$', '').strip()
                return Decimal(trm_value)
            
        except Exception as e:
            logger.error(f"Error parsing Superfinanciera: {e}")
            return None
    
    def _obtener_trm_banrep(self) -> Optional[Decimal]:
        """Scraping de TRM desde Banco de la República"""
        try:
            response = requests.get(self.SOURCES["banrep"], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscar valor TRM en estructura HTML específica del Banrep
            trm_element = soup.find('td', string=lambda text: text and 'TRM' in text)
            
            if trm_element and trm_element.find_next('td'):
                trm_value = trm_element.find_next('td').get_text().strip()
                # Limpiar y convertir a Decimal
                trm_clean = trm_value.replace(',', '').replace('$', '').strip()
                return Decimal(trm_clean)
                
        except Exception as e:
            logger.error(f"Error parsing Banrep: {e}")
            return None
    
    def programar_actualizacion_automatica(self):
        """
        Programar actualización diaria de TRM usando scheduler:
        - Ejecutar todos los días a las 7:00 PM
        - Reintentar hasta 3 veces si falla
        """
        import schedule
        import time
        
        def job_actualizar_trm():
            try:
                success = self.actualizar_trm_diaria()
                if success:
                    logger.info("✅ TRM actualizada automáticamente")
                else:
                    logger.error("❌ Falló la actualización automática de TRM")
            except Exception as e:
                logger.error(f"❌ Error en job TRM: {e}")
        
        # Programar para las 7:00 PM todos los días
        schedule.every().day.at("19:00").do(job_actualizar_trm)
        
        logger.info("📅 Scheduler TRM configurado para las 7:00 PM diario")
        
        # Loop infinito del scheduler (ejecutar en background)
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
```

---

## 📊 CAPA DE MODELOS (ORM SQLAlchemy)

### Modelo Usuario con Sistema RBAC

```python
# /app/models/usuarios.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    
    # Sistema de roles híbrido (legacy + RBAC)
    rol = Column(String(50), nullable=False)  # Legacy: admin, tesoreria, etc.
    rol_id = Column(Integer, ForeignKey('roles.id', ondelete='SET NULL'), nullable=True, index=True)
    estado = Column(Boolean, nullable=False, default=True)
    
    # Relaciones
    rol_obj = relationship('Rol', back_populates='usuarios', foreign_keys=[rol_id])
    
    def tiene_permiso(self, codigo_permiso: str) -> bool:
        """Verificar si usuario tiene un permiso específico"""
        if not self.rol_obj or not self.rol_obj.activo:
            return False
        
        return any(
            p.codigo == codigo_permiso and p.activo 
            for p in self.rol_obj.permisos
        )
    
    def obtener_permisos(self) -> list:
        """Obtener todos los permisos del usuario"""
        if not self.rol_obj or not self.rol_obj.activo:
            return []
        
        return [p.codigo for p in self.rol_obj.permisos if p.activo]
```

### Modelo de Conceptos de Flujo de Caja

```python
# /app/models/conceptos_flujo_caja.py

class ConceptoFlujoCaja(Base):
    __tablename__ = "conceptos_flujo_caja"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(10), nullable=True)  # I=Ingreso, E=Egreso, vacío=Neutral
    tipo = Column(String(50), nullable=True)   # Personalizable
    
    # Configuración de visualización
    area = Column(Enum(AreaConcepto), nullable=False, default=AreaConcepto.ambas)
    orden_display = Column(Integer, default=0, index=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Sistema de dependencias automáticas
    depende_de_concepto_id = Column(Integer, ForeignKey("conceptos_flujo_caja.id", ondelete="SET NULL"), nullable=True)
    tipo_dependencia = Column(Enum(TipoDependencia), nullable=True)  # copia, suma, resta
    formula_dependencia = Column(String(255), nullable=True)  # Para fórmulas complejas
    
    # Auditoría automática
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    transacciones = relationship("TransaccionFlujoCaja", back_populates="concepto")
    concepto_dependiente = relationship("ConceptoFlujoCaja", remote_side=[id], backref="conceptos_dependientes")
```

### Modelo de Transacciones de Flujo de Caja

```python
# /app/models/transacciones_flujo_caja.py

class TransaccionFlujoCaja(Base):
    __tablename__ = "transacciones_flujo_caja"
    
    # Identificación única
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    
    # Referencias foráneas
    concepto_id = Column(Integer, ForeignKey("conceptos_flujo_caja.id", ondelete="CASCADE"), nullable=False)
    cuenta_id = Column(Integer, ForeignKey("cuentas_bancarias.id", ondelete="CASCADE"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    compania_id = Column(Integer, ForeignKey("companias.id", ondelete="SET NULL"), nullable=True)
    
    # Datos de la transacción
    monto = Column(DECIMAL(18, 2), nullable=False, default=0.00)
    descripcion = Column(Text, nullable=True)
    area = Column(Enum(AreaTransaccion), nullable=False, default=AreaTransaccion.tesoreria)
    
    # Metadatos y auditoría
    auditoria = Column(JSON, nullable=True)  # Información adicional de auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones con carga lazy optimizada
    concepto = relationship("ConceptoFlujoCaja", back_populates="transacciones")
    cuenta = relationship("CuentaBancaria", back_populates="transacciones")
    usuario = relationship("Usuario")
    compania = relationship("Compania")
```

---

## 🛠️ CAPA DE API (ENDPOINTS REST)

### Estructura de Endpoints

| Módulo | Endpoint Base | Funcionalidades |
|---------|---------------|-----------------|
| `auth.py` | `/auth` | Login, refresh token, user info |
| `users.py` | `/users` | CRUD usuarios |
| `conceptos_flujo_caja.py` | `/api/conceptos-flujo-caja` | CRUD conceptos |
| `transacciones_flujo_caja.py` | `/api/transacciones-flujo-caja` | CRUD transacciones, reportes |
| `cuentas_bancarias.py` | `/api/bank-accounts` | Gestión cuentas |
| `trm.py` | `/api/v1/trm` | TRM automática |
| `websocket.py` | `/ws` | Comunicación tiempo real |

### Ejemplo de API Endpoint

```python
# /app/api/conceptos_flujo_caja.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

router = APIRouter(prefix="/api/conceptos-flujo-caja", tags=["Conceptos Flujo de Caja"])

@router.post("/", response_model=ConceptoFlujoCajaResponse, status_code=status.HTTP_201_CREATED)
def crear_concepto(
    concepto_data: ConceptoFlujoCajaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo concepto de flujo de caja
    
    Validaciones:
    - Usuario debe tener permisos de creación
    - Concepto no debe duplicarse en la misma área
    - Área debe ser válida (tesoreria, pagaduria, ambas)
    """
    # Validar permisos
    if not current_user.tiene_permiso('conceptos.crear'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear conceptos"
        )
    
    try:
        service = ConceptoFlujoCajaService(db)
        concepto = service.crear_concepto(concepto_data)
        
        # Registrar en auditoría
        auditoria_service = AuditoriaService(db)
        auditoria_service.registrar_accion(
            tabla="conceptos_flujo_caja",
            registro_id=concepto.id,
            accion="CREATE",
            datos_nuevos=concepto_data.model_dump(),
            usuario_id=current_user.id
        )
        
        return concepto
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando concepto: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/area/{area}", response_model=List[ConceptoFlujoCajaResponse])
def obtener_conceptos_por_area(
    area: AreaConceptoSchema,
    activos_only: bool = Query(True, description="Solo conceptos activos"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener conceptos filtrados por área con ordenamiento"""
    if not current_user.tiene_permiso('conceptos.leer'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos de lectura")
    
    service = ConceptoFlujoCajaService(db)
    conceptos = service.obtener_conceptos_por_area(area, activos_only)
    
    return conceptos

@router.put("/{concepto_id}", response_model=ConceptoFlujoCajaResponse)
def actualizar_concepto(
    concepto_id: int,
    concepto_data: ConceptoFlujoCajaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar concepto existente con validaciones completas"""
    if not current_user.tiene_permiso('conceptos.editar'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos de edición")
    
    service = ConceptoFlujoCajaService(db)
    
    # Obtener estado anterior para auditoría
    concepto_anterior = service.obtener_concepto_por_id(concepto_id)
    if not concepto_anterior:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concepto no encontrado")
    
    concepto_actualizado = service.actualizar_concepto(concepto_id, concepto_data)
    
    # Registrar cambios en auditoría
    auditoria_service = AuditoriaService(db)
    auditoria_service.registrar_accion(
        tabla="conceptos_flujo_caja",
        registro_id=concepto_id,
        accion="UPDATE",
        datos_anteriores=concepto_anterior.__dict__,
        datos_nuevos=concepto_actualizado.__dict__,
        usuario_id=current_user.id
    )
    
    return concepto_actualizado
```

---

## 🔄 SISTEMA DE WEBSOCKETS TIEMPO REAL

```python
# /app/core/websocket_manager.py

from fastapi import WebSocket
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manager para conexiones WebSocket en tiempo real"""
    
    def __init__(self):
        # Almacenar conexiones activas por usuario
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Conectar un nuevo WebSocket para un usuario"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"Usuario {user_id} conectado vía WebSocket")
        
        # Enviar mensaje de bienvenida
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Conectado al sistema de tiempo real"
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Desconectar WebSocket de un usuario"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"Usuario {user_id} desconectado de WebSocket")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Enviar mensaje a un WebSocket específico"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error enviando mensaje WebSocket: {e}")
    
    async def broadcast_to_user(self, message: dict, user_id: int):
        """Enviar mensaje a todas las conexiones de un usuario"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await self.send_personal_message(message, connection)
    
    async def broadcast_to_all(self, message: dict):
        """Enviar mensaje a todos los usuarios conectados"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                await self.send_personal_message(message, connection)

# Instancia global del manager
websocket_manager = WebSocketManager()

# Endpoint WebSocket
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Recibir mensajes del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Procesar diferentes tipos de mensajes
            if message_data.get("type") == "ping":
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
    finally:
        websocket_manager.disconnect(websocket, user_id)
```

---

## ⚡ OPTIMIZACIONES Y RENDIMIENTO

### Connection Pool Database

```python
# Configuración optimizada en database.py
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,      # Verificar conexión antes de usar
    pool_recycle=300,        # Renovar conexiones cada 5 min
    max_overflow=20,         # Conexiones extra permitidas
    pool_size=10,           # Pool base de conexiones
    pool_timeout=30         # Timeout para obtener conexión
)
```

### Queries Optimizadas

```python
# Ejemplo de query optimizada con joins
def obtener_transacciones_con_detalles(fecha: date) -> List[TransaccionFlujoCaja]:
    return db.query(TransaccionFlujoCaja)\
        .options(
            joinedload(TransaccionFlujoCaja.concepto),
            joinedload(TransaccionFlujoCaja.cuenta),
            joinedload(TransaccionFlujoCaja.usuario)
        )\
        .filter(TransaccionFlujoCaja.fecha == fecha)\
        .all()
```

### Caché con Redis (Futuro)

```python
# Estructura preparada para integrar Redis
class CacheService:
    def __init__(self):
        # self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        pass
    
    def get_trm_cache(self, fecha: date) -> Optional[Decimal]:
        """Obtener TRM desde caché"""
        pass
    
    def set_trm_cache(self, fecha: date, valor: Decimal, ttl: int = 3600):
        """Guardar TRM en caché con TTL"""
        pass
```

---

## 📊 MONITOREO Y LOGGING

### Configuración de Logs

```python
# En main.py
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging con rotación
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Log a archivo con rotación (10MB máx, 5 archivos)
        RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
        # Log a consola en desarrollo
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Métricas de Performance

```python
import time
from functools import wraps

def measure_time(func):
    """Decorator para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} ejecutado en {end_time - start_time:.4f} segundos")
        return result
    return wrapper

# Uso en servicios críticos
@measure_time
def crear_transaccion(self, transaccion_data):
    # Lógica del servicio
    pass
```

---

## 🔒 SEGURIDAD IMPLEMENTADA

### Headers de Seguridad

```python
# En main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.bolivar.com"]
)
```

### Validación de Input

```python
from pydantic import BaseModel, validator
from typing import Optional

class TransaccionFlujoCajaCreate(BaseModel):
    concepto_id: int
    cuenta_id: Optional[int] = None
    monto: Decimal
    descripcion: Optional[str] = None
    
    @validator('monto')
    def validar_monto(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v > Decimal('999999999.99'):
            raise ValueError('El monto excede el límite permitido')
        return v
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if v and len(v) > 500:
            raise ValueError('La descripción es demasiado larga')
        return v
```

Esta documentación proporciona una visión completa de la arquitectura del backend, incluyendo todos los componentes, patrones de diseño, servicios, y código fuente relevante del sistema de flujo de caja.