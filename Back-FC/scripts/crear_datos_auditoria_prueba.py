"""
Script para poblar la tabla de auditoría con datos de prueba
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.auditoria_service import AuditoriaService
from app.models.usuarios import Usuario

def crear_datos_auditoria_prueba():
    """Crear registros de auditoría de prueba"""
    db = next(get_db())
    
    try:
        # Obtener un usuario existente para las pruebas
        usuario = db.query(Usuario).first()
        if not usuario:
            print("❌ No se encontraron usuarios. Primero debe crear usuarios.")
            return
        
        print(f"👤 Usando usuario: {usuario.nombre} ({usuario.email})")
        
        # Crear varios registros de prueba
        registros_prueba = [
            {
                "accion": "CREATE",
                "modulo": "FLUJO_CAJA",
                "entidad": "Transacción",
                "entidad_id": "2025-10-23",
                "descripcion": "Creó transacción: CONSUMO en BANCO DAVIVIENDA - 482800001265 por $500,000",
                "valores_nuevos": {"monto": 500000, "concepto": "CONSUMO"},
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            {
                "accion": "UPDATE", 
                "modulo": "FLUJO_CAJA",
                "entidad": "Transacción",
                "entidad_id": "2025-10-23",
                "descripcion": "Modificó transacción: PAGOS INTERCOMPAÑÍAS ($2,000,000 → $2,500,000)",
                "valores_anteriores": {"monto": 2000000},
                "valores_nuevos": {"monto": 2500000},
                "ip_address": "192.168.1.101",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            },
            {
                "accion": "CREATE",
                "modulo": "EMPRESAS",
                "entidad": "Empresa",
                "entidad_id": "10",
                "descripcion": "Creó empresa: SEGUROS GENERALES S.A.",
                "valores_nuevos": {"nombre": "SEGUROS GENERALES S.A.", "codigo": "SG001"},
                "ip_address": "192.168.1.102",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0"
            },
            {
                "accion": "DELETE",
                "modulo": "CUENTAS",
                "entidad": "Cuenta Bancaria", 
                "entidad_id": "25",
                "descripcion": "Eliminó cuenta bancaria: BANCO POPULAR - 40195224",
                "valores_anteriores": {"banco": "BANCO POPULAR", "numero": "40195224"},
                "ip_address": "192.168.1.103",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/17.2.0"
            },
            {
                "accion": "EXPORT",
                "modulo": "REPORTES",
                "entidad": "Reporte",
                "descripcion": "Exportó reporte de flujo mensual de octubre 2025",
                "valores_nuevos": {"formato": "excel", "periodo": "2025-10"},
                "ip_address": "192.168.1.104",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0"
            },
            {
                "accion": "UPDATE",
                "modulo": "USUARIOS",
                "entidad": "Usuario",
                "entidad_id": str(usuario.id),
                "descripcion": f"Actualizó perfil de usuario: {usuario.nombre}",
                "valores_anteriores": {"activo": True},
                "valores_nuevos": {"activo": True, "ultima_modificacion": "2025-10-23"},
                "ip_address": "192.168.1.105",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            },
            {
                "accion": "CREATE",
                "modulo": "CONCEPTOS",
                "entidad": "Concepto",
                "entidad_id": "100",
                "descripcion": "Creó nuevo concepto: INVERSIÓN TEMPORALES",
                "valores_nuevos": {"nombre": "INVERSIÓN TEMPORALES", "tipo": "ingreso", "area": "tesoreria"},
                "ip_address": "192.168.1.106",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            },
            {
                "accion": "READ",
                "modulo": "FLUJO_CAJA",
                "entidad": "Dashboard",
                "descripcion": "Consultó dashboard de tesorería para fecha 2025-10-23",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            }
        ]
        
        # Crear los registros con fechas variadas
        for i, registro in enumerate(registros_prueba):
            # Distribuir en los últimos días
            fecha_offset = timedelta(days=i % 7, hours=i % 24, minutes=i * 15)
            fecha_registro = datetime.now() - fecha_offset
            
            # Crear registro manualmente ya que no tenemos request
            from app.models.auditoria import RegistroAuditoria
            
            registro_auditoria = RegistroAuditoria(
                usuario_id=usuario.id,
                usuario_nombre=usuario.nombre,
                usuario_email=usuario.email,
                accion=registro["accion"],
                modulo=registro["modulo"],
                entidad=registro["entidad"],
                entidad_id=registro.get("entidad_id"),
                descripcion=registro["descripcion"],
                valores_anteriores=registro.get("valores_anteriores"),
                valores_nuevos=registro.get("valores_nuevos"),
                ip_address=registro["ip_address"],
                user_agent=registro["user_agent"],
                fecha_hora=fecha_registro,
                duracion_ms=100 + (i * 50),
                resultado="EXITOSO"
            )
            
            db.add(registro_auditoria)
            db.commit()
            
# La fecha ya se establece arriba
        
        print(f"✅ Se crearon {len(registros_prueba)} registros de auditoría de prueba")
        
        # Mostrar estadísticas
        from app.models.auditoria import RegistroAuditoria
        total_registros = db.query(RegistroAuditoria).count()
        print(f"📊 Total de registros en auditoría: {total_registros}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    crear_datos_auditoria_prueba()