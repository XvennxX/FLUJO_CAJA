#!/usr/bin/env python3
"""
Configurar dependencias automáticas entre conceptos
"""

import mysql.connector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def main():
    print("🔗 CONFIGURANDO DEPENDENCIAS AUTOMÁTICAS")
    print("=" * 50)
    
    settings = get_settings()
    
    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        autocommit=True
    )
    
    cursor = connection.cursor()
    
    # Buscar los IDs de los conceptos
    cursor.execute("""
        SELECT id FROM conceptos_flujo_caja 
        WHERE nombre = 'SALDO DIA ANTERIOR' AND area = 'pagaduria'
    """)
    result = cursor.fetchone()
    saldo_dia_anterior_id = result[0] if result else None
    
    cursor.execute("""
        SELECT id FROM conceptos_flujo_caja 
        WHERE nombre = 'SALDO NETO INICIAL PAGADURÍA' AND area = 'tesoreria'
    """)
    result = cursor.fetchone()
    saldo_neto_inicial_id = result[0] if result else None
    
    if saldo_dia_anterior_id and saldo_neto_inicial_id:
        cursor.execute("""
            UPDATE conceptos_flujo_caja 
            SET depende_de_concepto_id = %s, tipo_dependencia = 'copia'
            WHERE id = %s
        """, (saldo_dia_anterior_id, saldo_neto_inicial_id))
        
        print("✅ Dependencia configurada:")
        print(f"   'SALDO NETO INICIAL PAGADURÍA' (ID: {saldo_neto_inicial_id})")
        print(f"   depende de 'SALDO DIA ANTERIOR' (ID: {saldo_dia_anterior_id})")
        print("   Tipo: COPIA (valor se copia automáticamente)")
    else:
        print("❌ No se encontraron los conceptos para configurar dependencia")
        print(f"   SALDO DIA ANTERIOR ID: {saldo_dia_anterior_id}")
        print(f"   SALDO NETO INICIAL ID: {saldo_neto_inicial_id}")
    
    # Verificar el resultado
    cursor.execute("""
        SELECT c1.nombre as concepto, c2.nombre as depende_de, c1.tipo_dependencia
        FROM conceptos_flujo_caja c1
        LEFT JOIN conceptos_flujo_caja c2 ON c1.depende_de_concepto_id = c2.id
        WHERE c1.depende_de_concepto_id IS NOT NULL
    """)
    
    dependencias = cursor.fetchall()
    print(f"\n📊 DEPENDENCIAS CONFIGURADAS: {len(dependencias)}")
    for concepto, depende_de, tipo in dependencias:
        print(f"   '{concepto}' ← '{depende_de}' ({tipo})")
    
    cursor.close()
    connection.close()
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")

if __name__ == "__main__":
    main()
