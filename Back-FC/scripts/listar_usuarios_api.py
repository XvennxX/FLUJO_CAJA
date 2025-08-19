import requests
import json

def mostrar_usuarios_api():
    """Obtiene y muestra usuarios usando la API existente"""
    
    # Paso 1: Login como administrador
    login_data = {
        'email': 'carlos.gomez@flujo.com',
        'password': 'admin123'
    }

    print('🔐 Haciendo login como administrador...')
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)

    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data['access_token']
        print('✅ Login exitoso')
        
        # Paso 2: Obtener lista de usuarios
        headers = {'Authorization': f'Bearer {token}'}
        users_response = requests.get('http://localhost:8000/api/v1/users/', headers=headers)
        
        if users_response.status_code == 200:
            usuarios = users_response.json()
            print(f'\n👥 USUARIOS REGISTRADOS ({len(usuarios)} total):')
            print('=' * 80)
            
            for i, user in enumerate(usuarios, 1):
                print(f'📋 Usuario #{i}')
                print(f'   ID: {user["id"]}')
                print(f'   Nombre: {user["nombre"]}')
                print(f'   Email: {user["email"]}')
                print(f'   Rol: {user["rol"]}')
                print()
                
            # Resumen por roles
            roles = {}
            for user in usuarios:
                rol = user['rol']
                roles[rol] = roles.get(rol, 0) + 1
            
            print('🎭 RESUMEN POR ROLES:')
            for rol, cantidad in roles.items():
                print(f'   • {rol}: {cantidad} usuario(s)')
            print('=' * 80)
                
        else:
            print(f'❌ Error obteniendo usuarios: {users_response.status_code}')
            print(users_response.text)
    else:
        print(f'❌ Error en login: {login_response.status_code}')
        print(login_response.text)

if __name__ == "__main__":
    mostrar_usuarios_api()
