import requests
import json

# Credenciales de todos los usuarios
usuarios = [
    ("carlos.gomez@flujo.com", "admin123", "Administrador"),
    ("maria.lopez@flujo.com", "tesoreria123", "Tesorería"),
    ("javier.ruiz@flujo.com", "pagaduria123", "Pagaduría"),
    ("laura.martinez@flujo.com", "mesa123", "Mesa de Dinero")
]

url = "http://localhost:8000/api/v1/auth/login"

print("🔐 PROBANDO LOGIN DE TODOS LOS USUARIOS")
print("=" * 60)

for email, password, rol_esperado in usuarios:
    try:
        data = {"email": email, "password": password}
        response = requests.post(url, json=data)
        
        print(f"📧 Email: {email}")
        print(f"🔑 Contraseña: {password}")
        
        if response.status_code == 200:
            result = response.json()
            user = result["user"]
            print(f"✅ LOGIN EXITOSO")
            print(f"   👤 Nombre: {user['nombre']}")
            print(f"   👔 Rol: {user['rol']}")
            print(f"   🎫 Token: {result['access_token'][:40]}...")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"   Mensaje: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("-" * 60)

print("🎉 PRUEBAS COMPLETADAS")
