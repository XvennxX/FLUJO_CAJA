#!/usr/bin/env python3
"""
Script para agregar campos faltantes a las tablas de flujo de caja
Maneja errores de columnas que ya existen
"""

import mysql.connector
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def ejecutar_alter_seguro(cursor, sql, descripcion):
    """Ejecuta ALTER TABLE de forma segura, ignorando si ya existe"""
    try:
        cursor.execute(sql)
        print(f"   ✅ {descripcion}")
        return True
    except mysql.connector.Error as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e):
            print(f"   ⚠️ {descripcion} (ya existe)")
            return True
        else:
            print(f"   ❌ {descripcion}: {e}")
            return False

def main():
    print("🔧 AGREGANDO CAMPOS FALTANTES A TABLAS FLUJO DE CAJA")
    print("=" * 60)
    
    settings = get_settings()
    
    try:
        connection = mysql.connector.connect(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            autocommit=True
        )
        
        cursor = connection.cursor()
        print(f"✅ Conectado a la base de datos: {settings.db_name}")
        print()
        
        # Lista de campos a agregar a conceptos_flujo_caja
        conceptos_fields = [
            ("ADD COLUMN area ENUM('tesoreria','pagaduria','ambas') NOT NULL DEFAULT 'ambas'", "Campo 'area'"),
            ("ADD COLUMN orden_display INT DEFAULT 0", "Campo 'orden_display'"),
            ("ADD COLUMN activo BOOLEAN DEFAULT TRUE", "Campo 'activo'"),
            ("ADD COLUMN depende_de_concepto_id INT NULL", "Campo 'depende_de_concepto_id'"),
            ("ADD COLUMN tipo_dependencia ENUM('copia','suma','resta') NULL", "Campo 'tipo_dependencia'"),
            ("ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "Campo 'created_at'"),
            ("ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "Campo 'updated_at'")
        ]
        
        print("📋 CONCEPTOS_FLUJO_CAJA:")
        for alter_sql, descripcion in conceptos_fields:
            sql = f"ALTER TABLE conceptos_flujo_caja {alter_sql}"
            ejecutar_alter_seguro(cursor, sql, descripcion)
        
        print()
        
        # Lista de campos a agregar a transacciones_flujo_caja
        transacciones_fields = [
            ("ADD COLUMN area ENUM('tesoreria','pagaduria') NOT NULL DEFAULT 'tesoreria'", "Campo 'area'"),
            ("ADD COLUMN compania_id INT NULL", "Campo 'compania_id'"),
            ("ADD COLUMN auditoria JSON NULL", "Campo 'auditoria'"),
            ("ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "Campo 'created_at'"),
            ("ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "Campo 'updated_at'")
        ]
        
        print("📋 TRANSACCIONES_FLUJO_CAJA:")
        for alter_sql, descripcion in transacciones_fields:
            sql = f"ALTER TABLE transacciones_flujo_caja {alter_sql}"
            ejecutar_alter_seguro(cursor, sql, descripcion)
        
        print()
        print("🔗 AGREGANDO FOREIGN KEYS E ÍNDICES:")
        
        # Foreign Keys
        fk_sqls = [
            ("ALTER TABLE conceptos_flujo_caja ADD CONSTRAINT fk_concepto_dependencia FOREIGN KEY (depende_de_concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE SET NULL", "FK concepto dependencia"),
            ("ALTER TABLE transacciones_flujo_caja ADD CONSTRAINT fk_transaccion_concepto FOREIGN KEY (concepto_id) REFERENCES conceptos_flujo_caja(id) ON DELETE CASCADE", "FK transacción concepto")
        ]
        
        for sql, descripcion in fk_sqls:
            ejecutar_alter_seguro(cursor, sql, descripcion)
        
        # Índices
        index_sqls = [
            ("CREATE INDEX idx_conceptos_area ON conceptos_flujo_caja(area)", "Índice conceptos.area"),
            ("CREATE INDEX idx_conceptos_activo ON conceptos_flujo_caja(activo)", "Índice conceptos.activo"),
            ("CREATE INDEX idx_conceptos_orden ON conceptos_flujo_caja(orden_display)", "Índice conceptos.orden"),
            ("CREATE INDEX idx_transacciones_fecha ON transacciones_flujo_caja(fecha)", "Índice transacciones.fecha"),
            ("CREATE INDEX idx_transacciones_area ON transacciones_flujo_caja(area)", "Índice transacciones.area"),
            ("CREATE INDEX idx_transacciones_concepto ON transacciones_flujo_caja(concepto_id)", "Índice transacciones.concepto")
        ]
        
        for sql, descripcion in index_sqls:
            ejecutar_alter_seguro(cursor, sql, descripcion)
        
        print()
        print("🎉 MIGRACIÓN COMPLETADA")
        print("=" * 60)
        
        # Verificar estructura final
        print("📊 VERIFICANDO ESTRUCTURA FINAL:")
        cursor.execute("SHOW COLUMNS FROM conceptos_flujo_caja")
        conceptos_columns = [row[0] for row in cursor.fetchall()]
        print(f"   CONCEPTOS: {len(conceptos_columns)} columnas")
        
        cursor.execute("SHOW COLUMNS FROM transacciones_flujo_caja")
        transacciones_columns = [row[0] for row in cursor.fetchall()]
        print(f"   TRANSACCIONES: {len(transacciones_columns)} columnas")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
