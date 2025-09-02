#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y gestionar usuarios en la base de datos
"""

import sys
sys.path.append("c:/Users/1006509625/Desktop/Nueva carpeta/Back-FC")

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.usuarios import Usuario
from app.core.config import get_settings
from app.services.auth_service import get_password_hash, verify_password

def connect_to_db():
    """Conectar a la base de datos"""
    try:
        settings = get_settings()
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def list_all_users(db):
    """Listar todos los usuarios"""
    print("👥 USUARIOS EN LA BASE DE DATOS:")
    print("-" * 60)
    
    users = db.query(Usuario).all()
    if not users:
        print("   ❌ No hay usuarios en la base de datos")
        return []
    
    for user in users:
        status = "🟢 Activo" if user.estado else "🔴 Inactivo"
        print(f"   ID: {user.id}")
        print(f"   Nombre: {user.nombre}")
        print(f"   Email: {user.email}")
        print(f"   Rol: {user.rol}")
        print(f"   Estado: {status}")
        print(f"   Hash: {user.contrasena[:20]}...")
        print("-" * 40)
    
    return users

def test_password_verification(db, email, test_passwords):
    """Probar verificación de contraseñas"""
    print(f"\n🔐 PROBANDO CONTRASEÑAS PARA: {email}")
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        print(f"   ❌ Usuario {email} no encontrado")
        return None
    
    for password in test_passwords:
        is_valid = verify_password(password, user.contrasena)
        status = "✅" if is_valid else "❌"
        print(f"   {status} '{password}': {is_valid}")
        if is_valid:
            return password
    
    return None

def create_test_user(db):
    """Crear usuario de prueba"""
    print("\n🏗️ CREANDO USUARIO DE PRUEBA...")
    
    # Verificar si ya existe
    existing = db.query(Usuario).filter(Usuario.email == "test@bolivar.com").first()
    if existing:
        print("   ⚠️ Usuario test@bolivar.com ya existe")
        # Actualizar contraseña
        existing.contrasena = get_password_hash("test123")
        db.commit()
        print("   ✅ Contraseña actualizada a 'test123'")
        return existing
    
    # Crear nuevo usuario
    test_user = Usuario(
        nombre="Usuario Test",
        email="test@bolivar.com",
        contrasena=get_password_hash("test123"),
        rol="admin",
        estado=True
    )
    
    try:
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print("   ✅ Usuario creado exitosamente:")
        print(f"      Email: test@bolivar.com")
        print(f"      Contraseña: test123")
        print(f"      Rol: admin")
        return test_user
    except Exception as e:
        print(f"   ❌ Error creando usuario: {e}")
        db.rollback()
        return None

def main():
    print("🔍 DIAGNÓSTICO DE USUARIOS Y AUTENTICACIÓN")
    print("=" * 60)
    
    # Conectar a la base de datos
    db = connect_to_db()
    if not db:
        return
    
    try:
        # 1. Listar usuarios existentes
        users = list_all_users(db)
        
        # 2. Si hay usuarios, probar contraseñas comunes
        if users:
            common_passwords = ["123456", "admin123", "mesa123", "tesoreria123", "pagaduria123", "password", "admin"]
            
            for user in users[:3]:  # Solo los primeros 3 usuarios
                valid_password = test_password_verification(db, user.email, common_passwords)
                if valid_password:
                    print(f"\n✅ CREDENCIALES VÁLIDAS ENCONTRADAS:")
                    print(f"   Email: {user.email}")
                    print(f"   Contraseña: {valid_password}")
                    print(f"   Rol: {user.rol}")
                    break
        
        # 3. Crear usuario de prueba si es necesario
        if not users or len(users) == 0:
            create_test_user(db)
        else:
            print(f"\n🔧 RECOMENDACIÓN:")
            print(f"   Crear usuario de prueba con credenciales conocidas...")
            test_user = create_test_user(db)
            if test_user:
                print(f"\n✅ USAR ESTAS CREDENCIALES PARA TESTING:")
                print(f"   Email: test@bolivar.com")
                print(f"   Contraseña: test123")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
