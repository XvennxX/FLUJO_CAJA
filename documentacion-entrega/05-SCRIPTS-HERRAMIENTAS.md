# SCRIPTS Y HERRAMIENTAS - SISTEMA DE FLUJO DE CAJA

## INFORMACIÓN GENERAL

**Proyecto**: Sistema de Flujo de Caja - Bolívar  
**Lenguaje**: Python 3.9+  
**Fecha de Documentación**: 18 de Diciembre de 2025  

---

## 📁 ESTRUCTURA DE SCRIPTS

### Organización de Directorios

```
Back-FC/scripts/
├── setup/                  # Configuración inicial del sistema
├── maintenance/           # Scripts de mantenimiento y reparación
├── migrations/            # Migraciones de base de datos
├── trm/                   # Sistema TRM automático
├── utils/                 # Utilidades generales
├── debug/                 # Scripts de depuración
├── tests/                 # Scripts de pruebas
├── dev/                   # Utilidades de desarrollo
├── archive/               # Scripts obsoletos (respaldo)
└── [scripts raíz]         # Scripts principales

tools/
├── debug/                 # Herramientas de análisis
├── setup/                 # Configuración del proyecto
├── maintenance/           # Mantenimiento general
└── [scripts raíz]         # Utilidades principales
```

---

## 🚀 SCRIPTS DE SETUP (CONFIGURACIÓN INICIAL)

### Ubicación: `Back-FC/scripts/setup/`

### `init_roles_permisos.py`

**Propósito**: Inicializar el sistema RBAC completo con roles y permisos predefinidos.

**Código fuente**:

```python
"""
Script para inicializar roles y permisos del sistema
Ejecutar: python -m scripts.setup.init_roles_permisos
"""
import sys
import os
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
        
        # Módulo: Compañías
        {"codigo": "companias.ver", "nombre": "Ver compañías", "modulo": "companias", "descripcion": "Permite ver compañías"},
        {"codigo": "companias.crear", "nombre": "Crear compañías", "modulo": "companias", "descripcion": "Permite crear nuevas compañías"},
        {"codigo": "companias.editar", "nombre": "Editar compañías", "modulo": "companias", "descripcion": "Permite editar compañías"},
        {"codigo": "companias.eliminar", "nombre": "Eliminar compañías", "modulo": "companias", "descripcion": "Permite eliminar compañías"},
        
        # Módulo: Reportes
        {"codigo": "reportes.ver", "nombre": "Ver reportes", "modulo": "reportes", "descripcion": "Permite ver reportes de flujo de caja"},
        {"codigo": "reportes.exportar", "nombre": "Exportar reportes", "modulo": "reportes", "descripcion": "Permite exportar reportes a Excel/PDF"},
        
        # Módulo: Auditoría
        {"codigo": "auditoria.ver", "nombre": "Ver auditoría", "modulo": "auditoria", "descripcion": "Permite ver registros de auditoría"},
        
        # Módulo: Configuración
        {"codigo": "configuracion.ver", "nombre": "Ver configuración", "modulo": "configuracion", "descripcion": "Permite ver configuración del sistema"},
        {"codigo": "configuracion.editar", "nombre": "Editar configuración", "modulo": "configuracion", "descripcion": "Permite editar configuración del sistema"},
        
        # Módulo: TRM
        {"codigo": "trm.ver", "nombre": "Ver TRM", "modulo": "trm", "descripcion": "Permite ver tasas TRM"},
        {"codigo": "trm.editar", "nombre": "Editar TRM", "modulo": "trm", "descripcion": "Permite editar tasas TRM manualmente"},
    ]
    
    permisos_creados = []
    for p_data in permisos_data:
        # Verificar si ya existe
        existente = db.query(Permiso).filter(Permiso.codigo == p_data["codigo"]).first()
        if not existente:
            permiso = Permiso(**p_data)
            db.add(permiso)
            permisos_creados.append(permiso)
            print(f"✅ Permiso creado: {p_data['codigo']}")
        else:
            permisos_creados.append(existente)
            print(f"⚠️ Permiso ya existe: {p_data['codigo']}")
    
    db.commit()
    return permisos_creados


def crear_roles_sistema(db, permisos):
    """Crear roles predefinidos del sistema"""
    
    # Agrupar permisos por código
    permisos_dict = {p.codigo: p for p in permisos}
    
    roles_data = [
        {
            "nombre": "Administrador",
            "codigo": "ADMIN",
            "descripcion": "Acceso total al sistema",
            "es_sistema": True,
            "permisos": list(permisos_dict.keys())  # Todos los permisos
        },
        {
            "nombre": "Tesorería",
            "codigo": "TESORERIA",
            "descripcion": "Gestión de tesorería y flujo de caja",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear", "transacciones.editar",
                "conceptos.ver", "cuentas.ver", "companias.ver",
                "reportes.ver", "reportes.exportar", "trm.ver"
            ]
        },
        {
            "nombre": "Pagaduría",
            "codigo": "PAGADURIA",
            "descripcion": "Gestión de pagaduría y nómina",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear", "transacciones.editar",
                "conceptos.ver", "cuentas.ver", "companias.ver",
                "reportes.ver", "reportes.exportar", "trm.ver"
            ]
        },
        {
            "nombre": "Mesa de Dinero",
            "codigo": "MESA_DINERO",
            "descripcion": "Operaciones de mesa de dinero",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "transacciones.crear",
                "conceptos.ver", "cuentas.ver", "companias.ver",
                "reportes.ver", "trm.ver"
            ]
        },
        {
            "nombre": "Consulta",
            "codigo": "CONSULTA",
            "descripcion": "Solo visualización de reportes",
            "es_sistema": True,
            "permisos": [
                "transacciones.ver", "conceptos.ver", "cuentas.ver",
                "companias.ver", "reportes.ver", "trm.ver"
            ]
        }
    ]
    
    for r_data in roles_data:
        existente = db.query(Rol).filter(Rol.codigo == r_data["codigo"]).first()
        if not existente:
            rol = Rol(
                nombre=r_data["nombre"],
                codigo=r_data["codigo"],
                descripcion=r_data["descripcion"],
                es_sistema=r_data["es_sistema"]
            )
            # Asignar permisos
            for codigo_permiso in r_data["permisos"]:
                if codigo_permiso in permisos_dict:
                    rol.permisos.append(permisos_dict[codigo_permiso])
            
            db.add(rol)
            db.commit()
            print(f"✅ Rol creado: {r_data['nombre']} con {len(r_data['permisos'])} permisos")
        else:
            print(f"⚠️ Rol ya existe: {r_data['nombre']}")


def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("🚀 INICIALIZANDO SISTEMA DE ROLES Y PERMISOS")
        print("=" * 60)
        
        # Crear permisos
        print("\n📋 CREANDO PERMISOS...")
        permisos = crear_permisos_sistema(db)
        
        # Crear roles
        print("\n👥 CREANDO ROLES...")
        crear_roles_sistema(db, permisos)
        
        print("\n" + "=" * 60)
        print("✅ SISTEMA RBAC INICIALIZADO CORRECTAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

**Ejecución**:
```bash
cd Back-FC
python -m scripts.setup.init_roles_permisos
```

**Resultado**: Crea 35+ permisos en 10 módulos y 5 roles predefinidos.

---

## 💱 SISTEMA TRM AUTOMÁTICO

### Ubicación: `Back-FC/scripts/trm/`

### `trm_scraper.py`

**Propósito**: Obtener TRM automáticamente desde fuentes oficiales colombianas.

**Código fuente principal**:

```python
"""
Script para obtener y registrar la TRM usando la fecha oficial de vigencia
"""
import logging
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict
import requests
import urllib3

class TRMScraper:
    def __init__(self) -> None:
        # Desactivar advertencias SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.urls = {
            "datos_abiertos": "https://www.datos.gov.co/resource/32sa-8pi3.json",
            "banrep_api": "https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario",
        }

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-CO,es;q=0.9",
        })
        self.session.verify = False

    def get_trm_from_datos_abiertos(self, fecha: Optional[date] = None) -> Optional[Dict[str, object]]:
        """
        Consultar TRM desde Datos Abiertos Colombia (fuente principal).
        
        Args:
            fecha: Fecha para consultar (por defecto hoy)
        
        Returns:
            Dict con valor y fecha de vigencia, o None si no se encuentra
        """
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
        """
        Consultar TRM desde Banco de la República (fuente secundaria/fallback).
        """
        if fecha is None:
            fecha = date.today()

        params = {"anio": fecha.year, "mes": fecha.month, "dia": fecha.day}
        logger.info(f"Consultando BanRep (fecha={fecha})…")
        try:
            r = self.session.get(self.urls["banrep_api"], params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            # Procesar respuesta BanRep
            if data and "dataSeriesValores" in data:
                for serie in data["dataSeriesValores"]:
                    if "valores" in serie:
                        for v in serie["valores"]:
                            if v.get("valor"):
                                return Decimal(str(v["valor"]))
        except Exception as e:
            logger.error(f"Error consultando BanRep: {e}")
        
        return None

    def obtener_y_guardar_trm(self, fecha: Optional[date] = None) -> bool:
        """
        Obtener TRM y guardar en la base de datos.
        
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        if fecha is None:
            fecha = date.today()
        
        # Verificar si ya existe
        db = SessionLocal()
        try:
            existente = db.query(TRM).filter(TRM.fecha == fecha).first()
            if existente:
                logger.info(f"TRM ya existe para {fecha}: {existente.valor}")
                return True
            
            # Intentar fuentes en orden
            resultado = self.get_trm_from_datos_abiertos(fecha)
            
            if not resultado:
                valor_banrep = self.get_trm_from_banrep(fecha)
                if valor_banrep:
                    resultado = {"valor": valor_banrep, "vigenciadesde": fecha}
            
            if resultado:
                nueva_trm = TRM(
                    fecha=resultado["vigenciadesde"],
                    valor=resultado["valor"]
                )
                db.add(nueva_trm)
                db.commit()
                logger.info(f"✅ TRM guardada: {fecha} = {resultado['valor']}")
                return True
            else:
                logger.error(f"❌ No se encontró TRM para {fecha}")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando TRM: {e}")
            db.rollback()
            return False
        finally:
            db.close()


def main():
    """Función principal para ejecución manual o por scheduler"""
    scraper = TRMScraper()
    exito = scraper.obtener_y_guardar_trm()
    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
```

**Fuentes de datos**:
1. **Datos Abiertos Colombia**: https://www.datos.gov.co/resource/32sa-8pi3.json
2. **Banco de la República** (fallback): API de estadísticas económicas

**Ejecución**:
```bash
cd Back-FC
python -m scripts.trm.trm_scraper
```

**Automatización**: Configurar en Windows Task Scheduler o cron para ejecución diaria a las 7:00 PM.

---

## 🗄️ SCRIPTS DE MIGRACIÓN

### Ubicación: `Back-FC/scripts/migrations/`

### `create_flujo_caja_tables.sql`

```sql
-- =========================================================
-- MIGRACIÓN: CREAR TABLAS FLUJO DE CAJA DIARIO
-- Fecha: 26 de agosto de 2025
-- =========================================================

-- 1. TABLA: conceptos_flujo_caja
CREATE TABLE conceptos_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del concepto',
    codigo VARCHAR(10) COMMENT 'Código para dashboard (I, E, vacio)',
    tipo ENUM('ingreso','egreso','neutral') NOT NULL,
    area ENUM('tesoreria','pagaduria','ambas') NOT NULL,
    orden_display INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    
    -- DEPENDENCIAS AUTOMÁTICAS
    depende_de_concepto_id INT NULL,
    tipo_dependencia ENUM('copia','suma','resta') NULL,
    factor DECIMAL(10,4) DEFAULT 1.0000,
    
    -- AUDITORÍA
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- FOREIGN KEYS
    FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL,
    
    -- ÍNDICES
    INDEX idx_area_activo (area, activo),
    INDEX idx_orden_display (orden_display),
    INDEX idx_dependencia (depende_de_concepto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. TABLA: transacciones_flujo_caja
CREATE TABLE transacciones_flujo_caja (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    concepto_id INT NOT NULL,
    cuenta_id INT NULL,
    monto DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    descripcion TEXT,
    usuario_id INT NULL,
    
    -- FOREIGN KEYS
    FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE,
    FOREIGN KEY (cuenta_id) REFERENCES cuentas_bancarias(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    -- CONSTRAINTS
    UNIQUE KEY unique_transaccion (fecha, concepto_id, cuenta_id),
    
    -- ÍNDICES
    INDEX idx_fecha (fecha),
    INDEX idx_concepto_fecha (concepto_id, fecha),
    INDEX idx_cuenta_fecha (cuenta_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### `001_agregar_sistema_rbac.sql`

```sql
-- ============================================================================
-- MIGRACIÓN: Sistema de Roles y Permisos (RBAC)
-- ============================================================================

-- 1. Crear tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    es_sistema BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Crear tabla de permisos
CREATE TABLE IF NOT EXISTS permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    modulo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_codigo (codigo),
    INDEX idx_modulo (modulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Crear tabla de relación roles-permisos
CREATE TABLE IF NOT EXISTS rol_permiso (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Agregar columna rol_id a usuarios
ALTER TABLE usuarios 
ADD COLUMN rol_id INT NULL,
ADD CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL;
```

**Ejecución de migraciones**:
```bash
cd Back-FC
mysql -u usuario -p flujo_caja < scripts/migrations/create_flujo_caja_tables.sql
mysql -u usuario -p flujo_caja < scripts/migrations/001_agregar_sistema_rbac.sql
```

---

## 🔧 SCRIPTS DE MANTENIMIENTO

### Ubicación: `Back-FC/scripts/maintenance/`

### `recalcular_saldo_final.py`

**Propósito**: Recalcular saldos finales usando fórmulas de dependencia.

```python
"""
Script para recalcular saldo final de todas las transacciones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from decimal import Decimal
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.models import TransaccionFlujoCaja, ConceptoFlujoCaja

def recalcular_saldo_final(fecha_inicio: date, fecha_fin: date):
    """
    Recalcular saldo final para un rango de fechas.
    
    Fórmula: SALDO FINAL = SALDO INICIAL + TOTAL INGRESOS - TOTAL EGRESOS
    """
    db = SessionLocal()
    try:
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            print(f"📅 Procesando fecha: {fecha_actual}")
            
            # Obtener saldo inicial del día
            saldo_inicial = db.query(TransaccionFlujoCaja)\
                .join(ConceptoFlujoCaja)\
                .filter(
                    TransaccionFlujoCaja.fecha == fecha_actual,
                    ConceptoFlujoCaja.nombre == 'SALDO DIA ANTERIOR'
                ).first()
            
            if not saldo_inicial:
                print(f"  ⚠️ Sin saldo inicial para {fecha_actual}")
                fecha_actual += timedelta(days=1)
                continue
            
            # Calcular total ingresos (código 'I')
            total_ingresos = db.query(
                func.sum(TransaccionFlujoCaja.monto)
            ).join(ConceptoFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_actual,
                ConceptoFlujoCaja.codigo == 'I'
            ).scalar() or Decimal('0.00')
            
            # Calcular total egresos (código 'E')
            total_egresos = db.query(
                func.sum(TransaccionFlujoCaja.monto)
            ).join(ConceptoFlujoCaja).filter(
                TransaccionFlujoCaja.fecha == fecha_actual,
                ConceptoFlujoCaja.codigo == 'E'
            ).scalar() or Decimal('0.00')
            
            # Calcular saldo final
            saldo_final = saldo_inicial.monto + total_ingresos - total_egresos
            
            # Actualizar o crear registro de saldo final
            concepto_saldo_final = db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.nombre == 'SALDO FINAL'
            ).first()
            
            if concepto_saldo_final:
                transaccion_final = db.query(TransaccionFlujoCaja).filter(
                    TransaccionFlujoCaja.fecha == fecha_actual,
                    TransaccionFlujoCaja.concepto_id == concepto_saldo_final.id
                ).first()
                
                if transaccion_final:
                    transaccion_final.monto = saldo_final
                    print(f"  ✅ Saldo final actualizado: {saldo_final:,.2f}")
                else:
                    nueva_transaccion = TransaccionFlujoCaja(
                        fecha=fecha_actual,
                        concepto_id=concepto_saldo_final.id,
                        monto=saldo_final,
                        descripcion="Saldo final recalculado"
                    )
                    db.add(nueva_transaccion)
                    print(f"  ✅ Saldo final creado: {saldo_final:,.2f}")
            
            fecha_actual += timedelta(days=1)
        
        db.commit()
        print("\n✅ Recálculo completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Por defecto recalcular último mes
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    print("=" * 60)
    print("🔄 RECALCULANDO SALDOS FINALES")
    print(f"   Desde: {fecha_inicio}")
    print(f"   Hasta: {fecha_fin}")
    print("=" * 60)
    
    recalcular_saldo_final(fecha_inicio, fecha_fin)
```

**Ejecución**:
```bash
cd Back-FC
python -m scripts.maintenance.recalcular_saldo_final
```

### `limpiar_registros_nulos.py`

**Propósito**: Eliminar registros con datos nulos o inválidos.

```python
"""
Script para limpiar registros nulos o inválidos de la base de datos
"""
from app.core.database import SessionLocal
from app.models import TransaccionFlujoCaja, ConceptoFlujoCaja

def limpiar_registros():
    db = SessionLocal()
    try:
        # 1. Eliminar transacciones con concepto_id nulo
        transacciones_nulas = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.concepto_id == None
        ).count()
        
        if transacciones_nulas > 0:
            db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.concepto_id == None
            ).delete()
            print(f"✅ Eliminadas {transacciones_nulas} transacciones sin concepto")
        
        # 2. Eliminar transacciones con monto 0 y sin descripción
        transacciones_vacias = db.query(TransaccionFlujoCaja).filter(
            TransaccionFlujoCaja.monto == 0,
            TransaccionFlujoCaja.descripcion == None
        ).count()
        
        if transacciones_vacias > 0:
            db.query(TransaccionFlujoCaja).filter(
                TransaccionFlujoCaja.monto == 0,
                TransaccionFlujoCaja.descripcion == None
            ).delete()
            print(f"✅ Eliminadas {transacciones_vacias} transacciones vacías")
        
        db.commit()
        print("✅ Limpieza completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    limpiar_registros()
```

---

## 🧪 SCRIPTS DE PRUEBAS

### Ubicación: `Back-FC/scripts/tests/`

### `test_trm_system.py`

**Propósito**: Verificar funcionamiento completo del sistema TRM.

```python
"""
Test completo del sistema TRM
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import date, timedelta
from scripts.trm.trm_scraper import TRMScraper
from app.core.database import SessionLocal
from app.models.trm import TRM

def test_conexion_fuentes():
    """Probar conectividad a fuentes TRM"""
    scraper = TRMScraper()
    
    print("🔗 Probando conexión a Datos Abiertos...")
    try:
        resultado = scraper.get_trm_from_datos_abiertos()
        if resultado:
            print(f"  ✅ Datos Abiertos: TRM = {resultado['valor']}")
        else:
            print("  ⚠️ Sin datos en Datos Abiertos")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n🔗 Probando conexión a BanRep...")
    try:
        resultado = scraper.get_trm_from_banrep()
        if resultado:
            print(f"  ✅ BanRep: TRM = {resultado}")
        else:
            print("  ⚠️ Sin datos en BanRep")
    except Exception as e:
        print(f"  ❌ Error: {e}")


def test_base_datos():
    """Verificar datos TRM en base de datos"""
    db = SessionLocal()
    try:
        # Contar registros
        total = db.query(TRM).count()
        print(f"\n📊 Total registros TRM: {total}")
        
        # Última TRM
        ultima = db.query(TRM).order_by(TRM.fecha.desc()).first()
        if ultima:
            print(f"📅 Última TRM: {ultima.fecha} = {ultima.valor}")
        
        # TRM de hoy
        hoy = date.today()
        trm_hoy = db.query(TRM).filter(TRM.fecha == hoy).first()
        if trm_hoy:
            print(f"✅ TRM de hoy disponible: {trm_hoy.valor}")
        else:
            print("⚠️ No hay TRM para hoy")
            
    finally:
        db.close()


def test_guardar_trm():
    """Probar guardado de TRM"""
    scraper = TRMScraper()
    
    print("\n💾 Probando guardado de TRM...")
    resultado = scraper.obtener_y_guardar_trm()
    
    if resultado:
        print("✅ TRM guardada exitosamente")
    else:
        print("❌ No se pudo guardar TRM")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST COMPLETO DEL SISTEMA TRM")
    print("=" * 60)
    
    test_conexion_fuentes()
    test_base_datos()
    test_guardar_trm()
    
    print("\n" + "=" * 60)
    print("✅ TESTS COMPLETADOS")
    print("=" * 60)
```

**Ejecución**:
```bash
cd Back-FC
python -m scripts.tests.test_trm_system
```

---

## 🛠️ HERRAMIENTAS DE DEBUG

### Ubicación: `Back-FC/scripts/debug/`

### `verificar_estado_bd.py`

**Propósito**: Verificar estado general de la base de datos.

```python
"""
Verificar estado general de la base de datos
"""
from app.core.database import SessionLocal
from app.models import (
    Usuario, Rol, ConceptoFlujoCaja, TransaccionFlujoCaja,
    CuentaBancaria, Compania, TRM
)
from sqlalchemy import func

def verificar_estado():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("📊 ESTADO DE LA BASE DE DATOS")
        print("=" * 60)
        
        # Conteo por tabla
        tablas = [
            ("Usuarios", Usuario),
            ("Roles", Rol),
            ("Conceptos", ConceptoFlujoCaja),
            ("Transacciones", TransaccionFlujoCaja),
            ("Cuentas Bancarias", CuentaBancaria),
            ("Compañías", Compania),
            ("TRM", TRM),
        ]
        
        for nombre, modelo in tablas:
            count = db.query(modelo).count()
            print(f"  {nombre}: {count} registros")
        
        # Transacciones por área
        print("\n📈 TRANSACCIONES POR ÁREA:")
        areas = db.query(
            TransaccionFlujoCaja.area,
            func.count(TransaccionFlujoCaja.id)
        ).group_by(TransaccionFlujoCaja.area).all()
        
        for area, count in areas:
            print(f"  {area.value if area else 'Sin área'}: {count}")
        
        # Usuarios activos/inactivos
        print("\n👥 USUARIOS:")
        activos = db.query(Usuario).filter(Usuario.estado == True).count()
        inactivos = db.query(Usuario).filter(Usuario.estado == False).count()
        print(f"  Activos: {activos}")
        print(f"  Inactivos: {inactivos}")
        
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    verificar_estado()
```

---

## 📋 SCRIPTS DE CONCEPTOS

### Ubicación: `Back-FC/scripts/`

### `crear_conceptos_tesoreria_completos.py`

**Propósito**: Crear todos los conceptos de flujo de caja para el área de Tesorería.

```python
"""
Crear conceptos completos de tesorería con orden y configuración
"""
from app.core.database import SessionLocal
from app.models import ConceptoFlujoCaja, AreaConcepto

CONCEPTOS_TESORERIA = [
    # Saldos iniciales
    {"nombre": "SALDO DIA ANTERIOR", "codigo": "", "area": "tesoreria", "orden_display": 1},
    
    # Ingresos
    {"nombre": "CONSUMO", "codigo": "I", "area": "tesoreria", "orden_display": 10},
    {"nombre": "VENTANILLA", "codigo": "I", "area": "tesoreria", "orden_display": 11},
    {"nombre": "PAGOS INTERBANCARIOS", "codigo": "I", "area": "tesoreria", "orden_display": 12},
    {"nombre": "TRASLADO ENTRANTE", "codigo": "I", "area": "tesoreria", "orden_display": 13},
    {"nombre": "FNG", "codigo": "I", "area": "tesoreria", "orden_display": 14},
    {"nombre": "SINIESTROS", "codigo": "I", "area": "tesoreria", "orden_display": 15},
    
    # Total ingresos (calculado)
    {"nombre": "TOTAL INGRESOS", "codigo": "", "area": "tesoreria", "orden_display": 20, 
     "formula_dependencia": "SUMA(10,11,12,13,14,15)"},
    
    # Egresos
    {"nombre": "PAGO RECLAMACIONES", "codigo": "E", "area": "tesoreria", "orden_display": 30},
    {"nombre": "PAGOS A TERCEROS", "codigo": "E", "area": "tesoreria", "orden_display": 31},
    {"nombre": "TRASLADOS SALIENTES", "codigo": "E", "area": "tesoreria", "orden_display": 32},
    {"nombre": "GMF", "codigo": "E", "area": "tesoreria", "orden_display": 33},
    
    # Total egresos (calculado)
    {"nombre": "TOTAL EGRESOS", "codigo": "", "area": "tesoreria", "orden_display": 40,
     "formula_dependencia": "SUMA(30,31,32,33)"},
    
    # Saldo final (calculado)
    {"nombre": "SALDO FINAL", "codigo": "", "area": "tesoreria", "orden_display": 50,
     "formula_dependencia": "1 + 20 - 40"},
]

def crear_conceptos():
    db = SessionLocal()
    try:
        for concepto_data in CONCEPTOS_TESORERIA:
            existente = db.query(ConceptoFlujoCaja).filter(
                ConceptoFlujoCaja.nombre == concepto_data["nombre"],
                ConceptoFlujoCaja.area == AreaConcepto[concepto_data["area"]]
            ).first()
            
            if not existente:
                concepto = ConceptoFlujoCaja(
                    nombre=concepto_data["nombre"],
                    codigo=concepto_data.get("codigo"),
                    area=AreaConcepto[concepto_data["area"]],
                    orden_display=concepto_data["orden_display"],
                    formula_dependencia=concepto_data.get("formula_dependencia"),
                    activo=True
                )
                db.add(concepto)
                print(f"✅ Creado: {concepto_data['nombre']}")
            else:
                print(f"⚠️ Ya existe: {concepto_data['nombre']}")
        
        db.commit()
        print("\n✅ Conceptos de tesorería creados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    crear_conceptos()
```

---

## 🔄 PROCEDIMIENTOS DE EJECUCIÓN

### Orden de Ejecución para Instalación Nueva

```bash
# 1. Configurar entorno virtual
cd PROYECTO
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Instalar dependencias
cd Back-FC
pip install -r requirements.txt

# 3. Crear base de datos y tablas
mysql -u root -p < scripts/migrations/create_flujo_caja_tables.sql
mysql -u root -p < scripts/migrations/001_agregar_sistema_rbac.sql

# 4. Inicializar roles y permisos
python -m scripts.setup.init_roles_permisos

# 5. Crear conceptos de flujo de caja
python scripts/crear_conceptos_tesoreria_completos.py
python scripts/crear_conceptos_pagaduria.py

# 6. Obtener TRM inicial
python -m scripts.trm.trm_scraper

# 7. Verificar estado
python -m scripts.debug.verificar_estado_bd
```

### Mantenimiento Periódico

```bash
# Diario (7:00 PM)
python -m scripts.trm.trm_scraper

# Semanal
python -m scripts.maintenance.limpiar_registros_nulos

# Mensual
python -m scripts.maintenance.recalcular_saldo_final
```

### Solución de Problemas

```bash
# Verificar estado general
python -m scripts.debug.verificar_estado_bd

# Probar sistema TRM
python -m scripts.tests.test_trm_system

# Recalcular saldos incorrectos
python -m scripts.maintenance.recalcular_saldo_final

# Limpiar datos inválidos
python -m scripts.maintenance.limpiar_registros_nulos
```

Esta documentación proporciona una guía completa de todos los scripts y herramientas disponibles en el sistema de flujo de caja, incluyendo su código fuente, propósito y procedimientos de ejecución.