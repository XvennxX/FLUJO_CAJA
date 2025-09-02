"""
Script de prueba rápida para verificar actualizaciones de TRM
"""

import time
import requests
from datetime import datetime

def check_trm_status():
    """Verifica el estado actual de la TRM"""
    try:
        response = requests.get('http://localhost:8000/api/v1/trm/current')
        if response.status_code == 200:
            data = response.json()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TRM actual: ${float(data['valor']):,.2f} (Fecha: {data['fecha']})")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error de conexión: {e}")
        return False

def monitor_trm_updates(duration_minutes=5):
    """Monitorea las actualizaciones de TRM por un tiempo determinado"""
    print("=" * 60)
    print("MONITOR DE ACTUALIZACIONES TRM")
    print("=" * 60)
    print(f"Monitoreando por {duration_minutes} minutos...")
    print(f"Verificando cada 30 segundos...")
    print("=" * 60)
    
    end_time = time.time() + (duration_minutes * 60)
    
    while time.time() < end_time:
        check_trm_status()
        time.sleep(30)  # Verificar cada 30 segundos
        
    print("=" * 60)
    print("MONITOREO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    print("Verificación inicial:")
    check_trm_status()
    print("\nIniciando monitoreo...")
    monitor_trm_updates(3)  # Monitorear por 3 minutos
