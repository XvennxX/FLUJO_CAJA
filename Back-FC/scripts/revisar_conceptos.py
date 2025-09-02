#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para revisar y crear conceptos de flujo de caja correctos
"""

import requests
import json

BASE_URL = "http://localhost:8000"

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

def revisar_conceptos_actuales(token):
    """Revisar conceptos actuales en la base de datos"""
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(f'{BASE_URL}/api/v1/api/conceptos-flujo-caja/', headers=headers)
    
    if response.status_code == 200:
        conceptos = response.json()
        print(f"📋 CONCEPTOS ACTUALES EN BD: {len(conceptos)}")
        print("=" * 60)
        
        # Agrupar por área
        tesoreria = [c for c in conceptos if c['area'] == 'tesoreria']
        pagaduria = [c for c in conceptos if c['area'] == 'pagaduria']
        ambas = [c for c in conceptos if c['area'] == 'ambas']
        
        print(f"🏦 TESORERÍA ({len(tesoreria)}):")
        for c in tesoreria[:5]:  # Solo los primeros 5
            tipo = c.get('tipo_movimiento', c.get('tipo', 'N/A'))
            print(f"   - {c['nombre']} ({tipo})")
        if len(tesoreria) > 5:
            print(f"   ... y {len(tesoreria) - 5} más")
            
        print(f"💰 PAGADURÍA ({len(pagaduria)}):")
        for c in pagaduria[:5]:  # Solo los primeros 5
            tipo = c.get('tipo_movimiento', c.get('tipo', 'N/A'))
            print(f"   - {c['nombre']} ({tipo})")
        if len(pagaduria) > 5:
            print(f"   ... y {len(pagaduria) - 5} más")
            
        print(f"🔄 AMBAS ({len(ambas)}):")
        for c in ambas:
            tipo = c.get('tipo_movimiento', c.get('tipo', 'N/A'))
            print(f"   - {c['nombre']} ({tipo})")
            
        # Mostrar estructura de un concepto para debug
        if conceptos:
            print(f"\n🔍 ESTRUCTURA DE EJEMPLO:")
            print(f"   Campos disponibles: {list(conceptos[0].keys())}")
            print(f"   Ejemplo: {json.dumps(conceptos[0], indent=2, ensure_ascii=False)[:200]}...")
            
        return conceptos
    else:
        print(f"❌ Error obteniendo conceptos: {response.text}")
        return []

def main():
    print("🔍 REVISANDO CONCEPTOS ACTUALES EN LA BASE DE DATOS")
    print("=" * 60)
    
    token = get_admin_token()
    if not token:
        return
        
    conceptos = revisar_conceptos_actuales(token)
    
    print(f"\n📝 RESUMEN:")
    print(f"   Total conceptos: {len(conceptos)}")
    print(f"   ¿Necesitas crear conceptos específicos para Pagaduría?")
    print(f"   ¿Los conceptos actuales coinciden con tu Excel?")

if __name__ == "__main__":
    main()
