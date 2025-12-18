#!/usr/bin/env python3
"""Script para crear índice en gmf_config"""
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
try:
    db.execute(text("""
        CREATE INDEX idx_gmf_config_cuenta_fecha_vigencia 
        ON gmf_config(cuenta_bancaria_id, fecha_vigencia_desde DESC)
    """))
    db.commit()
    print("✅ Índice creado exitosamente")
except Exception as e:
    if '1061' in str(e):  # Duplicate key name
        print("✅ Índice ya existe")
    else:
        print(f"⚠️ Error: {e}")
finally:
    db.close()
