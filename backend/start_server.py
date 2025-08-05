#!/usr/bin/env python
"""
Script para iniciar el servidor FastAPI
"""
import sys
import os
from pathlib import Path

# Agregar el directorio Backend al PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
