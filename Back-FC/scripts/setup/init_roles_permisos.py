"""
Script para inicializar roles y permisos del sistema
Ejecutar: python -m scripts.setup.init_roles_permisos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.models.roles import Rol, Permiso
from app.models.usuarios import Usuario

def crear_permisos_sistema(db):
    """Crear todos los permisos del sistema"""
    
    permisos_data = [
        # Módulo: Usuarios
        {"codigo": "usuarios.ver", "nombre": "Ver usuarios", "modulo": "usuarios", "descripcion": "Permite ver la lista de usuarios"},
        {"codigo": "usuarios.crear", "nombre": "Crear usuarios", "modulo": "usuarios", "descripcion": "Permite crear nuevos usuarios"},
        {"codigo": "usuarios.editar", "nombre": "Editar usuarios", "modulo": "usuarios", "descripcion": "Permite editar usuarios existentes"},
        {"codigo": "usuarios.eliminar", "nombre": "Eliminar usuarios", "modulo": "usuarios", "descripcion": "Permite eliminar usuarios"},
        {"codigo": "usuarios.cambiar_estado", "nombre": "Cambiar estado de usuarios", "modulo": "usuarios", "descripcion": "Permite activar/desactivar usuarios"},
        
        # Módulo: Roles y Permisos
        {"codigo": "roles.ver", "nombre": "Ver roles", "modulo": "roles", "descripcion": "Permite ver roles y permisos"},
        {"codigo": "roles.crear", "nombre": "Crear roles", "modulo": "roles", "descripcion": "Permite crear nuevos roles"},
        {"codigo": "roles.editar", "nombre": "Editar roles", "modulo": "roles", "descripcion": "Permite editar roles y asignar permisos"},
        {"codigo": "roles.eliminar", "nombre": "Eliminar roles", "modulo": "roles", "descripcion": "Permite eliminar roles"},
        
        # Módulo: Transacciones
        {"codigo": "transacciones.ver", "nombre": "Ver transacciones", "modulo": "transacciones", "descripcion": "Permite ver transacciones de flujo de caja"},
        {"codigo": "transacciones.crear", "nombre": "Crear transacciones", "modulo": "transacciones", "descripcion": "Permite crear nuevas transacciones"},
        {"codigo": "transacciones.editar", "nombre": "Editar transacciones", "modulo": "transacciones", "descripcion": "Permite editar transacciones existentes"},
        {"codigo": "transacciones.eliminar", "nombre": "Eliminar transacciones", "modulo": "transacciones", "descripcion": "Permite eliminar transacciones"},
        {"codigo": "transacciones.aprobar", "nombre": "Aprobar transacciones", "modulo": "transacciones", "descripcion": "Permite aprobar transacciones pendientes"},
        
        # Módulo: Conceptos
        {"codigo": "conceptos.ver", "nombre": "Ver conceptos", "modulo": "conceptos", "descripcion": "Permite ver conceptos de flujo de caja"},
        {"codigo": "conceptos.crear", "nombre": "Crear conceptos", "modulo": "conceptos", "descripcion": "Permite crear nuevos conceptos"},
        {"codigo": "conceptos.editar", "nombre": "Editar conceptos", "modulo": "conceptos", "descripcion": "Permite editar conceptos existentes"},
        {"codigo": "conceptos.eliminar", "nombre": "Eliminar conceptos", "modulo": "conceptos", "descripcion": "Permite eliminar conceptos"},
        
        # Módulo: Cuentas Bancarias
        {"codigo": "cuentas.ver", "nombre": "Ver cuentas bancarias", "modulo": "cuentas", "descripcion": "Permite ver cuentas bancarias"},
        {"codigo": "cuentas.crear", "nombre": "Crear cuentas bancarias", "modulo": "cuentas", "descripcion": "Permite crear nuevas cuentas bancarias"},
        {"codigo": "cuentas.editar", "nombre": "Editar cuentas bancarias", "modulo": "cuentas", "descripcion": "Permite editar cuentas bancarias"},
        {"codigo": "cuentas.eliminar", "nombre": "Eliminar cuentas bancarias", "modulo": "cuentas", "descripcion": "Permite eliminar cuentas bancarias"},
        
        # Módulo: Reportes
        {"codigo": "reportes.ver", "nombre": "Ver reportes", "modulo": "reportes", "descripcion": "Permite ver reportes y consultas"},
        {"codigo": "reportes.exportar", "nombre": "Exportar reportes", "modulo": "reportes", "descripcion": "Permite exportar reportes a Excel/PDF"},
        {"codigo": "reportes.consolidado", "nombre": "Ver reportes consolidados", "modulo": "reportes", "descripcion": "Permite ver reportes consolidados de todas las áreas"},
        
        # Módulo: TRM
        {"codigo": "trm.ver", "nombre": "Ver TRM", "modulo": "trm", "descripcion": "Permite ver tasas de cambio"},
        {"codigo": "trm.editar", "nombre": "Editar TRM", "modulo": "trm", "descripcion": "Permite editar tasas de cambio"},
        
        # Módulo: Conciliación
        {"codigo": "conciliacion.ver", "nombre": "Ver conciliaciones", "modulo": "conciliacion", "descripcion": "Permite ver conciliaciones contables"},
        {"codigo": "conciliacion.crear", "nombre": "Crear conciliaciones", "modulo": "conciliacion", "descripcion": "Permite crear conciliaciones"},
        {"codigo": "conciliacion.aprobar", "nombre": "Aprobar conciliaciones", "modulo": "conciliacion", "descripcion": "Permite aprobar conciliaciones"},
        
        # Módulo: Auditoría
        {"codigo": "auditoria.ver", "nombre": "Ver auditoría", "modulo": "auditoria", "descripcion": "Permite ver registros de auditoría"},
        
        # Módulo: Configuración
        {"codigo": "configuracion.ver", "nombre": "Ver configuración", "modulo": "configuracion", "descripcion": "Permite ver configuración del sistema"},
        {"codigo": "configuracion.editar", "nombre": "Editar configuración", "modulo": "configuracion", "descripcion": "Permite modificar configuración del sistema"},
    ]
    
    permisos_creados = []
    for permiso_data in permisos_data:
        # Verificar si ya existe
        permiso_existente = db.query(Permiso).filter(Permiso.codigo == permiso_data["codigo"]).first()
        if not permiso_existente:
            permiso = Permiso(**permiso_data, activo=True)
            db.add(permiso)
            permisos_creados.append(permiso_data["codigo"])
    
    db.commit()
    print(f"✅ Creados {len(permisos_creados)} permisos nuevos")
    return permisos_creados


def crear_roles_sistema(db):
    """Crear roles predefinidos del sistema"""
    
    # Obtener todos los permisos
    todos_permisos = db.query(Permiso).all()
    permisos_dict = {p.codigo: p for p in todos_permisos}
    
    roles_data = [
        {
            "codigo": "ADMIN",
            "nombre": "Administrador",
            "descripcion": "Acceso total al sistema. Puede gestionar usuarios, roles y toda la configuración.",
            "es_sistema": True,
            "permisos": [p.codigo for p in todos_permisos]  # Todos los permisos
        },
        {
            "codigo": "TESORERIA",
            "nombre": "Tesorería",
            "descripcion": "Gestión completa de flujo de caja, transacciones y reportes de tesorería.",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear", "transacciones.editar", "transacciones.aprobar",
                "conceptos.ver", "conceptos.crear", "conceptos.editar",
                "cuentas.ver", "cuentas.crear", "cuentas.editar",
                "reportes.ver", "reportes.exportar", "reportes.consolidado",
                "trm.ver",
                "conciliacion.ver", "conciliacion.crear", "conciliacion.aprobar",
            ]
        },
        {
            "codigo": "PAGADURIA",
            "nombre": "Pagaduría",
            "descripcion": "Gestión de transacciones de nómina y pagos a proveedores.",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear", "transacciones.editar",
                "conceptos.ver",
                "cuentas.ver",
                "reportes.ver", "reportes.exportar",
                "trm.ver",
            ]
        },
        {
            "codigo": "MESA_DINERO",
            "nombre": "Mesa de Dinero",
            "descripcion": "Gestión de operaciones de tesorería, inversiones y divisas.",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear", "transacciones.editar",
                "conceptos.ver",
                "cuentas.ver",
                "reportes.ver", "reportes.exportar",
                "trm.ver", "trm.editar",
                "conciliacion.ver",
            ]
        },
        {
            "codigo": "CONSULTA",
            "nombre": "Solo Consulta",
            "descripcion": "Acceso de solo lectura a transacciones y reportes.",
            "es_sistema": False,
            "permisos": [
                "transacciones.ver",
                "conceptos.ver",
                "cuentas.ver",
                "reportes.ver",
                "trm.ver",
                "conciliacion.ver",
            ]
        },
    ]
    
    roles_creados = []
    for rol_data in roles_data:
        # Verificar si ya existe
        rol_existente = db.query(Rol).filter(Rol.codigo == rol_data["codigo"]).first()
        if not rol_existente:
            permisos_rol = [permisos_dict[codigo] for codigo in rol_data["permisos"] if codigo in permisos_dict]
            
            rol = Rol(
                codigo=rol_data["codigo"],
                nombre=rol_data["nombre"],
                descripcion=rol_data["descripcion"],
                es_sistema=rol_data["es_sistema"],
                activo=True
            )
            rol.permisos = permisos_rol
            
            db.add(rol)
            roles_creados.append(rol_data["codigo"])
    
    db.commit()
    print(f"✅ Creados {len(roles_creados)} roles nuevos")
    return roles_creados


def migrar_usuarios_a_nuevos_roles(db):
    """Migrar usuarios del sistema de roles antiguo al nuevo"""
    
    # Mapeo de roles antiguos a nuevos
    mapeo_roles = {
        "administrador": "ADMIN",
        "tesoreria": "TESORERIA",
        "pagaduria": "PAGADURIA",
        "mesa_dinero": "MESA_DINERO",
    }
    
    usuarios = db.query(Usuario).all()
    usuarios_migrados = 0
    
    for usuario in usuarios:
        if usuario.rol_id is None and usuario.rol:  # Si no tiene rol nuevo pero sí antiguo
            codigo_rol_nuevo = mapeo_roles.get(usuario.rol.lower())
            if codigo_rol_nuevo:
                rol_nuevo = db.query(Rol).filter(Rol.codigo == codigo_rol_nuevo).first()
                if rol_nuevo:
                    usuario.rol_id = rol_nuevo.id
                    usuarios_migrados += 1
    
    db.commit()
    print(f"✅ Migrados {usuarios_migrados} usuarios al nuevo sistema de roles")
    return usuarios_migrados


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("INICIALIZACIÓN DE ROLES Y PERMISOS DEL SISTEMA")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. Crear permisos
        print("1️⃣ Creando permisos del sistema...")
        crear_permisos_sistema(db)
        
        # 2. Crear roles
        print("\n2️⃣ Creando roles del sistema...")
        crear_roles_sistema(db)
        
        # 3. Migrar usuarios existentes
        print("\n3️⃣ Migrando usuarios existentes...")
        migrar_usuarios_a_nuevos_roles(db)
        
        print("\n" + "="*70)
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70 + "\n")
        
        # Mostrar resumen
        total_permisos = db.query(Permiso).count()
        total_roles = db.query(Rol).count()
        total_usuarios = db.query(Usuario).filter(Usuario.rol_id.isnot(None)).count()
        
        print(f"📊 RESUMEN:")
        print(f"   - Total permisos: {total_permisos}")
        print(f"   - Total roles: {total_roles}")
        print(f"   - Usuarios con nuevo sistema: {total_usuarios}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
