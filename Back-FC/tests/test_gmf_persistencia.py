#!/usr/bin/env python3
"""
Prueba manual/integración para verificar la persistencia de GMF como transacción.
- Usa la configuración GMF efectiva por fecha/cuenta (si no existe, crea una básica).
- Ajusta componentes (ID 1,2,3 por defecto) con signos ya aplicados.
- Ejecuta recálculo directo y verifica la transacción GMF.
"""
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys
import json

# Asegurar importación del paquete app
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.database import get_db
from app.services.dependencias_flujo_caja_service import DependenciasFlujoCajaService
from app.models.transacciones_flujo_caja import TransaccionFlujoCaja, AreaTransaccion
from app.models.conceptos_flujo_caja import ConceptoFlujoCaja
from app.models.gmf_config import GMFConfig
from app.models.cuentas_bancarias import CuentaBancaria


def _ensure_gmf_config(db, cuenta_id: int, conceptos_ids):
    cfg = db.query(GMFConfig).filter(GMFConfig.cuenta_bancaria_id == cuenta_id, GMFConfig.activo == True).order_by(GMFConfig.fecha_creacion.desc()).first()
    if cfg:
        return cfg
    cfg = GMFConfig(
        cuenta_bancaria_id=cuenta_id,
        conceptos_seleccionados=json.dumps(conceptos_ids),
        activo=True,
        fecha_creacion=datetime.now(),
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def probar_gmf_persistencia():
    try:
        db = next(get_db())
        service = DependenciasFlujoCajaService(db)

        # Seleccionar una cuenta existente
        cuenta = db.query(CuentaBancaria).first()
        if not cuenta:
            print("❌ No hay cuentas bancarias en la BD de prueba")
            return

        fecha_prueba = date.today()
        print(f"🧪 Probando GMF en cuenta {cuenta.id} para {fecha_prueba}")

        # Asegurar concepto GMF existe
        concepto_gmf = db.query(ConceptoFlujoCaja).filter(ConceptoFlujoCaja.nombre == 'GMF').first()
        if not concepto_gmf:
            print("❌ El concepto 'GMF' no existe; por favor créalo en catálogo de conceptos")
            return

        # Configuración base: usar 1,2,3 si existen
        conceptos_base = [1, 2, 3]
        _ensure_gmf_config(db, cuenta.id, conceptos_base)

        # Sembrar/ajustar componentes (signos ya aplicados):
        # ID1 = 1, ID2 = -2, ID3 = 3  → suma = 1 - 2 + 3 = 2 → GMF = 2*4/1000 = 0.008
        componentes = {
            1: Decimal('1'),
            2: Decimal('-2'),
            3: Decimal('3'),
        }
        for cid, monto in componentes.items():
            t = db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_prueba,
                TransaccionFlujoCaja.concepto_id == cid,
                TransaccionFlujoCaja.cuenta_id == cuenta.id,
                TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
            ).first()
            if t:
                t.monto = monto
                t.descripcion = 'Test GMF componentes'
            else:
                t = TransaccionFlujoCaja(
                    fecha=fecha_prueba,
                    concepto_id=cid,
                    cuenta_id=cuenta.id,
                    monto=monto,
                    descripcion='Test GMF componentes',
                    usuario_id=1,
                    area=AreaTransaccion.tesoreria,
                    compania_id=1,
                )
                db.add(t)
        db.commit()

        # Ejecutar recálculo directo GMF
        result = service.recalcular_gmf(
            fecha=fecha_prueba,
            cuenta_id=cuenta.id,
            usuario_id=1,
            compania_id=1,
        )
        db.commit()
        print(f"🔁 Resultado recálculo GMF: {result}")

        # Verificar transacción GMF
        tg = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.fecha == fecha_prueba,
            TransaccionFlujoCaja.concepto_id == concepto_gmf.id,
            TransaccionFlujoCaja.cuenta_id == cuenta.id,
            TransaccionFlujoCaja.area == AreaTransaccion.tesoreria,
        ).first()
        if not tg:
            print("❌ No se encontró transacción GMF persistida")
            return

        esperado = (sum(componentes.values()) * Decimal('4')) / Decimal('1000')
        esperado_2d = esperado.quantize(Decimal('0.01'))
        print(f"✅ GMF persistido: {tg.monto} (esperado {esperado} → {esperado_2d} en 2 decimales)")
        assert tg.monto == esperado_2d
        print("🎉 Prueba de persistencia GMF OK")

    except Exception as e:
        print(f"❌ Error en prueba GMF: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    probar_gmf_persistencia()
