"""
Script para obtener y registrar la TRM usando la fecha oficial de vigencia (vigenciadesde)
"""

import logging
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict

import requests
import urllib3

# Asegurar que el paquete 'app' sea importable al ejecutar el script directamente
CURRENT_FILE = os.path.abspath(__file__)
BACK_FC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
if BACK_FC_ROOT not in sys.path:
    sys.path.append(BACK_FC_ROOT)

from app.core.database import SessionLocal
from app.models.trm import TRM
from app.models.dias_festivos import DiaFestivo

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class TRMScraper:
    def __init__(self) -> None:
        # Desactivar advertencias SSL (en algunos entornos)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.urls = {
            "datos_abiertos": "https://www.datos.gov.co/resource/32sa-8pi3.json",
            "banrep_api": "https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario",
        }

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "es-CO,es;q=0.9",
            }
        )
        self.session.verify = False

    # ----------------------
    # Fuentes de información
    # ----------------------
    def get_trm_from_datos_abiertos(self, fecha: Optional[date] = None) -> Optional[Dict[str, object]]:
        if fecha is None:
            fecha = date.today()
        fecha_str = fecha.strftime("%Y-%m-%d")

        params = {
            "$select": "valor, vigenciadesde",
            "$where": f"vigenciadesde between '{fecha_str}T00:00:00.000' and '{fecha_str}T23:59:59.999'",
            "$order": "vigenciadesde desc",
            "$limit": 1,
        }

        logger.info(f"Consultando Datos Abiertos (vigenciadesde={fecha_str})…")
        try:
            r = self.session.get(self.urls["datos_abiertos"], params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"Error consultando Datos Abiertos: {e}")
            return None

        if data and isinstance(data, list) and len(data) > 0:
            raw_valor = data[0].get("valor")
            raw_vig = data[0].get("vigenciadesde")
            if raw_valor is None or raw_vig is None:
                return None
            try:
                valor = Decimal(str(raw_valor))
            except Exception:
                valor = Decimal(str(raw_valor).replace(",", ""))
            vigenciadesde = datetime.strptime(str(raw_vig)[:10], "%Y-%m-%d").date()
            return {"valor": valor, "vigenciadesde": vigenciadesde}

        return None

    def get_trm_from_banrep(self, fecha: Optional[date] = None) -> Optional[Decimal]:
        if fecha is None:
            fecha = date.today()
        fecha_str = fecha.strftime("%Y-%m-%d")

        params = {"anio": fecha.year, "mes": fecha.month, "dia": fecha.day}
        logger.info(f"Consultando BanRep (fecha={fecha_str})…")
        try:
            r = self.session.get(self.urls["banrep_api"], params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"Error consultando BanRep: {e}")
            return None

        if isinstance(data, dict) and "data" in data:
            for item in data["data"]:
                f = str(item.get("fecha", ""))
                if f.startswith(fecha_str):
                    raw_valor = item.get("valor")
                    if raw_valor is None:
                        continue
                    try:
                        return Decimal(str(raw_valor))
                    except Exception:
                        return Decimal(str(raw_valor).replace(",", ""))
        return None

    def get_current_trm(self, fecha: Optional[date] = None) -> Optional[Dict[str, object]]:
        # Preferir Datos Abiertos (trae vigenciadesde)
        da = self.get_trm_from_datos_abiertos(fecha)
        if da:
            return da
        # Fallback BanRep: usar fecha solicitada como vigenciadesde
        br = self.get_trm_from_banrep(fecha)
        if br:
            return {"valor": br, "vigenciadesde": (fecha or date.today())}
        return None

    # ----------------------
    # Persistencia en BD
    # ----------------------
    def save_trm_to_database(self, fecha: date, valor: Decimal) -> bool:
        db = SessionLocal()
        try:
            existing = db.query(TRM).filter(TRM.fecha == fecha).first()
            if existing:
                existing.valor = valor
            else:
                db.add(TRM(fecha=fecha, valor=valor))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error guardando TRM en BD: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def update_daily_trm(self, fecha: Optional[date] = None) -> bool:
        if fecha is None:
            fecha = date.today()
        # Saltar fines de semana y festivos (TRM se publica días hábiles y rige para el día siguiente)
        if fecha.isoweekday() in (6, 7):
            logger.info(f"Saltando fin de semana {fecha}")
            return False
        db = SessionLocal()
        try:
            if DiaFestivo.es_festivo(fecha, db):
                logger.info(f"Saltando festivo {fecha}")
                return False
        finally:
            db.close()

        trm = self.get_current_trm(fecha)
        if trm and "vigenciadesde" in trm and "valor" in trm:
            return self.save_trm_to_database(trm["vigenciadesde"], trm["valor"])  # type: ignore[index]
        logger.error(f"No se pudo obtener TRM para {fecha}")
        return False


def main() -> int:
    scraper = TRMScraper()
    ok = scraper.update_daily_trm()
    logger.info("Proceso completado" if ok else "Proceso falló")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
