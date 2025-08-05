from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
