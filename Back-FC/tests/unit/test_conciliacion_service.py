#!/usr/bin/env python3
"""
Test directo de la API de conciliación
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.services.conciliacion_contable_service import ConciliacionContableService
from datetime import date

def test_conciliacion():
    """Probar servicio de conciliación directamente"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("PROBANDO SERVICIO DE CONCILIACIÓN")
        print("=" * 60)
        
        fecha = date(2025, 11, 4)
        print(f"\nBuscando conciliación para fecha: {fecha}")
        
        # Probar el servicio directamente
        resultado = ConciliacionContableService.obtener_conciliacion_por_fecha(
            db=db,
            fecha=fecha
        )
        
        print(f"\n✅ Respuesta obtenida:")
        print(f"   Fecha: {resultado.fecha}")
        print(f"   Número de empresas: {len(resultado.empresas)}")
        
        if resultado.empresas:
            print(f"\n📋 DETALLE DE EMPRESAS:")
            for i, empresa in enumerate(resultado.empresas, 1):
                print(f"\n   {i}. {empresa.compania.nombre}")
                print(f"      ID: {empresa.id}")
                print(f"      Compañía ID: {empresa.compania_id}")
                print(f"      Pagaduría: ${empresa.total_pagaduria}")
                print(f"      Tesorería: ${empresa.total_tesoreria}")
                print(f"      Total: ${empresa.total_calculado}")
                print(f"      Centralizadora: {empresa.total_centralizadora}")
                print(f"      Diferencia: ${empresa.diferencia}")
                print(f"      Estado: {empresa.estado}")
        else:
            print("\n❌ No se encontraron empresas")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_conciliacion()
