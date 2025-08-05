"""
Script para probar la conexión a la base de datos MySQL
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    try:
        from app.core.database import engine
        from app.core.config import settings
        
        print("🔧 Configuración de Base de Datos:")
        print(f"  Host: {settings.DB_HOST}")
        print(f"  Puerto: {settings.DB_PORT}")
        print(f"  Usuario: {settings.DB_USER}")
        print(f"  Base de Datos: {settings.DB_NAME}")
        print(f"  URL: {settings.DATABASE_URL.replace(settings.DB_PASSWORD, '***')}")
        print()
        
        print("🔌 Probando conexión...")
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print("✅ ¡Conexión exitosa a MySQL!")
                
                # Verificar que la base de datos flujo_caja existe
                result = connection.execute(text("SHOW DATABASES LIKE 'flujo_caja'"))
                if result.fetchone():
                    print("✅ Base de datos 'flujo_caja' encontrada")
                    
                    # Verificar tablas
                    connection.execute(text("USE flujo_caja"))
                    result = connection.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result.fetchall()]
                    
                    expected_tables = ['rol', 'usuario', 'cuenta', 'concepto', 'ingreso', 'egreso', 'auditoria', 'sesion_usuario']
                    
                    print(f"📊 Tablas encontradas: {len(tables)}")
                    for table in tables:
                        print(f"  ✓ {table}")
                    
                    missing_tables = [table for table in expected_tables if table not in tables]
                    if missing_tables:
                        print(f"⚠️  Tablas faltantes: {missing_tables}")
                        print("💡 Ejecuta los scripts SQL de la carpeta Database/scripts/")
                    else:
                        print("✅ Todas las tablas necesarias están presentes")
                        
                        # Verificar datos iniciales
                        result = connection.execute(text("SELECT COUNT(*) FROM rol"))
                        rol_count = result.fetchone()[0]
                        
                        result = connection.execute(text("SELECT COUNT(*) FROM concepto"))
                        concepto_count = result.fetchone()[0]
                        
                        print(f"📈 Datos iniciales:")
                        print(f"  Roles: {rol_count}")
                        print(f"  Conceptos: {concepto_count}")
                        
                        if rol_count == 0 or concepto_count == 0:
                            print("💡 Ejecuta el script Database/seeds/initial_data.sql para cargar datos iniciales")
                        
                else:
                    print("❌ Base de datos 'flujo_caja' no encontrada")
                    print("💡 Ejecuta: mysql -u root -p < Database/scripts/create_database.sql")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        print()
        print("🔧 Posibles soluciones:")
        print("1. Verifica que MySQL esté ejecutándose")
        print("2. Confirma las credenciales en el archivo .env")
        print("3. Asegúrate de que la base de datos 'flujo_caja' exista")
        print("4. Verifica que pymysql esté instalado: pip install pymysql")
        return False

if __name__ == "__main__":
    print("🧪 Probando conexión a la base de datos...")
    print("=" * 50)
    test_database_connection()
