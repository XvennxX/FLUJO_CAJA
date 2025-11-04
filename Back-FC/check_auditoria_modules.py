from app.core.database import SessionLocal
from app.models.auditoria import RegistroAuditoria
from sqlalchemy import func

db = SessionLocal()
try:
    print('\n--- Conteo de registros por módulo ---')
    rows = db.query(RegistroAuditoria.modulo, func.count(RegistroAuditoria.id)).group_by(RegistroAuditoria.modulo).all()
    for modulo, cnt in rows:
        print(f'{modulo}: {cnt}')

    print('\n--- Últimos 5 registros por módulo CUENTAS y EMPRESAS ---')
    for mod in ['CUENTAS', 'EMPRESAS']:
        regs = db.query(RegistroAuditoria).filter(RegistroAuditoria.modulo==mod).order_by(RegistroAuditoria.fecha_hora.desc()).limit(5).all()
        print(f'\nModulo {mod} - encontrados: {len(regs)}')
        for r in regs:
            print(f'  ID:{r.id} Acc:{r.accion} Desc:{r.descripcion} User:{r.usuario_nombre} Fecha:{r.fecha_hora} VA:{r.valores_anteriores} VN:{r.valores_nuevos}')

finally:
    db.close()
