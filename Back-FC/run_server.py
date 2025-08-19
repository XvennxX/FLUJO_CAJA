#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo
"""

import uvicorn
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI...")
    print("📊 Dashboard disponible en: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000/api/v1")
    print("⏹️  Presiona Ctrl+C para detener el servidor")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
