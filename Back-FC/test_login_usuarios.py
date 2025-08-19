import requests
import json

usuarios_prueba = [
    {'email': 'maria.lopez@flujo.com', 'password': 'tesoreria123', 'nombre': 'María (Tesorería)'},
    {'email': 'javier.ruiz@flujo.com', 'password': 'pagaduria123', 'nombre': 'Javier (Pagaduría)'},
    {'email': 'laura.martinez@flujo.com', 'password': 'mesa123', 'nombre': 'Laura (Mesa de Dinero)'}
]

url = 'http://localhost:8000/api/v1/auth/login'

for usuario in usuarios_prueba:
    nombre = usuario['nombre']
    print(f'=== PROBANDO LOGIN CON {nombre} ===')
    try:
        response = requests.post(url, json={'email': usuario['email'], 'password': usuario['password']})
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            user_data = data['user']
            print(f'Usuario: {user_data["nombre"]}')
            print(f'Rol: {user_data["rol"]}')
            print('✅ LOGIN EXITOSO')
        else:
            print(f'❌ Error: {response.text}')
        print()
    except Exception as e:
        print(f'❌ Error de conexión: {e}')
        print()
