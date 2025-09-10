"""
Script para agregar el campo formula_dependencia al modelo ConceptoFlujoCaja.
Esto permitirá fórmulas complejas como "SUMA(1,2,3)" para múltiples dependencias.
"""

import sys
import os

# Agregar el directorio raíz del backend al path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_root)

from sqlalchemy import text
from app.core.database import engine, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def agregar_campo_formula_dependencia():
    """
    Agrega el campo formula_dependencia a la tabla conceptos_flujo_caja.
    """
    try:
        with engine.connect() as connection:
            # Verificar si la columna ya existe
            result = connection.execute(text("""
                SELECT COUNT(*) as existe
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'conceptos_flujo_caja' 
                AND COLUMN_NAME = 'formula_dependencia'
            """))
            
            existe = result.fetchone()[0]
            
            if existe == 0:
                # Agregar la columna
                connection.execute(text("""
                    ALTER TABLE conceptos_flujo_caja 
                    ADD COLUMN formula_dependencia VARCHAR(255) NULL 
                    COMMENT 'Fórmulas complejas como SUMA(1,2,3) para múltiples dependencias'
                """))
                
                connection.commit()
                logger.info("✅ Campo formula_dependencia agregado exitosamente")
                
                # Configurar el SALDO NETO INICIAL PAGADURIA
                configurar_saldo_neto_inicial()
                
            else:
                logger.info("ℹ️ El campo formula_dependencia ya existe")
                
    except Exception as e:
        logger.error(f"❌ Error agregando campo formula_dependencia: {str(e)}")
        raise

def configurar_saldo_neto_inicial():
    """
    Configura la fórmula para SALDO NETO INICIAL PAGADURIA.
    """
    try:
        db = SessionLocal()
        
        with engine.connect() as connection:
            # Buscar los IDs de los conceptos necesarios
            result = connection.execute(text("""
                SELECT id, nombre 
                FROM conceptos_flujo_caja 
                WHERE nombre IN (
                    'SALDO INICIAL',
                    'CONSUMO', 
                    'VENTANILLA',
                    'SALDO NETO INICIAL PAGADURIA'
                )
                AND activo = 1
            """))
            
            conceptos = {row[1]: row[0] for row in result.fetchall()}
            
            # Verificar que tenemos todos los conceptos
            required_concepts = ['SALDO INICIAL', 'CONSUMO', 'VENTANILLA', 'SALDO NETO INICIAL PAGADURIA']
            missing_concepts = [c for c in required_concepts if c not in conceptos]
            
            if missing_concepts:
                logger.warning(f"⚠️ Conceptos faltantes: {missing_concepts}")
                return
            
            # Crear la fórmula
            saldo_inicial_id = conceptos['SALDO INICIAL']
            consumo_id = conceptos['CONSUMO']
            ventanilla_id = conceptos['VENTANILLA']
            saldo_neto_id = conceptos['SALDO NETO INICIAL PAGADURIA']
            
            formula = f"SUMA({saldo_inicial_id},{consumo_id},{ventanilla_id})"
            
            # Actualizar el concepto SALDO NETO
            connection.execute(text("""
                UPDATE conceptos_flujo_caja 
                SET formula_dependencia = :formula,
                    tipo_dependencia = 'suma'
                WHERE id = :saldo_neto_id
            """), {
                'formula': formula,
                'saldo_neto_id': saldo_neto_id
            })
            
            connection.commit()
            
            logger.info(f"✅ SALDO NETO INICIAL PAGADURIA configurado con fórmula: {formula}")
            logger.info(f"📊 IDs utilizados:")
            logger.info(f"   - SALDO INICIAL: {saldo_inicial_id}")
            logger.info(f"   - CONSUMO: {consumo_id}")
            logger.info(f"   - VENTANILLA: {ventanilla_id}")
            logger.info(f"   - SALDO NETO: {saldo_neto_id}")
            
    except Exception as e:
        logger.error(f"❌ Error configurando SALDO NETO: {str(e)}")

def verificar_configuracion():
    """
    Verifica que la configuración se aplicó correctamente.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT 
                    id,
                    nombre,
                    formula_dependencia,
                    tipo_dependencia
                FROM conceptos_flujo_caja 
                WHERE formula_dependencia IS NOT NULL
                   OR tipo_dependencia IS NOT NULL
                ORDER BY nombre
            """))
            
            logger.info("🔍 Conceptos con dependencias configuradas:")
            for row in result.fetchall():
                logger.info(f"   ID: {row[0]} | {row[1]}")
                logger.info(f"      Fórmula: {row[2] or 'N/A'}")
                logger.info(f"      Tipo: {row[3] or 'N/A'}")
                logger.info("   ---")
                
    except Exception as e:
        logger.error(f"❌ Error verificando configuración: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando migración de formula_dependencia...")
    
    agregar_campo_formula_dependencia()
    verificar_configuracion()
    
    logger.info("✅ Migración completada")
