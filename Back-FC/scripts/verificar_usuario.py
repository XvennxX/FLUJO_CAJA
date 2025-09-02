#!/usr/bin/env python3
"""
Script para verificar y crear usuario de prueba
"""
import mysql.connector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def verificar_usuario():
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

    # Verificar si existe usuario con ID 1
    cursor.execute("SELECT id FROM usuarios WHERE id = 1")
    usuario = cursor.fetchone()

    if usuario:
        print("✅ Usuario ID 1 existe")
    else:
        print("⚠️ Usuario ID 1 no existe, creando usuario de prueba...")
        cursor.execute("""
            INSERT INTO usuarios (id, nombre, email, contrasena, rol) 
            VALUES (1, 'admin', 'admin@example.com', 'hashed_password', 'admin')
        """)
        print("✅ Usuario de prueba creado")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    verificar_usuario()
