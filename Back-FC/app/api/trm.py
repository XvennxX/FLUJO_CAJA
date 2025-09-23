from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.trm import TRM
from pydantic import BaseModel

router = APIRouter()

# Schemas
class TRMCreate(BaseModel):
    fecha: date
    valor: Decimal

class TRMResponse(BaseModel):
    fecha: date
    valor: Decimal
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

# Endpoints
@router.get("/current", response_model=TRMResponse)
def get_current_trm(db: Session = Depends(get_db)):
    """Obtener la TRM más reciente"""
    trm = db.query(TRM).order_by(desc(TRM.fecha)).first()
    if not trm:
        raise HTTPException(status_code=404, detail="No se encontró información de TRM")
    return trm

@router.get("/by-date/{fecha}", response_model=TRMResponse)
def get_trm_by_date(fecha: date, db: Session = Depends(get_db)):
    """Obtener la TRM por fecha específica"""
    trm = db.query(TRM).filter(TRM.fecha == fecha).first()
    if not trm:
        raise HTTPException(status_code=404, detail=f"No se encontró TRM para la fecha {fecha}")
    return trm

@router.post("/verificar-faltantes")
def verificar_trms_faltantes(days_back: int = 7):
    """Verificar y actualizar TRMs faltantes"""
    try:
        import subprocess
        import sys
        import os
        
        # Ruta al script de actualización
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            'scripts', 'trm', 'update_missing_trm.py'
        )
        
        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail="Script de actualización no encontrado")
        
        # Ejecutar el script
        result = subprocess.run([
            sys.executable, script_path, str(days_back)
        ], capture_output=True, text=True, timeout=300)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "days_checked": days_back
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout ejecutando script de TRM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando TRMs: {str(e)}")

@router.post("/obtener-fecha/{fecha}")
def obtener_trm_fecha(fecha: date):
    """Obtener TRM para una fecha específica"""
    try:
        import subprocess
        import sys
        import os
        
        # Ruta al script de actualización
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            'scripts', 'trm', 'update_missing_trm.py'
        )
        
        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail="Script de actualización no encontrado")
        
        # Ejecutar el script con fecha específica
        result = subprocess.run([
            sys.executable, script_path, fecha.isoformat()
        ], capture_output=True, text=True, timeout=60)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "fecha": fecha.isoformat()
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout obteniendo TRM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo TRM: {str(e)}")

@router.get("/range", response_model=List[TRMResponse])
def get_trm_range(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Obtener rango de TRM"""
    query = db.query(TRM)
    
    if fecha_inicio:
        query = query.filter(TRM.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(TRM.fecha <= fecha_fin)
    
    trm_list = query.order_by(desc(TRM.fecha)).limit(limit).all()
    return trm_list

@router.post("/", response_model=TRMResponse)
def create_trm(trm_data: TRMCreate, db: Session = Depends(get_db)):
    """Crear o actualizar TRM"""
    # Verificar si ya existe TRM para esa fecha
    existing_trm = db.query(TRM).filter(TRM.fecha == trm_data.fecha).first()
    
    if existing_trm:
        # Actualizar valor existente
        existing_trm.valor = trm_data.valor
        db.commit()
        db.refresh(existing_trm)
        return existing_trm
    else:
        # Crear nuevo registro
        new_trm = TRM(
            fecha=trm_data.fecha,
            valor=trm_data.valor
        )
        db.add(new_trm)
        db.commit()
        db.refresh(new_trm)
        return new_trm

@router.delete("/{fecha}")
def delete_trm(fecha: date, db: Session = Depends(get_db)):
    """Eliminar TRM por fecha"""
    trm = db.query(TRM).filter(TRM.fecha == fecha).first()
    if not trm:
        raise HTTPException(status_code=404, detail=f"No se encontró TRM para la fecha {fecha}")
    
    db.delete(trm)
    db.commit()
    return {"message": f"TRM eliminada para la fecha {fecha}"}
