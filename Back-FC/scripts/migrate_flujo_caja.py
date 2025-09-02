#!/usr/bin/env python3
"""
Script para ejecutar todas las migraciones de flujo de caja
Ejecuta los archivos SQL en orden correcto
"""

import os
import mysql.connector
from mysql.connector import Error
import sys

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def ejecutar_sql_file(cursor, filepath):
    """Ejecuta un archivo SQL"""
    try:
        print(f"📄 Ejecutando: {os.path.basename(filepath)}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir por statements (punto y coma)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    # Consume todos los resultados
                    try:
                        cursor.fetchall()
                    except:
                        pass
                    print(f"   ✅ Ejecutado correctamente")
                except Error as e:
                    if "already exists" in str(e) or "Duplicate" in str(e):
                        print(f"   ⚠️ Ya existe (ignorando): {e}")
                    else:
                        print(f"   ❌ Error: {e}")
                        return False
        
        return True
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO MIGRACIÓN DE FLUJO DE CAJA")
    print("=" * 50)
    
    settings = get_settings()
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            autocommit=True
        )
        
        cursor = connection.cursor()
        print(f"✅ Conectado a la base de datos: {settings.db_name}")
        print()
        
        # Lista de archivos SQL en orden de ejecución
        sql_files = [
            "create_flujo_caja_tables.sql",
            "alter_conceptos_flujo_caja.sql",
            "alter_transacciones_flujo_caja.sql", 
            "insert_conceptos_iniciales.sql",
            "configure_dependencias.sql"
        ]
        
        # Directorio de migraciones
        migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        
        # Ejecutar cada archivo
        for sql_file in sql_files:
            filepath = os.path.join(migrations_dir, sql_file)
            
            if os.path.exists(filepath):
                success = ejecutar_sql_file(cursor, filepath)
                if success:
                    print(f"✅ {sql_file} ejecutado exitosamente")
                else:
                    print(f"❌ Error ejecutando {sql_file}")
                    return False
            else:
                print(f"⚠️ Archivo no encontrado: {sql_file}")
            
            print("-" * 30)
        
        print()
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        
        # Mostrar resumen
        cursor.execute("""
            SELECT 
                area,
                COUNT(*) as total_conceptos
            FROM conceptos_flujo_caja 
            WHERE activo = TRUE 
            GROUP BY area
        """)
        
        print("📊 RESUMEN:")
        for area, total in cursor.fetchall():
            print(f"   {area.upper()}: {total} conceptos")
        
        cursor.execute("""
            SELECT COUNT(*) as dependencias
            FROM conceptos_flujo_caja 
            WHERE depende_de_concepto_id IS NOT NULL
        """)
        
        dependencias = cursor.fetchone()[0]
        print(f"   DEPENDENCIAS: {dependencias} configuradas")
        
    except Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
