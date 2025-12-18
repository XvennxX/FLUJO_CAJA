from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class TipoCuenta(enum.Enum):
    CORRIENTE = "CORRIENTE"
    AHORROS = "AHORROS"

class CuentaBancaria(Base):
    __tablename__ = "cuentas_bancarias"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_cuenta = Column(String(50), nullable=False)
    compania_id = Column(Integer, ForeignKey("companias.id"), nullable=False)
    banco_id = Column(Integer, ForeignKey("bancos.id"), nullable=False)
    tipo_cuenta = Column(Enum(TipoCuenta), nullable=False, default=TipoCuenta.CORRIENTE)
    
    # Relaciones
    compania = relationship("Compania", back_populates="cuentas_bancarias")
    banco = relationship("Banco", back_populates="cuentas_bancarias")
    transacciones = relationship("TransaccionFlujoCaja", back_populates="cuenta")
    monedas = relationship("CuentaMoneda", back_populates="cuenta", cascade="all, delete-orphan")
    gmf_configs = relationship("GMFConfig", back_populates="cuenta_bancaria", cascade="all, delete-orphan")
    cuatro_por_mil_configs = relationship("CuatroPorMilConfig", back_populates="cuenta_bancaria", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CuentaBancaria(id={self.id}, numero='{self.numero_cuenta}', tipo='{self.tipo_cuenta}')>"