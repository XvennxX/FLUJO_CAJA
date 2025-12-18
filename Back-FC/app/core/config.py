from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "flujo_caja")
    database_url_env: Optional[str] = os.getenv("DATABASE_URL")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hora para coincidir con frontend
    
    # CORS
    # Permitir configurar orígenes por variable de entorno separada por comas
    allowed_origins: list = ["http://localhost:5000", "http://127.0.0.1:5000"]
    
    # App
    app_name: str = "Sistema de Flujo de Caja - Bolívar"
    version: str = "1.0.0"
    debug: bool = True
    
    @property
    def database_url(self) -> str:
        # Priorizar DATABASE_URL si está presente (debe ser MySQL en este proyecto)
        if self.database_url_env and self.database_url_env.strip():
            return self.database_url_env.strip()
        # Fallback: construir URL MySQL a partir de variables por partes
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def cors_allowed_origins(self) -> List[str]:
        env_val = os.getenv("ALLOWED_ORIGINS")
        if env_val:
            # Soportar lista separada por comas y espacios
            return [o.strip() for o in env_val.split(",") if o.strip()]
        return self.allowed_origins
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()