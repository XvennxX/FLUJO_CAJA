"""
Configuración global del sistema de flujo de caja
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Información de la aplicación
    APP_NAME: str = "Sistema de Flujo de Caja"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos MySQL
    DATABASE_URL: str = "mysql+pymysql://flujo_user:flujo_pass_2025@localhost:3306/flujo_caja_db"
    
    # Seguridad JWT
    SECRET_KEY: str = "flujo_caja_secret_key_super_secure_2025_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Archivos y uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".csv"]
    
    # Redis (opcional)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email (para notificaciones)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Configuración de reportes
    REPORTS_DIR: str = "reports"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


# Configuraciones específicas por ambiente
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://flujo_user:flujo_pass_2025@localhost:5432/flujo_caja_dev"


class ProductionSettings(Settings):
    DEBUG: bool = False
    # En producción estas variables deben venir del environment
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")


def get_settings():
    """Factory para obtener configuración según el ambiente"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()
