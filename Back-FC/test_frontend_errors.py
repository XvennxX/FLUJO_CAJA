import requests

print("🧪 VERIFICANDO RESPUESTAS DEL BACKEND")
print("=" * 50)

url = "http://localhost:8000/api/v1/auth/login"

# Casos de prueba
test_cases = [
    {
        "name": "Login exitoso",
        "email": "carlos.gomez@flujo.com",
        "password": "admin123",
        "expected_status": 200
    },
    {
        "name": "Contraseña incorrecta", 
        "email": "carlos.gomez@flujo.com",
        "password": "wrongpassword",
        "expected_status": 401
    },
    {
        "name": "Usuario inexistente",
        "email": "noexiste@test.com", 
        "password": "admin123",
        "expected_status": 401
    },
    {
        "name": "Email inválido",
        "email": "emailinvalido",
        "password": "admin123", 
        "expected_status": 422
    }
]

for test in test_cases:
    print(f"\n🔍 Probando: {test['name']}")
    print(f"   Email: {test['email']}")
    print(f"   Password: {test['password']}")
    
    try:
        response = requests.post(url, json={
            "email": test["email"],
            "password": test["password"]
        })
        
        print(f"   Status: {response.status_code} (esperado: {test['expected_status']})")
        
        if response.status_code == test["expected_status"]:
            print("   ✅ Estado correcto")
        else:
            print("   ❌ Estado incorrecto")
            
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"   Mensaje: {error_data.get('detail', 'Sin mensaje')}")
            except:
                print(f"   Respuesta raw: {response.text}")
        else:
            data = response.json()
            print(f"   Usuario: {data['user']['nombre']}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

print("\n🎯 Las pruebas han terminado. Ahora prueba en el frontend:")
print("👉 Abre http://localhost:5000 y prueba con credenciales incorrectas")
