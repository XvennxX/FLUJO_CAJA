#!/usr/bin/env python3
"""
Script para mostrar todos los usuarios existentes en la base de datos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.usuarios import Usuario
from sqlalchemy import text

def mostrar_usuarios():
    """Muestra todos los usuarios de la base de datos"""
    db = SessionLocal()
    try:
        print("=" * 80)
        print(" 👥 USUARIOS REGISTRADOS EN SIFCO")
        print("=" * 80)
        
        # Obtener todos los usuarios
        usuarios = db.query(Usuario).all()
        
        if not usuarios:
            print("❌ No hay usuarios registrados en la base de datos.")
            return
        
        # Mostrar información de cada usuario
        for i, user in enumerate(usuarios, 1):
            print(f"\n📋 Usuario #{i}")
            print(f"   ID: {user.id}")
            print(f"   Nombre: {user.nombre}")
            print(f"   Email: {user.email}")
            print(f"   Rol: {user.rol}")
            print(f"   Hash contraseña: {user.contrasena[:20]}...")
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total de usuarios: {len(usuarios)}")
        
        # Mostrar conteo por rol
        print(f"\n🎭 USUARIOS POR ROL:")
        roles = db.execute(text('SELECT rol, COUNT(*) as cantidad FROM usuarios GROUP BY rol')).fetchall()
        for rol, cantidad in roles:
            print(f"   • {rol}: {cantidad} usuario(s)")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error al consultar usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    mostrar_usuarios()
