#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear conceptos específicos de Pagaduría según el Excel
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Conceptos exactos del Excel para Pagaduría
CONCEPTOS_PAGADURIA = [
    { 'codigo': '', 'nombre': 'DIFERENCIA SALDOS', 'tipo': 'neutral' },
    { 'codigo': '', 'nombre': 'SALDOS EN BANCOS', 'tipo': 'neutral' },
    { 'codigo': 'I', 'nombre': 'SALDO DIA ANTERIOR', 'tipo': 'ingreso' },
    { 'codigo': 'I', 'nombre': 'INGRESO', 'tipo': 'ingreso' },
    { 'codigo': 'E', 'nombre': 'EGRESO', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'CONSUMO NACIONAL', 'tipo': 'egreso' },
    { 'codigo': 'I', 'nombre': 'INGRESO CTA PAGADURIA', 'tipo': 'ingreso' },
    { 'codigo': 'I', 'nombre': 'FINANSEGUROS', 'tipo': 'ingreso' },
    { 'codigo': 'I', 'nombre': 'RECAUDOS LIBERTADOR', 'tipo': 'ingreso' },
    { 'codigo': 'I', 'nombre': 'RENDIMIENTOS FINANCIEROS', 'tipo': 'ingreso' },
    { 'codigo': 'I', 'nombre': 'INGRESOS REASEGUROS', 'tipo': 'ingreso' },
    { 'codigo': 'E', 'nombre': 'EGR. REASEGUROS', 'tipo': 'egreso' },
    { 'codigo': 'I', 'nombre': 'ING. COMPRA DE DIVISAS-REASEGUR', 'tipo': 'ingreso' },
    { 'codigo': 'E', 'nombre': 'EGR. VENTA DIVISAS-REASEGUROS', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'EGRESO - TRASLADOS COMPAÑÍAS', 'tipo': 'egreso' },
    { 'codigo': 'I', 'nombre': 'INGRESO - TRASLADOS COMPAÑÍAS', 'tipo': 'ingreso' },
    { 'codigo': 'E', 'nombre': 'EMBARGOS', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'OTROS PAGOS', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'VENTAN PROVEEDORES', 'tipo': 'egreso' },
    { 'codigo': '', 'nombre': 'INTERCIAS RELAC./INDUS', 'tipo': 'neutral' },
    { 'codigo': 'E', 'nombre': 'COMISIONES DAVIVIENDA', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'NOMINA CONSEJEROS', 'tipo': 'egreso' },
    { 'codigo': '', 'nombre': 'NOMINA ADMINISTRATIVA', 'tipo': 'neutral' },
    { 'codigo': '', 'nombre': 'NOMINA PENSIONES', 'tipo': 'neutral' },
    { 'codigo': 'E', 'nombre': 'PAGO SOI', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'PAGO IVA', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'OTROS IMPTOS', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'EGRESO DIVIDENDOS', 'tipo': 'egreso' },
    { 'codigo': 'E', 'nombre': 'CUATRO POR MIL', 'tipo': 'egreso' },
    { 'codigo': '', 'nombre': 'DIFERENCIA EN CAMBIO CTAS REASEGUROS', 'tipo': 'neutral' }
]

def get_admin_token():
    """Obtener token de administrador"""
    login_data = {
        'email': 'carlos.gomez@flujo.com',
        'password': 'admin123'
    }
    
    response = requests.post(f'{BASE_URL}/api/v1/auth/login', json=login_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"❌ Error login admin: {response.text}")
        return None

def limpiar_conceptos_pagaduria(token):
    """Eliminar todos los conceptos de pagaduría existentes"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # Obtener conceptos de pagaduría
    response = requests.get(f'{BASE_URL}/api/v1/api/conceptos-flujo-caja/por-area/pagaduria', headers=headers)
    
    if response.status_code == 200:
        conceptos = response.json()
        print(f"🗑️ Eliminando {len(conceptos)} conceptos de pagaduría existentes...")
        
        for concepto in conceptos:
            delete_response = requests.delete(
                f'{BASE_URL}/api/v1/api/conceptos-flujo-caja/{concepto["id"]}',
                headers=headers
            )
            if delete_response.status_code == 200:
                print(f"   ✅ Eliminado: {concepto['nombre']}")
            else:
                print(f"   ❌ Error eliminando {concepto['nombre']}: {delete_response.text}")
    else:
        print(f"❌ Error obteniendo conceptos de pagaduría: {response.text}")

def crear_conceptos_pagaduria(token):
    """Crear los conceptos correctos de pagaduría"""
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"🏗️ Creando {len(CONCEPTOS_PAGADURIA)} conceptos de pagaduría...")
    
    for i, concepto in enumerate(CONCEPTOS_PAGADURIA, 1):
        concepto_data = {
            "codigo": concepto['codigo'],
            "nombre": concepto['nombre'],
            "area": "pagaduria",
            "tipo": concepto['tipo'],  # Usar 'tipo' en lugar de 'tipo_movimiento'
            "activo": True,
            "orden_display": i,  # Usar 'orden_display' en lugar de 'orden'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/v1/api/conceptos-flujo-caja/',
            json=concepto_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"   ✅ Creado: {concepto['nombre']} ({concepto['tipo']})")
        else:
            print(f"   ❌ Error creando {concepto['nombre']}: {response.text}")

def main():
    print("🔧 CREANDO CONCEPTOS ESPECÍFICOS DE PAGADURÍA")
    print("=" * 60)
    
    token = get_admin_token()
    if not token:
        return
    
    print("⚠️ ATENCIÓN: Este script eliminará TODOS los conceptos de pagaduría existentes")
    print("y creará los conceptos específicos del Excel.")
    print()
    respuesta = input("¿Continuar? (s/N): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        # Paso 1: Limpiar conceptos existentes
        limpiar_conceptos_pagaduria(token)
        
        # Paso 2: Crear conceptos correctos
        crear_conceptos_pagaduria(token)
        
        print(f"\n✅ PROCESO COMPLETADO")
        print(f"   - Conceptos de pagaduría recreados según Excel")
        print(f"   - Total: {len(CONCEPTOS_PAGADURIA)} conceptos")
        print(f"   - Recarga el frontend para ver los cambios")
    else:
        print("❌ Operación cancelada")

if __name__ == "__main__":
    main()
