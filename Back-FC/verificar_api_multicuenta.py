#!/usr/bin/env python3
"""
Script para verificar que los auto-cálculos funcionan correctamente 
para múltiples cuentas a través de la API
"""

import requests
import sys
import logging
from datetime import date

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def login():
    """Autenticarse en la API"""
    login_data = {
        "email": "maria.lopez@flujo.com",
        "password": "tesoreria123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return None

def verificar_transacciones_por_fecha(token, fecha="2025-09-09"):
    """Verificar transacciones por fecha y buscar auto-cálculos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/api/transacciones-flujo-caja/fecha/{fecha}", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"=== VERIFICACIÓN DE AUTO-CÁLCULOS PARA {fecha} ===")
        logger.info(f"Total transacciones: {len(data)}")
        
        # Agrupar por cuenta y concepto
        auto_calculados = {}  # {cuenta_id: {concepto_id: monto}}
        conceptos_auto = [4, 50, 51]  # IDs de conceptos auto-calculados
        
        for transaccion in data:
            cuenta_id = transaccion.get("cuenta_id")
            concepto_id = transaccion.get("concepto_id")
            monto = transaccion.get("monto", 0)
            concepto_nombre = transaccion.get("concepto_nombre", "")
            
            if concepto_id in conceptos_auto:
                if cuenta_id not in auto_calculados:
                    auto_calculados[cuenta_id] = {}
                auto_calculados[cuenta_id][concepto_id] = {
                    "monto": monto,
                    "nombre": concepto_nombre
                }
        
        # Verificar resultados
        logger.info(f"\n=== CUENTAS CON AUTO-CÁLCULOS ===")
        for cuenta_id, conceptos in auto_calculados.items():
            logger.info(f"\n📊 CUENTA {cuenta_id}:")
            for concepto_id, info in conceptos.items():
                logger.info(f"  ✅ {info['nombre']}: ${info['monto']}")
        
        # Validar que múltiples cuentas tienen auto-cálculos
        cuentas_con_autocalculos = len(auto_calculados)
        logger.info(f"\n=== RESUMEN ===")
        logger.info(f"Cuentas con auto-cálculos: {cuentas_con_autocalculos}")
        
        if cuentas_con_autocalculos >= 2:
            logger.info("✅ ÉXITO: Los auto-cálculos funcionan para múltiples cuentas")
            return True
        else:
            logger.warning("⚠️  ADVERTENCIA: Solo hay auto-cálculos para una cuenta")
            return False
            
    except Exception as e:
        logger.error(f"Error al verificar transacciones: {e}")
        return False

def main():
    """Función principal"""
    logger.info("=== VERIFICACIÓN DE AUTO-CÁLCULOS MULTI-CUENTA ===")
    
    # Autenticarse
    token = login()
    if not token:
        logger.error("❌ No se pudo autenticar")
        sys.exit(1)
    
    logger.info("✅ Autenticación exitosa")
    
    # Verificar transacciones
    exito = verificar_transacciones_por_fecha(token)
    
    if exito:
        logger.info("\n🎉 VERIFICACIÓN COMPLETADA: Los auto-cálculos funcionan correctamente para múltiples cuentas")
        sys.exit(0)
    else:
        logger.error("\n❌ VERIFICACIÓN FALLIDA: Los auto-cálculos no funcionan para múltiples cuentas")
        sys.exit(1)

if __name__ == "__main__":
    main()
