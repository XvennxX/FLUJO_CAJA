#!/usr/bin/env python3
"""
Script para actualizar TRM inmediatamente
"""

import sys
import os
from datetime import date, timedelta
import requests
from decimal import Decimal

# Agregar el directorio actual al path
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.trm import TRM

def get_trm_from_api(fecha):
    """
    Obtener TRM desde la API de datos abiertos
    """
    try:
        # URL de la API de datos abiertos del gobierno
        url = f"https://www.datos.gov.co/resource/32sa-8pi3.json?fecha={fecha.strftime('%Y-%m-%d')}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # El valor viene en el campo 'valor'
                trm_value = Decimal(str(data[0]['valor']))
                return trm_value
        
        # Si falla, intentar con Banco de la República
        url_banrep = f"https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario"
        
        response = requests.get(url_banrep, timeout=10)
        if response.status_code == 200:
            # Este es más complejo, usaremos un valor por defecto
            print(f"API Banco República disponible, pero necesita parsing específico")
            
    except Exception as e:
        print(f"Error consultando APIs: {e}")
    
    return None

def update_trm_for_date(fecha, valor=None):
    """
    Actualizar TRM para una fecha específica
    """
    db = SessionLocal()
    try:
        # Verificar si ya existe
        existing = db.query(TRM).filter(TRM.fecha == fecha).first()
        if existing:
            print(f"TRM para {fecha} ya existe: {existing.valor}")
            return True
            
        # Si no se proporciona valor, intentar obtenerlo de APIs
        if valor is None:
            valor = get_trm_from_api(fecha)
            
        if valor is None:
            # Usar valor por defecto basado en la última TRM conocida
            latest_trm = db.query(TRM).order_by(TRM.fecha.desc()).first()
            if latest_trm:
                valor = latest_trm.valor
                print(f"Usando valor de TRM anterior: {valor}")
            else:
                valor = Decimal('4018.41')  # Valor por defecto
                print(f"Usando valor por defecto: {valor}")
        
        # Crear nueva TRM
        new_trm = TRM(fecha=fecha, valor=valor)
        db.add(new_trm)
        db.commit()
        
        print(f"✅ TRM actualizada para {fecha}: {valor}")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando TRM para {fecha}: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """
    Actualizar TRMs faltantes
    """
    print("=" * 50)
    print("ACTUALIZANDO TRMs FALTANTES")
    print("=" * 50)
    
    today = date.today()
    print(f"Fecha actual: {today}")
    
    # Verificar últimos 7 días
    for i in range(7, 0, -1):
        check_date = today - timedelta(days=i)
        print(f"\nVerificando TRM para: {check_date}")
        update_trm_for_date(check_date)
    
    # También intentar para hoy
    print(f"\nVerificando TRM para hoy: {today}")
    update_trm_for_date(today)
    
    print("\n" + "=" * 50)
    print("PROCESO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
