#!/usr/bin/env python3
"""
Script para recrear TODOS los conceptos de tesorería según Excel completo
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

# TODOS los conceptos de TESORERÍA según Excel completo
CONCEPTOS_TESORERIA_COMPLETOS = [
    # PAGADURÍA (conceptos iniciales)
    {"codigo": "", "nombre": "SALDO INICIAL", "tipo": "neutral"},
    {"codigo": "", "nombre": "CONSUMO", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTANILLA", "tipo": "egreso"},
    {"codigo": "", "nombre": "SALDO NETO INICIAL PAGADURÍA", "tipo": "neutral"},
    
    # RENTA FIJA
    {"codigo": "", "nombre": "PAGOS INTERCOMPAÑÍAS", "tipo": "egreso"},     # E
    {"codigo": "", "nombre": "COBROS INTERCOMPAÑÍAS", "tipo": "ingreso"},   # I (CORREGIDO)
    {"codigo": "", "nombre": "INGRESOS INTERESES", "tipo": "ingreso"},
    {"codigo": "", "nombre": "INGRESO REDENCIÓN TÍTULOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "APERTURA ACTIVO FINANCIERO", "tipo": "egreso"},
    {"codigo": "", "nombre": "CANCELACIÓN ACTIVO FINANCIERO", "tipo": "ingreso"},
    {"codigo": "", "nombre": "INTERESES ACTIVO FINANCIERO", "tipo": "ingreso"},
    {"codigo": "", "nombre": "CANCELACIÓN KW", "tipo": "egreso"},
    {"codigo": "", "nombre": "PAGO INTERESES KW", "tipo": "egreso"},
    {"codigo": "", "nombre": "APERTURA KW", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA TÍTULOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "COMPRA SIMULTÁNEA ACTIVA", "tipo": "egreso"},
    {"codigo": "", "nombre": "REDENCIÓN SIMULTÁNEA PASIVA", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA TÍTULOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA SIMULTÁNEA PASIVA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "REDENCIÓN SIMULTÁNEA ACTIVA", "tipo": "ingreso"},
    {"codigo": "", "nombre": "DISTRIBUCIÓN FCP", "tipo": "ingreso"},
    {"codigo": "", "nombre": "LLAMADO CAPITAL FCP", "tipo": "egreso"},
    {"codigo": "", "nombre": "RETIRO DE CAPITAL ENCARGOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "INCREMENTO DE CAPITAL ENCARGOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "TRASLADO ARL", "tipo": "neutral"},
    
    # RENTA VARIABLE
    {"codigo": "", "nombre": "COMPRA ACCIONES", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA ACCIONES", "tipo": "ingreso"},
    {"codigo": "", "nombre": "INGRESO DIVIDENDOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "EGRESO DIVIDENDOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "INGRESO DIVIDENDOS ETF", "tipo": "ingreso"},
    
    # DERIVADOS
    {"codigo": "", "nombre": "SWAP", "tipo": "neutral"},
    {"codigo": "", "nombre": "OPCIONES", "tipo": "egreso"},     # E
    {"codigo": "", "nombre": "OPCIONES", "tipo": "ingreso"},    # I (mismo nombre)
    {"codigo": "", "nombre": "FORWARD", "tipo": "egreso"},      # E
    {"codigo": "", "nombre": "FORWARD", "tipo": "ingreso"},     # I (mismo nombre)
    
    # DIVISAS
    {"codigo": "", "nombre": "COMPRA DIVISAS OTRAS ÁREAS", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTA DIVISAS OTRAS ÁREAS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "COMPRA DIVISAS REASEGUROS", "tipo": "egreso"},
    {"codigo": "", "nombre": "COMPRA DIVISAS COMPENSACIÓN", "tipo": "egreso"},
    {"codigo": "", "nombre": "VENTAS DIVISAS COMPENSACIÓN", "tipo": "ingreso"},
    
    # OTROS
    {"codigo": "", "nombre": "GARANTÍA SIMULTÁNEA", "tipo": "ingreso"},   # I
    {"codigo": "", "nombre": "GARANTÍA SIMULTÁNEA", "tipo": "egreso"},    # E (mismo nombre)
    {"codigo": "", "nombre": "EMBARGOS", "tipo": "neutral"},
    {"codigo": "", "nombre": "RECAUDO PRIMAS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "OTROS", "tipo": "neutral"},
    {"codigo": "", "nombre": "IMPUESTOS", "tipo": "egreso"},
    {"codigo": "", "nombre": "COMISIONES", "tipo": "egreso"},
    {"codigo": "", "nombre": "RENDIMIENTOS", "tipo": "ingreso"},
    {"codigo": "", "nombre": "GMF", "tipo": "egreso"},
    
    # FINALES
    {"codigo": "", "nombre": "SUB-TOTAL TESORERÍA", "tipo": "neutral"},
    {"codigo": "", "nombre": "SALDO FINAL CUENTAS", "tipo": "neutral"},
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
    print(f"🏗️ Creando {len(CONCEPTOS_TESORERIA_COMPLETOS)} conceptos de tesorería...")
    
    headers = obtener_headers()
    if not headers:
        print("❌ No se pudo obtener autenticación")
        return 0
    
    creados = 0
    for i, concepto in enumerate(CONCEPTOS_TESORERIA_COMPLETOS, 1):
        # Para conceptos con el mismo nombre pero diferente tipo, agregar sufijo al código
        codigo = concepto['codigo']
        if concepto['nombre'] in ["OPCIONES", "FORWARD", "GARANTÍA SIMULTÁNEA"]:
            codigo = f"{concepto['codigo']}_{concepto['tipo'][0].upper()}"  # _I o _E
        
        concepto_data = {
            "codigo": codigo,
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
    print("🔧 CREANDO CONCEPTOS COMPLETOS DE TESORERÍA")
    print("=" * 60)
    print("ℹ️ Este script creará los conceptos COMPLETOS del Excel (51 conceptos).")
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
        print(f"   - Total conceptos de tesorería: {len(CONCEPTOS_TESORERIA_COMPLETOS)}")
        print("   - Recarga el frontend para ver los cambios")
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")

if __name__ == "__main__":
    main()
