#!/usr/bin/env python3
"""
Script para recrear los conceptos de tesorería según Excel
Elimina todos los conceptos de tesorería existentes y crea los correctos
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def obtener_token():
    """Obtiene un token de autenticación"""
    login_data = {
        "email": "carlos.gomez@flujo.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def obtener_headers():
    """Obtiene headers con autorización"""
    token = obtener_token()
    if not token:
        return None
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# Conceptos específicos de TESORERÍA según Excel
CONCEPTOS_TESORERIA = [
    {"codigo": "", "nombre": "SALDO INICIAL", "tipo": "neutral"},
    {"codigo": "", "nombre": "CONSUMO", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTANILLA", "tipo": "egreso"},
    {"codigo": "", "nombre": "SALDO NETO INICIAL PAGADURÍA", "tipo": "neutral"},
    {"codigo": "", "nombre": "PAGOS INTERCOMPAÑÍAS", "tipo": "egreso"},
    {"codigo": "", "nombre": "COBROS INTERCOMPAÑÍAS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DÓLARES BANAGRÍCOLA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DÓLARES BANAGRÍCOLA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DÓLARES DAVIVIENDA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DÓLARES DAVIVIENDA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DÓLARES BANCOLOMBIA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DÓLARES BANCOLOMBIA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DÓLARES BANCO POPULAR", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DÓLARES BANCO POPULAR", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DÓLARES OTROS BANCOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DÓLARES OTROS BANCOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA EUROS BANAGRÍCOLA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA EUROS BANAGRÍCOLA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA EUROS DAVIVIENDA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA EUROS DAVIVIENDA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA EUROS BANCOLOMBIA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA EUROS BANCOLOMBIA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA EUROS BANCO POPULAR", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA EUROS BANCO POPULAR", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA EUROS OTROS BANCOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA EUROS OTROS BANCOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "RENDIMIENTOS FINANCIEROS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "DIFERENCIA EN CAMBIO", "tipo": "neutral"},
    {"codigo": "", "nombre": "SALDO FINAL", "tipo": "neutral"},
]

def eliminar_conceptos_tesoreria():
    """Elimina todos los conceptos de tesorería existentes"""
    try:
        headers = obtener_headers()
        if not headers:
            print("❌ No se pudo obtener autenticación")
            return 0
            
        # Obtener conceptos de tesorería
        response = requests.get(f"{BASE_URL}/api/v1/api/conceptos-flujo-caja/?area=tesoreria", headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo conceptos: {response.status_code}")
            return 0
            
        conceptos = response.json()
        
        print(f"🗑️ Eliminando {len(conceptos)} conceptos de tesorería existentes...")
        
        eliminados = 0
        for concepto in conceptos:
            delete_response = requests.delete(f"{BASE_URL}/api/v1/api/conceptos-flujo-caja/{concepto['id']}", headers=headers)
            if delete_response.status_code == 200:
                print(f"   ✅ Eliminado: {concepto['nombre']}")
                eliminados += 1
            else:
                print(f"   ❌ Error eliminando: {concepto['nombre']} - {delete_response.status_code}")
        
        return eliminados
    except Exception as e:
        print(f"❌ Error eliminando conceptos: {e}")
        return 0

def crear_conceptos_tesoreria():
    """Crea los conceptos de tesorería según Excel"""
    print(f"🏗️ Creando {len(CONCEPTOS_TESORERIA)} conceptos de tesorería...")
    
    headers = obtener_headers()
    if not headers:
        print("❌ No se pudo obtener autenticación")
        return 0
    
    creados = 0
    for i, concepto in enumerate(CONCEPTOS_TESORERIA, 1):
        concepto_data = {
            "codigo": concepto['codigo'],
            "nombre": concepto['nombre'],
            "area": "tesoreria",
            "tipo": concepto['tipo'],
            "activo": True,
            "orden_display": i,
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/api/conceptos-flujo-caja/",
                json=concepto_data,
                headers=headers
            )
            
            if response.status_code == 201:
                print(f"   ✅ Creado: {concepto['nombre']} ({concepto['tipo']})")
                creados += 1
            else:
                print(f"   ❌ Error creando {concepto['nombre']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creando {concepto['nombre']}: {e}")
    
    return creados

def main():
    print("🔧 CREANDO CONCEPTOS ESPECÍFICOS DE TESORERÍA")
    print("=" * 60)
    print("ℹ️ Este script creará los conceptos específicos del Excel.")
    print()
    
    respuesta = input("¿Continuar? (s/N): ").lower().strip()
    if respuesta != 's':
        print("❌ Operación cancelada")
        return
    
    try:
        # Solo crear nuevos conceptos (ya eliminaste manualmente)
        creados = crear_conceptos_tesoreria()
        
        print()
        print("✅ PROCESO COMPLETADO")
        print(f"   - Conceptos creados: {creados}")
        print(f"   - Total conceptos de tesorería: {len(CONCEPTOS_TESORERIA)}")
        print("   - Recarga el frontend para ver los cambios")
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")

if __name__ == "__main__":
    main()
