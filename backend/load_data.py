"""
Script para cargar datos iniciales en la base de datos
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_initial_data():
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        print("📊 Cargando datos iniciales...")
        
        with engine.connect() as connection:
            # Usar la base de datos flujo_caja
            connection.execute(text("USE flujo_caja"))
            
            # Insertar roles
            print("🎭 Insertando roles...")
            roles_sql = """
            INSERT IGNORE INTO rol (nombre_rol) VALUES 
            ('ADMINISTRADOR'),
            ('SUPERVISOR'),
            ('OPERADOR'),
            ('CONTADOR');
            """
            connection.execute(text(roles_sql))
            
            # Insertar conceptos
            print("📝 Insertando conceptos...")
            conceptos_sql = """
            INSERT IGNORE INTO concepto (nombre, tipo) VALUES 
            -- Conceptos de INGRESO
            ('Venta de Productos', 'INGRESO'),
            ('Venta de Servicios', 'INGRESO'),
            ('Intereses Bancarios', 'INGRESO'),
            ('Descuentos Recibidos', 'INGRESO'),
            ('Otros Ingresos', 'INGRESO'),
            ('Préstamos Recibidos', 'INGRESO'),
            ('Aportes de Socios', 'INGRESO'),

            -- Conceptos de EGRESO
            ('Compra de Mercancía', 'EGRESO'),
            ('Gastos de Oficina', 'EGRESO'),
            ('Servicios Públicos', 'EGRESO'),
            ('Nómina', 'EGRESO'),
            ('Arrendamientos', 'EGRESO'),
            ('Mantenimiento', 'EGRESO'),
            ('Impuestos', 'EGRESO'),
            ('Intereses Pagados', 'EGRESO'),
            ('Publicidad', 'EGRESO'),
            ('Transporte', 'EGRESO'),
            ('Seguros', 'EGRESO'),
            ('Otros Gastos', 'EGRESO');
            """
            connection.execute(text(conceptos_sql))
            
            # Insertar cuentas
            print("🏦 Insertando cuentas...")
            cuentas_sql = """
            INSERT IGNORE INTO cuenta (nombre, saldo_actual, estado) VALUES 
            ('Caja Principal', 0.00, TRUE),
            ('Banco Cuenta Corriente', 0.00, TRUE),
            ('Banco Cuenta Ahorros', 0.00, TRUE);
            """
            connection.execute(text(cuentas_sql))
            
            # Insertar usuario administrador
            print("👤 Insertando usuario administrador...")
            usuario_sql = """
            INSERT IGNORE INTO usuario (nombre_completo, correo, contraseña, id_rol, estado) VALUES 
            ('Administrador Sistema', 'admin@empresa.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewaBnBdmCrrHm/Ve', 1, TRUE);
            """
            connection.execute(text(usuario_sql))
            
            # Confirmar cambios
            connection.commit()
            
            print("✅ Datos iniciales cargados exitosamente!")
            print()
            print("📊 Resumen de datos cargados:")
            
            # Verificar datos cargados
            result = connection.execute(text("SELECT COUNT(*) FROM rol"))
            rol_count = result.fetchone()[0]
            print(f"  Roles: {rol_count}")
            
            result = connection.execute(text("SELECT COUNT(*) FROM concepto"))
            concepto_count = result.fetchone()[0]
            print(f"  Conceptos: {concepto_count}")
            
            result = connection.execute(text("SELECT COUNT(*) FROM cuenta"))
            cuenta_count = result.fetchone()[0]
            print(f"  Cuentas: {cuenta_count}")
            
            result = connection.execute(text("SELECT COUNT(*) FROM usuario"))
            usuario_count = result.fetchone()[0]
            print(f"  Usuarios: {usuario_count}")
            
            print()
            print("🔑 Credenciales de acceso:")
            print("  Usuario: admin@empresa.com")
            print("  Contraseña: admin123")
            
        return True
        
    except Exception as e:
        print(f"❌ Error cargando datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("📊 Cargando datos iniciales en la base de datos...")
    print("=" * 50)
    load_initial_data()
