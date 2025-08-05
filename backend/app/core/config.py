from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import os

class Settings(BaseSettings):
    # Información del proyecto
    PROJECT_NAME: str = "Flujo de Caja API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "flujo_caja"
    
    # URL de conexión a MySQL
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_muy_segura_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - manejar como string y convertir a lista
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Convertir string de CORS origins a lista"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS
    
    # Configuración adicional
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()
