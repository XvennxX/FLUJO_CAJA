import requests

print("🧪 PROBANDO MANEJO DE ERRORES")
print("=" * 50)

test_cases = [
    ("carlos.gomez@flujo.com", "wrongpassword", "Contraseña incorrecta"),
    ("wrong@email.com", "admin123", "Email inexistente"),
    ("notvalidemail", "admin123", "Email con formato inválido"),
]

url = "http://localhost:8000/api/v1/auth/login"

for email, password, description in test_cases:
    print(f"📧 Caso: {description}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    try:
        data = {"email": email, "password": password}
        response = requests.post(url, json=data)
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Sin detalle')}")
            except:
                print(f"   Error: {response.text}")
        else:
            print("   ✅ Login exitoso (inesperado)")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("-" * 50)

# Probar un caso exitoso
print("✅ Probando caso exitoso:")
try:
    data = {"email": "carlos.gomez@flujo.com", "password": "admin123"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login exitoso confirmado")
    else:
        print(f"❌ Error inesperado: {response.text}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
