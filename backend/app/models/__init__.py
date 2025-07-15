"""
Modelos SQLAlchemy para el sistema de flujo de caja
"""

from app.core.database import Base

# Importar todos los modelos aquí para que SQLAlchemy los reconozca
from .usuario import Usuario
from .categoria import Categoria  
from .transaccion import Transaccion
from .mes_flujo import MesFlujo

__all__ = ["Base", "Usuario", "Categoria", "Transaccion", "MesFlujo"]
